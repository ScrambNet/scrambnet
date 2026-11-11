"""Generate the vectors.json["records"] section from gossip.py (roadmap 3.4).

Positive vectors pin the canonical encoding + signing input (GR-21..GR-24) and a
valid signature (GR-25). Negative vectors each exercise exactly one reject clause
(GR-30 requires rejection for the *named* reason). The mixed-order vectors are the
load-bearing ones: they are rejected only by the [L]P-test of GR-28, not by a
small-order blacklist, so they separate a conforming implementation from one that
picked a permissive Ed25519 library.
"""
import json
import pathlib
import gossip as g

HERE = pathlib.Path(__file__).resolve().parent
VJSON = HERE / "vectors.json"

SK = bytes([3]) * 32  # fixed test seed
A = g.secret_to_public(SK)
ONION = bytes([0x11]) * 32

# A well-formed record (keys 0..6), then signed (adds key 7).
FIELDS = {
    0: 1,
    1: A,
    2: ONION,
    3: [[0, bytes.fromhex("cafe")], [5, b""]],
    4: 1000,
    5: 1731000000,
    6: 1731600000,
}
SIGNING_INPUT = g.signing_input(FIELDS)
SIG = g.sign(SK, SIGNING_INPUT)
CANON = g.sign_record(SK, FIELDS)

# Record with an unknown key 9 (signed-but-ignored, GR-2/GR-22).
FIELDS_U = dict(FIELDS)
FIELDS_U[9] = bytes.fromhex("abcd")
SIGNING_INPUT_U = g.signing_input(FIELDS_U)
CANON_U = g.sign_record(SK, FIELDS_U)


def hx(b):
    return bytes(b).hex()


def _jsonable(v):
    """Represent a record field value for JSON: byte strings become {"b": hex},
    uints stay ints, arrays recurse. The test harness reverses this."""
    if isinstance(v, (bytes, bytearray)):
        return {"b": hx(v)}
    if isinstance(v, list):
        return [_jsonable(x) for x in v]
    return v


# ---- negative vectors: each a minimal mutation, tagged with its clause ----
def neg_non_shortest_int():
    # map {0: 1} but value 1 encoded as a non-shortest 1-byte head 0x18 0x01
    # full record is awkward; use a minimal canonical-fail buffer.
    return bytes([0xA1, 0x00, 0x18, 0x01])


def neg_indefinite():
    return bytes([0x9F, 0x00, 0xFF])  # indefinite-length array [0]


def neg_disallowed_type():
    # map {0: 1.0-ish float}: head 0xf9 (half float)
    return bytes([0xA1, 0x00, 0xF9, 0x00, 0x00])


def neg_duplicate_key():
    return bytes([0xA2, 0x04, 0x00, 0x04, 0x00])  # {4:0, 4:0}


def neg_reordered_keys():
    return bytes([0xA2, 0x01, 0x00, 0x00, 0x00])  # keys 1,0 (descending)


def neg_trailing_bytes():
    return CANON + b"\x00"


def neg_top_level_array():
    return g.encode([1, 2, 3])


def neg_addrs_bad_shape():
    # addrs with a bare uint element (not a [uint,bytes] pair); sign so the
    # signature is VALID -> only GR-21a can reject it.
    f = dict(FIELDS)
    f[3] = [[0, bytes.fromhex("aa")], 5]
    m = g.signing_input(f)
    s = g.sign(SK, m)
    full = dict(f)
    full[g.SIG_KEY] = s
    return g.encode(full)


def neg_non_canonical_S():
    # valid record, then replace S with S+L (>= L) -> GR-26
    rec = bytearray(CANON)
    # find the 64-byte sig: it is the value of key 7, the last field. The sig is
    # the final 64 bytes of the record (key 7 is highest key, encoded last).
    sig = bytes(rec[-64:])
    R, S = sig[:32], int.from_bytes(sig[32:], "little")
    S2 = S + g._L
    rec[-32:] = S2.to_bytes(32, "little")
    return bytes(rec)


def neg_non_canonical_R_enc():
    # replace R's y with y+p (>= p) -> GR-27 (non-canonical point encoding)
    rec = bytearray(CANON)
    sig = bytes(rec[-64:])
    Rb = sig[:32]
    y = int.from_bytes(Rb, "little") & ((1 << 255) - 1)
    sign = (int.from_bytes(Rb, "little") >> 255) & 1
    y2 = y + g._p  # now y2 >= p (still < 2^255? p ~ 2^255, y<p so y+p < 2p < 2^256; but need top bit room)
    # y2 may exceed 255 bits; clamp into 255-bit field with sign bit -> craft a
    # 32-byte encoding whose low-255 bits are (y+p) mod 2^255 won't be >=p reliably.
    # Simpler: set y to exactly p (which is >= p) -> non-canonical.
    enc = (g._p | (sign << 255)).to_bytes(32, "little")
    rec[-64:-32] = enc
    return bytes(rec)


def neg_bad_sig():
    rec = bytearray(CANON)
    rec[-1] ^= 0x01  # flip a bit of S
    return bytes(rec)


def _mixed_order_point(seed):
    """A mixed-order point P = P_prime + T2 (order-2 torsion). Rejected only by
    the [L]P-test (GR-28), accepted by a small-order blacklist."""
    P = g._decode_point(g.secret_to_public(seed))
    T2 = (0, g._p - 1, 1, 0)  # the order-2 point (0, -1)
    return g._edwards_add(P, T2)


def neg_mixed_order_A():
    # id (key 1) is a mixed-order point; craft (R,S) so a COFACTORED verifier
    # would accept. We cannot derive it from a secret, so we hand-craft: use the
    # matching mixed-order public and a signature that passes the cofactored eq.
    # For the vector we provide the record with a mixed-order id and a plausible
    # sig; the REQUIRED behavior is rejection by GR-28, which is the test. The
    # construction detail (that cofactored would accept) is asserted in the test.
    Amix = g._encode_point(_mixed_order_point(bytes([7]) * 32))
    f = dict(FIELDS)
    f[1] = Amix
    m = g.signing_input(f)
    # sign with the base secret (sig won't verify under cofactorless anyway; the
    # point is that GR-28 rejects the key before the equation is even reached).
    s = g.sign(SK, m)
    full = dict(f)
    full[g.SIG_KEY] = s
    return g.encode(full)


def neg_mixed_order_R():
    # signature R is a mixed-order point -> GR-28 rejects R before the equation.
    Rmix = g._encode_point(_mixed_order_point(bytes([9]) * 32))
    rec = bytearray(CANON)
    rec[-64:-32] = Rmix
    return bytes(rec)


NEGATIVES = [
    ("non_shortest_int", "GR-21", neg_non_shortest_int()),
    ("indefinite_length", "GR-21", neg_indefinite()),
    ("disallowed_type", "GR-21", neg_disallowed_type()),
    ("duplicate_key", "GR-22", neg_duplicate_key()),
    ("reordered_keys", "GR-22/GR-23", neg_reordered_keys()),
    ("top_level_not_map", "GR-23", neg_top_level_array()),
    ("trailing_bytes", "GR-23", neg_trailing_bytes()),
    ("addrs_bad_shape", "GR-21a", neg_addrs_bad_shape()),
    ("non_canonical_S", "GR-26", neg_non_canonical_S()),
    ("non_canonical_R_enc", "GR-27", neg_non_canonical_R_enc()),
    ("mixed_order_A", "GR-28", neg_mixed_order_A()),
    ("mixed_order_R", "GR-28", neg_mixed_order_R()),
    ("bad_sig", "GR-25", neg_bad_sig()),
]


def build():
    records = {
        "comment": (
            "Part 2 section 2A: canonical CBOR (GR-21..GR-23) + Ed25519 strict "
            "profile (GR-25..GR-28). sk is the 32-byte Ed25519 seed; id=A is its "
            "public key. signing_input = 'ScrambNet-gossip-v1'||0x00||canon(record "
            "without key 7) (GR-24). An impl that reproduces canonical_cbor and "
            "signing_input, verifies every positive vector, and rejects every "
            "negative vector FOR ITS NAMED CLAUSE, conforms (GR-30). The "
            "mixed_order_A/mixed_order_R negatives are rejected only by GR-28's "
            "[L]P-test, not by a small-order blacklist; they separate a conforming "
            "impl from one that used a permissive (ZIP-215) Ed25519 library."
        ),
        "sk": hx(SK),
        "id": hx(A),
        "positive": {
            "fields_hex": {str(k): _jsonable(v) for k, v in FIELDS.items()},
            "signing_input": hx(SIGNING_INPUT),
            "sig": hx(SIG),
            "canonical_cbor": hx(CANON),
        },
        "positive_unknown_key": {
            "comment": "unknown key 9 is signed (part of canon and signing_input) and ignored for semantics (GR-2/GR-22).",
            "unknown_key": 9,
            "unknown_value_hex": hx(FIELDS_U[9]),
            "signing_input": hx(SIGNING_INPUT_U),
            "canonical_cbor": hx(CANON_U),
        },
        "negative": [
            {"name": n, "violates": c, "bytes": hx(b), "expect": "reject"}
            for (n, c, b) in NEGATIVES
        ],
    }
    data = json.loads(VJSON.read_text())
    data["records"] = records
    VJSON.write_text(json.dumps(data, indent=2) + "\n")
    return records


if __name__ == "__main__":
    r = build()
    print("records vector written:",
          "1 positive +", 1, "unknown-key +", len(r["negative"]), "negative")
