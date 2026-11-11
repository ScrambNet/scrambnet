"""Tests for the end-to-end AEAD layer (SP-1 belt). Run: python3 test_e2e.py"""

import json
import pathlib
import secrets
import unittest

import e2e


class AEADKnownAnswer(unittest.TestCase):
    """RFC 8439 test vectors: proves this is real ChaCha20-Poly1305, not a
    look-alike. If these pass, the construction interoperates with any
    conformant library -- the only thing that makes the PoC's AEAD credible."""

    def test_chacha20_block_rfc8439_2_3_2(self):
        key = bytes(range(32))
        nonce = bytes.fromhex("000000090000004a00000000")
        block = e2e._chacha_block(key, 1, nonce)
        self.assertEqual(block.hex(),
            "10f1e7e4d13b5915500fdd1fa32071c4"
            "c7d1f4c733c068030422aa9ac3d46c4e"
            "d2826446079faa0914c2d705d98b02a2"
            "b5129cd1de164eb9cbd083e8a2503c4e")

    def test_poly1305_rfc8439_2_5_2(self):
        key = bytes.fromhex(
            "85d6be7857556d337f4452fe42d506a8"
            "0103808afb0db2fd4abff6af4149f51b")
        msg = b"Cryptographic Forum Research Group"
        self.assertEqual(e2e._poly1305(key, msg).hex(),
                         "a8061dc1305136c6c22b8baf0c0127a9")

    def test_aead_rfc8439_2_8_2(self):
        key = bytes(range(0x80, 0xA0))
        nonce = bytes.fromhex("070000004041424344454647")
        aad = bytes.fromhex("50515253c0c1c2c3c4c5c6c7")
        pt = (b"Ladies and Gentlemen of the class of '99: If I could offer you "
              b"only one tip for the future, sunscreen would be it.")
        out = e2e.aead_encrypt(key, nonce, pt, aad)
        self.assertEqual(out[-16:].hex(), "1ae10b594f09e26a7e902ecbd0600691")
        self.assertEqual(e2e.aead_decrypt(key, nonce, out, aad), pt)


class AEADProperties(unittest.TestCase):
    def test_roundtrip_random(self):
        for _ in range(50):
            key = secrets.token_bytes(32)
            nonce = secrets.token_bytes(12)
            pt = secrets.token_bytes(secrets.randbelow(300))
            aad = secrets.token_bytes(secrets.randbelow(40))
            ct = e2e.aead_encrypt(key, nonce, pt, aad)
            self.assertEqual(e2e.aead_decrypt(key, nonce, ct, aad), pt)

    def test_tamper_fails_closed(self):
        key = secrets.token_bytes(32)
        nonce = secrets.token_bytes(12)
        pt = b"fail closed, never garbage"
        ct = bytearray(e2e.aead_encrypt(key, nonce, pt))
        for pos in (0, len(ct) // 2, len(ct) - 1):   # body and tag
            bad = bytearray(ct); bad[pos] ^= 0x01
            with self.assertRaises(ValueError):
                e2e.aead_decrypt(key, nonce, bytes(bad))

    def test_wrong_aad_fails(self):
        key = secrets.token_bytes(32)
        nonce = secrets.token_bytes(12)
        ct = e2e.aead_encrypt(key, nonce, b"msg", b"aad-A")
        with self.assertRaises(ValueError):
            e2e.aead_decrypt(key, nonce, ct, b"aad-B")


class SP1Belt(unittest.TestCase):
    def test_seal_open_roundtrip(self):
        kpair = secrets.token_bytes(32)
        for _ in range(20):
            nonce = secrets.token_bytes(8)
            pt = secrets.token_bytes(secrets.randbelow(500))
            self.assertEqual(e2e.open_(kpair, nonce, e2e.seal(kpair, nonce, pt)),
                             pt)

    def test_content_key_label_separated(self):
        """The content key must not collide with the SP-7 tag key derived from
        the same kpair: distinct HKDF labels must give distinct keys (the 1.4
        KDF-discipline direction)."""
        kpair = secrets.token_bytes(32)
        ck = e2e.content_key(kpair)                 # info = b"e2e-content"
        tag_key = e2e._hkdf_blake2s(kpair, b"tag")  # info = b"tag"
        self.assertNotEqual(ck, tag_key)
        self.assertEqual(len(ck), e2e.AEAD_KEY_BYTES)

    def test_wrong_pair_cannot_open(self):
        nonce = (1).to_bytes(8, "big")
        ct = e2e.seal(secrets.token_bytes(32), nonce, b"secret")
        with self.assertRaises(ValueError):
            e2e.open_(secrets.token_bytes(32), nonce, ct)

    def test_nonce_reuse_is_detectable_catastrophe(self):
        """Documenting, not endorsing: two plaintexts sealed under the same
        (kpair, msg_nonce) share a keystream. XOR of the two ciphertexts
        equals XOR of the two plaintexts -- the classic two-time-pad break.
        This test exists so the hazard is pinned in code: msg_nonce MUST be
        unique per message (the SP-7 / 1.3 nonce-discipline requirement)."""
        kpair = secrets.token_bytes(32)
        nonce = (99).to_bytes(8, "big")
        p1 = b"attack at dawn!!"
        p2 = b"retreat at dusk!"
        c1 = e2e.seal(kpair, nonce, p1)[:len(p1)]   # strip the 16-byte tag
        c2 = e2e.seal(kpair, nonce, p2)[:len(p2)]
        xored = bytes(a ^ b for a, b in zip(c1, c2))
        self.assertEqual(xored, bytes(a ^ b for a, b in zip(p1, p2)))


class Vectors(unittest.TestCase):
    """The e2e block of vectors.json: a second implementation that reproduces
    these interoperates on the content path (SP-1a / 3.2 vector-lock)."""

    def setUp(self):
        here = pathlib.Path(__file__).resolve().parent
        self.v = json.loads((here / "vectors.json").read_text())["e2e"]

    def test_content_key_vector(self):
        kpair = bytes.fromhex(self.v["kpair"])
        self.assertEqual(e2e.content_key(kpair).hex(), self.v["content_key"])

    def test_seal_vector(self):
        kpair = bytes.fromhex(self.v["kpair"])
        nonce = bytes.fromhex(self.v["msg_nonce"])
        pt = bytes.fromhex(self.v["plaintext"])
        self.assertEqual(e2e.seal(kpair, nonce, pt).hex(), self.v["ciphertext"])

    def test_open_vector(self):
        kpair = bytes.fromhex(self.v["kpair"])
        nonce = bytes.fromhex(self.v["msg_nonce"])
        ct = bytes.fromhex(self.v["ciphertext"])
        self.assertEqual(e2e.open_(kpair, nonce, ct).hex(), self.v["plaintext"])


class Limits(unittest.TestCase):
    def test_max_plaintext_constant(self):
        # dispersal's share-payload budget minus the AEAD tag (SP-8 fragments
        # above this). Kept in sync with dispersal.MAX_MESSAGE by this test.
        import dispersal as d
        self.assertEqual(e2e.MAX_PLAINTEXT, d.MAX_MESSAGE - e2e.TAG_BYTES)


if __name__ == "__main__":
    unittest.main(verbosity=2)
