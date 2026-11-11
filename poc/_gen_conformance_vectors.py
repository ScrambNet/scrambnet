"""Add the roadmap-3.2 conformance vectors to vectors.json: the keyed
constructions that did not yet have a stand-alone cross-implementation anchor.

Adds:
  - hkdf        : HKDF-BLAKE2s known-answer vectors (the PRK every other
                  derivation is built on -- content_key, k_tag, box_id).
  - gf_tables   : the GF(2^8) exp/log tables pinned as normative (their
                  blake2s hashes + a dense sample), so a second implementation
                  builds the same field.
  - params      : the (k,n) packed-byte nibble order, vector-locked (the two
                  PoC parsers once disagreed; a vector keeps them honest).
  - e2e_dispersal: the full content path encrypt -> split -> reconstruct ->
                  decrypt, so the composition (not only its parts) is pinned.
  - sphinx_hop  : DECLARED PENDING. The Part 1 §5 CH-2 per-hop derivation
                  (s_i = X25519(alpha_i, onion_i); hop keys via HKDF-BLAKE2s
                  under sphinx-rho/sphinx-mu/sphinx-delta) has no reference
                  implementation in this toy (dispersal.py: "no onion layer"),
                  so its vectors cannot be generated honestly yet. This entry
                  records that gap explicitly rather than hand-waving it.
"""
import hashlib
import json
import pathlib

import dispersal
import e2e

HERE = pathlib.Path(__file__).resolve().parent
VJSON = HERE / "vectors.json"


def hx(b):
    return bytes(b).hex()


def build_hkdf():
    cases = [
        (bytes([0x02]) * 32, b"e2e-content", 32),
        (bytes([0x02]) * 32, b"tag", 32),
        (bytes([0x02]) * 32, b"box\x00\x00\x00\x00\x00\x00\x4e\x20", 16),
        (bytes(range(32)), b"", 40),
        (bytes([0xFF]) * 32, b"info-label", 64),
    ]
    return {
        "comment": (
            "HKDF-BLAKE2s (RFC 5869 structure, BLAKE2s as the hash) is the one "
            "KDF under every ScrambNet derivation: content_key, the SP-7 tag key, "
            "and the box_id all call it. out = HKDF-BLAKE2s(key, info, length). "
            "An impl that reproduces these reproduces content_key/k_tag/box_id."
        ),
        "cases": [
            {"key": hx(k), "info": hx(info), "length": n,
             "out": hx(e2e._hkdf_blake2s(k, info, n))}
            for (k, info, n) in cases
        ],
    }


def build_gf_tables():
    exp = bytes(dispersal._EXP[i] for i in range(510))
    log = bytes(dispersal._LOG[i] for i in range(256))
    return {
        "comment": (
            "GF(2^8) with reduction polynomial 0x11b and generator 3 (the AES "
            "field). _EXP is 510 entries (doubled so gf_mul can add logs without "
            "a mod), _LOG is 256 entries. gf_mul(a,b) = _EXP[_LOG[a]+_LOG[b]] "
            "(0 if either operand is 0); gf_inv(a) = _EXP[255-_LOG[a]]. Pinned "
            "normative: a conforming impl MUST build byte-identical tables. "
            "Verify by the two blake2s hashes; the full tables are included so a "
            "second impl can diff directly."
        ),
        "exp_blake2s": hashlib.blake2s(exp).hexdigest(),
        "log_blake2s": hashlib.blake2s(log).hexdigest(),
        "exp": hx(exp),
        "log": hx(log),
        "mul_samples": [[a, b, dispersal.gf_mul(a, b)]
                        for (a, b) in [(0, 5), (1, 1), (2, 2), (0x53, 0xCA),
                                       (0xFF, 0xFF), (0x80, 0x02)]],
        "inv_samples": [[a, dispersal.gf_inv(a)] for a in (1, 2, 0x53, 0xFF)],
    }


def build_params():
    cases = []
    for (k, n) in [(3, 4), (1, 1), (2, 3), (15, 15), (1, 15)]:
        packed = (k << 4) | n
        cases.append({"k": k, "n": n, "packed_byte": packed,
                      "packed_hex": "%02x" % packed})
    return {
        "comment": (
            "The share-payload params byte packs k and n one nibble each: "
            "params = (k << 4) | n, so k = params >> 4 and n = params & 0x0F. "
            "This nibble order is vector-locked because the two PoC parsers once "
            "disagreed on it (SP-7a); a conforming parser MUST read k from the "
            "high nibble and n from the low nibble."
        ),
        "formula": "params = (k << 4) | n ; k = params >> 4 ; n = params & 0x0F",
        "cases": cases,
    }


def build_e2e_dispersal():
    kpair = bytes([0x02]) * 32
    msg_nonce = bytes.fromhex("0001020304050607")
    plaintext = b"ScrambNet full-path vector"
    ct = e2e.seal(kpair, msg_nonce, plaintext)
    # deterministic Shamir coefficients so the split is reproducible: split needs
    # (k-1) * len(secret) coefficient bytes (one degree-(k-1) polynomial per
    # secret byte), here 2 * len(ct).
    coeffs = bytes((0xA0 + i) & 0xFF for i in range(2 * len(ct)))
    shares = dispersal.split(ct, n=4, k=3, coeffs=coeffs)
    # reconstruct from shares 1,2,3 and decrypt to show the composition closes.
    recovered_ct = dispersal.reconstruct({1: shares[0], 2: shares[1], 3: shares[2]})
    recovered_pt = e2e.open_(kpair, msg_nonce, recovered_ct)
    assert recovered_pt == plaintext
    assert recovered_ct == ct
    return {
        "comment": (
            "The full content path as one vector (SP-1 composition): "
            "ciphertext = seal(kpair, msg_nonce, plaintext); "
            "shares = split(ciphertext, n=4, k=3, coeffs); any k=3 of the n=4 "
            "shares reconstruct the ciphertext, which open_ decrypts back to the "
            "plaintext. Pins the composition, not only seal and split in "
            "isolation. coeffs are fixed here only to make the split "
            "reproducible (a real sender draws them from a CSPRNG, RI-2)."
        ),
        "kpair": hx(kpair),
        "msg_nonce": hx(msg_nonce),
        "plaintext": hx(plaintext),
        "coeffs": hx(coeffs),
        "n": 4, "k": 3,
        "ciphertext": hx(ct),
        "shares": [hx(s) for s in shares],
        "reconstruct_from": [1, 2, 3],
    }


def build_sphinx_hop_pending():
    return {
        "status": "pending-implementation",
        "comment": (
            "Part 1 §5 CH-2 pins the per-hop key agreement: "
            "s_i = X25519(alpha_i, onion_i), and the hop keys (routing-info "
            "stream, the gamma MAC, the delta AEAD) via HKDF-BLAKE2s under the "
            "fixed labels sphinx-rho / sphinx-mu / sphinx-delta. There is no "
            "separate handshake transcript to vector (CH-1). These vectors are "
            "DECLARED PENDING, not hand-waved: this PoC implements no onion layer "
            "or X25519 (poc/dispersal.py: 'no onion layer'), so a reference "
            "output cannot be generated honestly yet. When a node implements the "
            "Sphinx layer, this entry is replaced by (alpha_i, onion_i) -> s_i "
            "and the three label-derived hop keys. Until then, two "
            "implementations are NOT yet proven to interoperate at the circuit "
            "layer (I-1), and this is stated openly (see Part 9 RI-10)."
        ),
        "labels": ["sphinx-rho", "sphinx-mu", "sphinx-delta"],
    }


def build():
    data = json.loads(VJSON.read_text())
    data["hkdf"] = build_hkdf()
    data["gf_tables"] = build_gf_tables()
    data["params"] = build_params()
    data["e2e_dispersal"] = build_e2e_dispersal()
    data["sphinx_hop"] = build_sphinx_hop_pending()
    VJSON.write_text(json.dumps(data, indent=2) + "\n")
    return data


if __name__ == "__main__":
    d = build()
    print("conformance vectors added. sections now:", list(d.keys()))
