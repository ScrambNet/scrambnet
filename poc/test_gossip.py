"""Tests for gossip-record canonical CBOR + Ed25519 (Part 2 §2A, GR-21..GR-30).
Run: python3 test_gossip.py

These make GR-30 mechanically checkable: the encoder reproduces each positive
vector's canonical bytes and signing input, every positive verifies, and every
negative vector is rejected -- the mixed-order ones *specifically* by the GR-28
[L]P subgroup test, which is what separates this strict profile from a permissive
(ZIP-215) one.
"""

import json
import pathlib
import unittest

import gossip as g

VJSON = pathlib.Path(__file__).resolve().parent / "vectors.json"


def _unjson(v):
    if isinstance(v, dict) and set(v) == {"b"}:
        return bytes.fromhex(v["b"])
    if isinstance(v, list):
        return [_unjson(x) for x in v]
    return v


class CanonicalCBOR(unittest.TestCase):
    """GR-21/GR-21a/GR-22/GR-23: the canonical encoding is total."""

    def test_shortest_form_heads(self):
        self.assertEqual(g.encode(10), bytes([10]))
        self.assertEqual(g.encode(24), bytes([0x18, 24]))
        self.assertEqual(g.encode(256), bytes([0x19, 0x01, 0x00]))
        self.assertEqual(g.encode(2 ** 32), bytes([0x1B]) + (2 ** 32).to_bytes(8, "big"))

    def test_roundtrip_including_boundaries_and_unknowns(self):
        for v in [0, 23, 24, 255, 256, 65535, 65536, 2 ** 32 - 1, 2 ** 32,
                  b"", b"\x00" * 32, [], [[0, b"abc"]], {},
                  {0: 1, 6: 2, 9: b"zz", 2: b"a" * 32}]:
            self.assertEqual(g.decode_canonical(g.encode(v)), v)
            self.assertTrue(g.is_canonical(g.encode(v)))

    def test_key_order_is_total(self):
        # bytewise order of shortest-form uint keys == numeric order (GR-22).
        import random
        keys = random.sample(range(0, 2 ** 20), 40)
        enc = {k: b"\x00" for k in keys}
        canon = g.encode(enc)
        # decode preserves ascending order; re-encode is identical.
        self.assertTrue(g.is_canonical(canon))

    def test_rejects_non_canonical(self):
        for buf in [bytes([0xA1, 0x00, 0x18, 0x01]),   # non-shortest value
                    bytes([0x9F, 0x00, 0xFF]),          # indefinite array
                    bytes([0xA1, 0x00, 0xF9, 0, 0]),    # float
                    bytes([0x61, 0x61]),                # text string
                    bytes([0xA2, 0x04, 0, 0x04, 0]),    # duplicate key
                    bytes([0xA2, 0x01, 0, 0x00, 0])]:   # reordered keys
            self.assertFalse(g.is_canonical(buf))


class Ed25519Profile(unittest.TestCase):
    """GR-25..GR-28. The signatures are cross-checked against an independent
    library when one is importable (not a PoC dependency; a test-only oracle)."""

    def test_sign_verify_roundtrip(self):
        seed = bytes([7]) * 32
        A = g.secret_to_public(seed)
        for n in (0, 1, 31, 64, 137):
            msg = bytes(range(n % 256)) * 1
            msg = msg[:n] if n else b""
            sig = g.sign(seed, msg)
            self.assertTrue(g.verify(A, sig, msg))
            bad = bytearray(sig)
            bad[0] ^= 1
            self.assertFalse(g.verify(A, bytes(bad), msg))

    def test_cross_validate_against_reference_if_available(self):
        try:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
            from cryptography.hazmat.primitives import serialization
        except Exception:
            self.skipTest("no reference Ed25519 library available")
        import secrets
        for _ in range(25):
            seed = secrets.token_bytes(32)
            msg = secrets.token_bytes(secrets.randbelow(100))
            priv = Ed25519PrivateKey.from_private_bytes(seed)
            pub = priv.public_key().public_bytes(
                serialization.Encoding.Raw, serialization.PublicFormat.Raw)
            self.assertEqual(g.secret_to_public(seed), pub)
            self.assertEqual(g.sign(seed, msg), priv.sign(msg))
            self.assertTrue(g.verify(pub, priv.sign(msg), msg))

    def test_reject_non_canonical_S(self):
        seed = bytes([5]) * 32
        A = g.secret_to_public(seed)
        msg = b"x"
        sig = bytearray(g.sign(seed, msg))
        S = int.from_bytes(sig[32:], "little")
        sig[32:] = (S + g._L).to_bytes(32, "little")
        self.assertFalse(g.verify(A, bytes(sig), msg))  # GR-26

    def test_reject_small_and_mixed_order_points(self):
        # GR-28: both small-order and mixed-order A/R are rejected by [L]P-test.
        small = [
            "0100000000000000000000000000000000000000000000000000000000000000",
            "26e8958fc2b227b045c3f489f2ef98f0d5dfac05d3c63339b13802886d53fc05",
            "ecffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff7f",
        ]
        for h in small:
            pt = g._decode_point(bytes.fromhex(h))
            if pt is not None:
                self.assertFalse(g._in_prime_order_subgroup(pt))
        # mixed-order = prime-order point + order-2 torsion; a blacklist misses it.
        Aprime = g._decode_point(g.secret_to_public(bytes([7]) * 32))
        T2 = (0, g._p - 1, 1, 0)
        mixed = g._edwards_add(Aprime, T2)
        self.assertTrue(g._in_prime_order_subgroup(Aprime))
        self.assertFalse(g._in_prime_order_subgroup(mixed))


class RecordVectors(unittest.TestCase):
    """GR-30: conformance is defined by vectors.json['records']."""

    @classmethod
    def setUpClass(cls):
        cls.r = json.loads(VJSON.read_text())["records"]

    def test_positive_canon_and_signing_input_reproduced(self):
        fields = {int(k): _unjson(v)
                  for k, v in self.r["positive"]["fields_hex"].items()}
        self.assertEqual(g.signing_input(fields).hex(),
                         self.r["positive"]["signing_input"])
        self.assertEqual(g.sign_record(bytes.fromhex(self.r["sk"]), fields).hex(),
                         self.r["positive"]["canonical_cbor"])

    def test_positives_verify(self):
        for key in ("positive", "positive_unknown_key"):
            rec = bytes.fromhex(self.r[key]["canonical_cbor"])
            self.assertIsNotNone(g.verify_record(rec),
                                 "%s should verify" % key)

    def test_negatives_all_rejected(self):
        for neg in self.r["negative"]:
            rec = bytes.fromhex(neg["bytes"])
            self.assertIsNone(g.verify_record(rec),
                              "negative %s (%s) must be rejected"
                              % (neg["name"], neg["violates"]))

    def test_mixed_order_negatives_fail_specifically_at_gr28(self):
        # The load-bearing property: these pass canonical CBOR + canonical point
        # encoding and are rejected ONLY by GR-28's subgroup test, so a permissive
        # (small-order-blacklist / cofactored) implementation would wrongly accept.
        for name in ("mixed_order_A", "mixed_order_R"):
            b = bytes.fromhex(next(n["bytes"] for n in self.r["negative"]
                                   if n["name"] == name))
            self.assertTrue(g.is_canonical(b))
            fields = g.decode_canonical(b)
            self.assertTrue(g._record_shape_ok(fields))
            pt = (g._decode_point(fields[1]) if name == "mixed_order_A"
                  else g._decode_point(fields[7][:32]))
            self.assertIsNotNone(pt, "point should decode canonically (GR-27 ok)")
            self.assertFalse(g._in_prime_order_subgroup(pt), "must fail GR-28")


if __name__ == "__main__":
    unittest.main(verbosity=2)
