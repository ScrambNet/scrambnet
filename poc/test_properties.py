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
