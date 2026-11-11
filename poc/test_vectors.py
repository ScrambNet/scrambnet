"""Cross-implementation conformance harness (roadmap 3.2). Run:
    python3 test_vectors.py

This is the "a second implementation passes every vector" check, run against the
first implementation (this PoC). It loads vectors.json and asserts that every
keyed construction reproduces byte-for-byte from the code, and -- importantly --
that no section of vectors.json is left without a conformance check, so a vector
can never be added without a test that pins it (I-1).

A second implementation in another language conforms iff it reproduces the same
outputs for every section here (except `sphinx_hop`, which is declared
pending-implementation until the onion layer exists).
"""

import json
import pathlib
import unittest

import dispersal
import e2e
import gossip
import rendezvous

VJSON = pathlib.Path(__file__).resolve().parent / "vectors.json"
VEC = json.loads(VJSON.read_text())

# Every section that carries vectors MUST be checked by a method below. A
# section named here but absent from the file, or present in the file but not
# here, fails test_every_section_is_covered -- so coverage cannot silently rot.
CHECKED_SECTIONS = {
    "gf_mul", "shamir", "tags", "e2e", "rendezvous", "records",
    "hkdf", "gf_tables", "params", "e2e_dispersal", "sphinx_hop",
}
NON_SECTION_KEYS = {"comment"}  # top-level keys that are not vector sections


def _h(s):
    return bytes.fromhex(s)


class VectorCoverage(unittest.TestCase):
    def test_every_section_is_covered(self):
        file_sections = set(VEC) - NON_SECTION_KEYS
        self.assertEqual(
            file_sections, CHECKED_SECTIONS,
            "vectors.json sections and the conformance checks have drifted: "
            "in file only=%s ; checked only=%s"
            % (file_sections - CHECKED_SECTIONS, CHECKED_SECTIONS - file_sections))


class KeyedConstructions(unittest.TestCase):
    def test_gf_mul(self):
        for a, b, r in VEC["gf_mul"]:
            self.assertEqual(dispersal.gf_mul(a, b), r)

    def test_gf_tables_pinned(self):
        g = VEC["gf_tables"]
        exp = bytes(dispersal._EXP[i] for i in range(510))
        log = bytes(dispersal._LOG[i] for i in range(256))
        import hashlib
        self.assertEqual(hashlib.blake2s(exp).hexdigest(), g["exp_blake2s"])
        self.assertEqual(hashlib.blake2s(log).hexdigest(), g["log_blake2s"])
        self.assertEqual(exp, _h(g["exp"]))
        self.assertEqual(log, _h(g["log"]))
        for a, b, r in g["mul_samples"]:
            self.assertEqual(dispersal.gf_mul(a, b), r)
        for a, inv in g["inv_samples"]:
            self.assertEqual(dispersal.gf_inv(a), inv)

    def test_shamir(self):
        s = VEC["shamir"]
        shares = dispersal.split(_h(s["secret"]), s["n"], s["k"], _h(s["coeffs"]))
        self.assertEqual([x.hex() for x in shares], s["shares"])

    def test_tags(self):
        t = VEC["tags"]
        for i, expected in enumerate(t["tags"], start=1):
            tag = dispersal.share_tag(_h(t["key"]), _h(t["nonce"]), i)
            self.assertEqual(tag.hex(), expected)

    def test_params_nibble_lock(self):
        for c in VEC["params"]["cases"]:
            self.assertEqual((c["k"] << 4) | c["n"], c["packed_byte"])
            self.assertEqual("%02x" % c["packed_byte"], c["packed_hex"])
            # and the unpack order the PoC parsers agree on
            self.assertEqual((c["packed_byte"] >> 4, c["packed_byte"] & 0x0F),
                             (c["k"], c["n"]))

    def test_hkdf(self):
        for c in VEC["hkdf"]["cases"]:
            out = e2e._hkdf_blake2s(_h(c["key"]), _h(c["info"]), c["length"])
            self.assertEqual(out.hex(), c["out"])
        # the two PoC HKDF entry points MUST agree (I-1 hazard if they diverge)
        for c in VEC["hkdf"]["cases"]:
            self.assertEqual(
                e2e._hkdf_blake2s(_h(c["key"]), _h(c["info"]), c["length"]),
                rendezvous.hkdf_blake2s(_h(c["key"]), _h(c["info"]), c["length"]))

    def test_e2e_content_path(self):
        v = VEC["e2e"]
        ct = e2e.seal(_h(v["kpair"]), _h(v["msg_nonce"]), _h(v["plaintext"]))
        self.assertEqual(ct.hex(), v["ciphertext"])
        self.assertEqual(e2e.open_(_h(v["kpair"]), _h(v["msg_nonce"]), ct),
                         _h(v["plaintext"]))

    def test_e2e_dispersal_full_path(self):
        v = VEC["e2e_dispersal"]
        ct = e2e.seal(_h(v["kpair"]), _h(v["msg_nonce"]), _h(v["plaintext"]))
        self.assertEqual(ct.hex(), v["ciphertext"])
        shares = dispersal.split(ct, v["n"], v["k"], _h(v["coeffs"]))
        self.assertEqual([s.hex() for s in shares], v["shares"])
        pts = {i: shares[i - 1] for i in v["reconstruct_from"]}
        rec = dispersal.reconstruct(pts)
        self.assertEqual(rec, ct)
        self.assertEqual(e2e.open_(_h(v["kpair"]), _h(v["msg_nonce"]), rec),
                         _h(v["plaintext"]))

    def test_rendezvous(self):
        v = VEC["rendezvous"]
        kpair = _h(v["kpair"])
        self.assertEqual(rendezvous.hkdf_blake2s(kpair, b"tag").hex(), v["k_tag"])
        for key, expected in v["box_ids"].items():
            drop_s, epoch_s = key.split("_")
            info = b"box" + bytes([int(drop_s)]) + int(epoch_s).to_bytes(8, "big")
            box_id = rendezvous.hkdf_blake2s(kpair, info, rendezvous.BOX_ID_BYTES)
            self.assertEqual(box_id.hex(), expected)

    def test_records(self):
        r = VEC["records"]
        self.assertIsNotNone(
            gossip.verify_record(_h(r["positive"]["canonical_cbor"])))
        for neg in r["negative"]:
            self.assertIsNone(gossip.verify_record(_h(neg["bytes"])),
                              "negative %s must reject" % neg["name"])

    def test_sphinx_hop_is_declared_pending(self):
        # The one honest gap: no onion layer in the toy, so no reference output.
        self.assertEqual(VEC["sphinx_hop"]["status"], "pending-implementation")
        self.assertEqual(VEC["sphinx_hop"]["labels"],
                         ["sphinx-rho", "sphinx-mu", "sphinx-delta"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
