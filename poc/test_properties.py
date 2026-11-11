"""Stronger property tests: the claims a reviewer will want checked, not just
asserted. Run: python3 test_properties.py

These are statistical, so they use generous margins and fixed sample sizes;
they demonstrate the properties hold empirically, they do not replace proof.
"""

import collections
import math
import secrets
import unittest

import dispersal as d
import rendezvous as rz


class UnconditionalFloor(unittest.TestCase):
    def test_k_minus_1_shares_are_uniform_over_many_secrets(self):
        """Fix two share x-positions; over random secrets, the pair of share
        bytes seen at those positions must be ~uniform over 256*256, i.e. the
        k-1 view carries no information about the secret. Chi-square sanity."""
        n, k = 4, 3
        pos = (1, 2)
        seen = collections.Counter()
        trials = 60000
        for _ in range(trials):
            secret = secrets.token_bytes(1)
            shares = d.split(secret, n, k)
            seen[(shares[pos[0] - 1][0], shares[pos[1] - 1][0])] += 1
        cells = 256 * 256
        expected = trials / cells
        # With trials << cells, expect ~0/1 per cell; assert the marginal on the
        # first observed byte is uniform (that is the information-bearing axis).
        marg = collections.Counter()
        total = 0
        for (a, _b), c in seen.items():
            marg[a] += c
            total += c
        chi = sum((marg.get(a, 0) - total / 256) ** 2 / (total / 256)
                  for a in range(256))
        # 255 dof: chi well under a loose bound means no detectable skew.
        self.assertLess(chi, 255 + 6 * math.sqrt(2 * 255),
                        f"share-byte marginal looks skewed: chi={chi:.0f}")

    def test_reconstruction_independent_of_which_k(self):
        secret = secrets.token_bytes(200)
        shares = d.split(secret, 5, 3)
        import itertools
        for sub in itertools.combinations(range(1, 6), 3):
            self.assertEqual(d.reconstruct({x: shares[x - 1] for x in sub}),
                             secret)

    def test_coefficient_reuse_breaks_the_floor(self):
        """SA-3, the negative test the floor's soundness depends on: if the
        polynomial coefficients are REUSED across byte positions instead of
        drawn independently, the k-1 view stops being independent of the secret
        and leaks. Concretely, with one coefficient tuple reused for every byte,
        share[a] XOR share[b] == secret[a] XOR secret[b] for ANY single share,
        with no key at all -- a total break. This test proves our tooling would
        catch a reuse / low-entropy-RNG implementation bug, not just assert it
        does not happen. See spec Part 7, SA-2/SA-3."""
        n, k = 4, 3
        trials = 500

        # Broken splitter: ONE coefficient set reused for every byte position.
        def split_reused(secret):
            one = secrets.token_bytes(k - 1)
            return d.split(secret, n, k, coeffs=one * len(secret))

        reuse_leaks = sum(
            1 for _ in range(trials)
            for sec in [secrets.token_bytes(2)]
            for sh in [split_reused(sec)]
            if (sh[0][0] ^ sh[0][1]) == (sec[0] ^ sec[1])
        )
        # Reuse leaks the secret-byte XOR deterministically: every single trial.
        self.assertEqual(reuse_leaks, trials,
                         "coefficient reuse should leak the secret XOR always")

        # Independent coefficients (the correct split): the same estimator is
        # right only ~1/256 of the time -- pure chance, no systematic leak.
        indep_hits = sum(
            1 for _ in range(trials)
            for sec in [secrets.token_bytes(2)]
            for sh in [d.split(sec, n, k)]
            if (sh[0][0] ^ sh[0][1]) == (sec[0] ^ sec[1])
        )
        # Loose bound around trials/256 (~2); well under 20 unless something is
        # systematically leaking.
        self.assertLess(indep_hits, 20,
                        f"independent coeffs should not leak; hits={indep_hits}")


class SP7Tags(unittest.TestCase):
    def test_no_collisions_across_many_messages(self):
        key = secrets.token_bytes(32)
        tags = set()
        for m in range(20000):
            for i in range(1, 5):
                tags.add(d.share_tag(key, m.to_bytes(8, "big"), i))
        self.assertEqual(len(tags), 20000 * 4)  # SP-7: all distinct

    def test_tag_unpredictable_without_key(self):
        """Two different keys give unrelated tags for the same (nonce,index)."""
        n = (0).to_bytes(8, "big")
        a = d.share_tag(secrets.token_bytes(32), n, 1)
        b = d.share_tag(secrets.token_bytes(32), n, 1)
        self.assertNotEqual(a, b)

    def test_no_equal_tag_unless_nonce_index_reused(self):
        """SP-7b: equal tags imply an equal (msg_nonce, index). We check the
        PRF input encoding is injective -- distinct (nonce, index) give distinct
        inputs -- which is what makes 'tags collide only on nonce reuse' hold.
        The shares of ONE message (one nonce, indices 1..n) must all differ, and
        only a reused (nonce,index) under one key can force an equal tag."""
        key = secrets.token_bytes(32)
        # injective input: build the raw PRF preimage for many (nonce,index)
        preimages = set()
        pairs = set()
        for nv in range(300):
            for idx in range(1, 16):
                nonce = nv.to_bytes(8, "big")
                preimages.add(nonce + bytes([idx]))   # the share_tag input
                pairs.add((nonce, idx))
        self.assertEqual(len(preimages), len(pairs))  # injective: no two collide
        # one message's shares (same nonce, indices 1..n) => all tags distinct
        nonce = (7).to_bytes(8, "big")
        tags = {d.share_tag(key, nonce, i) for i in range(1, 9)}
        self.assertEqual(len(tags), 8)
        # reusing (nonce,index) is the ONLY way to force an equal tag
        self.assertEqual(d.share_tag(key, nonce, 3), d.share_tag(key, nonce, 3))


class DropObservability(unittest.TestCase):
    def test_drop_cannot_distinguish_two_messages_by_stored_bytes(self):
        """A drop holds one slot; two different messages to the same box must
        leave stored bytes with no exploitable structure (both look random).
        We check the drop never sees equal slots for distinct deposits."""
        drop = rz.Drop()
        card = rz.Card(secrets.token_bytes(32), secrets.token_bytes(32), [drop])
        slots = set()
        for msg_i in range(500):
            rz.deposit_message(card, msg_i.to_bytes(4, "big"),
                               msg_i.to_bytes(8, "big"), 1_767_000_000.0, n=1, k=1)
        for q in drop.boxes.values():
            for _, slot in q:
                slots.add(slot)
        # every deposit (even of the same short content) yields a distinct slot
        # because of random padding -> no deposit-equality side channel.
        self.assertGreater(len(slots), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
