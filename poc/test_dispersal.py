"""Tests for the dispersal core PoC. Run: python3 test_dispersal.py"""

import itertools
import json
import pathlib
import secrets
import unittest

import dispersal as d


class GF(unittest.TestCase):
    def test_known_values(self):
        # Classic AES-field facts, independent of our tables.
        self.assertEqual(d.gf_mul(0x53, 0xCA), 0x01)
        self.assertEqual(d.gf_inv(0x53), 0xCA)
        self.assertEqual(d.gf_mul(0x02, 0x80), 0x1B)
        self.assertEqual(d.gf_mul(0x00, 0xFF), 0x00)

    def test_field_laws_sampled(self):
        for _ in range(200):
            a, b, c = (secrets.randbelow(256) for _ in range(3))
            self.assertEqual(d.gf_mul(a, b), d.gf_mul(b, a))
            self.assertEqual(d.gf_mul(a, d.gf_mul(b, c)),
                             d.gf_mul(d.gf_mul(a, b), c))
            self.assertEqual(d.gf_mul(a, b ^ c),
                             d.gf_mul(a, b) ^ d.gf_mul(a, c))
            if a:
                self.assertEqual(d.gf_mul(a, d.gf_inv(a)), 1)


class Shamir(unittest.TestCase):
    def test_roundtrip_every_k_subset(self):
        secret = secrets.token_bytes(64)
        n, k = 4, 3
        shares = d.split(secret, n, k)
        for subset in itertools.combinations(range(1, n + 1), k):
            points = {x: shares[x - 1] for x in subset}
            self.assertEqual(d.reconstruct(points), secret)

    def test_extreme_params(self):
        secret = secrets.token_bytes(16)
        for n, k in [(1, 1), (15, 15), (15, 2), (5, 5)]:
            shares = d.split(secret, n, k)
            points = {x + 1: shares[x] for x in range(k)}
            self.assertEqual(d.reconstruct(points), secret)

    def test_below_threshold_is_garbage(self):
        secret = secrets.token_bytes(64)
        shares = d.split(secret, 4, 3)
        self.assertNotEqual(d.reconstruct({1: shares[0], 2: shares[1]}), secret)

    def test_param_validation(self):
        for n, k in [(0, 0), (3, 4), (16, 2), (4, 0)]:
            with self.assertRaises(ValueError):
                d.split(b"x", n, k)


class Floor(unittest.TestCase):
    def test_enumeration_uniform(self):
        """I-2 by brute force: k-1 shares leave every secret byte equally
        consistent, for arbitrary observed share values."""
        for y in [(0x5A, 0xC3), (0x00, 0x00), (0xFF, 0x01)]:
            counts = d.floor_demo(y=y)
            self.assertEqual(set(counts.values()), {1})


class PayloadAndTags(unittest.TestCase):
    def test_payload_roundtrip(self):
        tag = secrets.token_bytes(d.TAG_BYTES)
        share = secrets.token_bytes(d.SHARE_BYTES)
        p = d.build_payload(tag, 2, 4, 3, share)  # build_payload(tag, index, n, k, share)
        self.assertEqual(len(p), d.DELTA_BYTES)
        # parse returns (tag, index, k, n, share): k=3, n=4
        self.assertEqual(d.parse_payload(p), (tag, 2, 3, 4, share))

    def test_tags_distinct_and_deterministic(self):
        key = secrets.token_bytes(32)
        tags = {d.share_tag(key, n.to_bytes(8, "big"), i)
                for n in range(8) for i in range(1, 5)}
        self.assertEqual(len(tags), 32)  # SP-7: no equal values across shares
        self.assertEqual(d.share_tag(key, b"\0" * 8, 1),
                         d.share_tag(key, b"\0" * 8, 1))

    def test_padding_roundtrip_and_limit(self):
        for m in [b"", b"x", secrets.token_bytes(d.MAX_MESSAGE)]:
            padded = d.pad(m)
            self.assertEqual(len(padded), d.SHARE_BYTES)
            self.assertEqual(d.unpad(padded), m)
        with self.assertRaises(ValueError):
            d.pad(secrets.token_bytes(d.MAX_MESSAGE + 1))

    def test_disperse_recognize_with_loss_and_noise(self):
        key = secrets.token_bytes(32)
        other_key = secrets.token_bytes(32)
        nonce = (3).to_bytes(8, "big")
        msg = secrets.token_bytes(200)
        payloads = d.disperse(msg, key, nonce)
        payloads.pop(0)                                   # lose one share
        payloads += d.disperse(b"noise", other_key, nonce)  # someone else's
        window = [i.to_bytes(8, "big") for i in range(8)]
        self.assertEqual(d.recognize(payloads, key, window), {nonce: msg})
        self.assertEqual(
            d.recognize(payloads[:2], key, window), {})   # below k: nothing


class Vectors(unittest.TestCase):
    """Cross-implementation vectors; see vectors.json next to this file."""

    def setUp(self):
        here = pathlib.Path(__file__).resolve().parent
        self.v = json.loads((here / "vectors.json").read_text())

    def test_gf(self):
        for a, b, p in self.v["gf_mul"]:
            self.assertEqual(d.gf_mul(a, b), p)

    def test_shamir_deterministic(self):
        s = self.v["shamir"]
        shares = d.split(bytes.fromhex(s["secret"]), s["n"], s["k"],
                         coeffs=bytes.fromhex(s["coeffs"]))
        self.assertEqual([x.hex() for x in shares], s["shares"])

    def test_tags(self):
        t = self.v["tags"]
        key, nonce = bytes.fromhex(t["key"]), bytes.fromhex(t["nonce"])
        for i, expect in enumerate(t["tags"], start=1):
            self.assertEqual(d.share_tag(key, nonce, i).hex(), expect)


if __name__ == "__main__":
    unittest.main(verbosity=2)
