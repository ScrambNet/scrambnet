"""ScrambNet gossip-record encoding and signatures -- reference implementation (DRAFT).

Executable companion to docs/en/spec/02-gossip-record.md, section 2A
(requirements GR-21..GR-30, roadmap 3.4): the canonical-CBOR profile and the
strict Ed25519 verification profile by which a relay's self-signed descriptor is
encoded, signed, and -- the part that actually matters -- verified *identically*
by every node. Canonical CBOR is signature-critical: two implementations that
disagree on a record's canonical bytes, or on whether a signature is valid,
reject each other's valid records (an I-1 partition) or split on a crafted record
(a security-relevant split-view). This file pins both to the byte so the
cross-implementation vectors in vectors.json["records"] can be regenerated and a
second implementation can prove conformance (GR-30).

NOT PRODUCTION CODE. The Ed25519 below is hand-rolled in pure Python (stdlib
hashlib.sha512 only) for readability and to honour this PoC's "no dependencies"
policy -- it is NOT constant-time (the scalar multiply branches on key bits) and
MUST NOT protect anything. A real node MUST use a vetted constant-time Ed25519
that matches this profile (Part 9, RI-8/RI-11). The point of this module is
*agreement on the accept/reject predicate*, not secrecy.

Profile pinned here (see Part 2 section 2A):
  - canonical CBOR: definite-length, shortest-form heads, four major types only
    (uint/byte-string/array/map), no duplicate keys, ascending numeric key order
    (== bytewise order of the shortest-form key), verify over received bytes;
  - Ed25519: RFC 8032 cofactorless [S]B = R + [k]A, k = SHA-512(R||A||M) mod L,
    plus S < L (canonical scalar), canonical point encodings for R and A, and
    small-/mixed-order A and R rejected (prime-order-subgroup membership). The
    signing input M is domain-separated: b"ScrambNet-gossip-v1" || 0x00 ||
    canon(record without key 7).
"""

import hashlib

# ----------------------------------------------------------------------------
# Canonical CBOR (the restricted profile of GR-21/GR-22). Four major types.
# ----------------------------------------------------------------------------

M_UINT = 0        # major type 0: unsigned integer
M_BYTES = 2       # major type 2: byte string
M_ARRAY = 4       # major type 4: array
M_MAP = 5         # major type 5: map


class CanonError(ValueError):
    """A record's bytes are not the canonical encoding (GR-21/GR-22/GR-23)."""


def _encode_head(major, n):
    """Shortest-form CBOR head for (major type, argument n). GR-21."""
    mt = major << 5
    if n < 0:
        raise CanonError("negative argument")
    if n <= 23:
        return bytes([mt | n])
    if n <= 0xFF:
        return bytes([mt | 24, n])
    if n <= 0xFFFF:
        return bytes([mt | 25, (n >> 8) & 0xFF, n & 0xFF])
    if n <= 0xFFFFFFFF:
        return bytes([mt | 26]) + n.to_bytes(4, "big")
    if n <= 0xFFFFFFFFFFFFFFFF:
        return bytes([mt | 27]) + n.to_bytes(8, "big")
    raise CanonError("argument too large for CBOR")


def encode(value):
    """Canonically encode a restricted value: int (uint), bytes, list, or dict
    with int keys. Produces the one legal encoding (GR-21/GR-22) or raises."""
    if isinstance(value, bool):
        # bool is a subclass of int in Python; the profile forbids booleans.
        raise CanonError("booleans are not a permitted type (GR-21)")
    if isinstance(value, int):
        if value < 0:
            raise CanonError("negative integers are not permitted (GR-21)")
        return _encode_head(M_UINT, value)
    if isinstance(value, (bytes, bytearray)):
        return _encode_head(M_BYTES, len(value)) + bytes(value)
    if isinstance(value, list):
        out = _encode_head(M_ARRAY, len(value))
        for item in value:
            out += encode(item)
        return out
    if isinstance(value, dict):
        for k in value:
            if isinstance(k, bool) or not isinstance(k, int) or k < 0:
                raise CanonError("map keys MUST be unsigned integers (GR-22)")
        # ascending numeric key order == bytewise order of shortest-form key.
        items = sorted(value.items(), key=lambda kv: kv[0])
        out = _encode_head(M_MAP, len(items))
        for k, v in items:
            out += _encode_head(M_UINT, k)
            out += encode(v)
        return out
    raise CanonError("type %r is not a permitted CBOR type (GR-21)" % type(value))


def _decode(buf, i):
    """Decode one item at buf[i:], enforcing the canonical profile. Returns
    (value, next_index). Raises CanonError on any non-canonical construct."""
    if i >= len(buf):
        raise CanonError("truncated")
    ib = buf[i]
    major = ib >> 5
    ai = ib & 0x1F  # additional info
    i += 1
    # Read the argument with shortest-form enforcement.
    if ai < 24:
        arg = ai
    elif ai == 24:
        if i >= len(buf):
            raise CanonError("truncated head")
        arg = buf[i]; i += 1
        if arg <= 23:
            raise CanonError("non-shortest 1-byte argument (GR-21)")
    elif ai == 25:
        if i + 2 > len(buf):
            raise CanonError("truncated head")
        arg = int.from_bytes(buf[i:i+2], "big"); i += 2
        if arg <= 0xFF:
            raise CanonError("non-shortest 2-byte argument (GR-21)")
    elif ai == 26:
        if i + 4 > len(buf):
            raise CanonError("truncated head")
        arg = int.from_bytes(buf[i:i+4], "big"); i += 4
        if arg <= 0xFFFF:
            raise CanonError("non-shortest 4-byte argument (GR-21)")
    elif ai == 27:
        if i + 8 > len(buf):
            raise CanonError("truncated head")
        arg = int.from_bytes(buf[i:i+8], "big"); i += 8
        if arg <= 0xFFFFFFFF:
            raise CanonError("non-shortest 8-byte argument (GR-21)")
    else:
        # ai 28..30 reserved, 31 = indefinite-length: all forbidden.
        raise CanonError("indefinite-length or reserved head (GR-21)")

    if major == M_UINT:
        return arg, i
    if major == M_BYTES:
        if i + arg > len(buf):
            raise CanonError("truncated byte string")
        return bytes(buf[i:i+arg]), i + arg
    if major == M_ARRAY:
        out = []
        for _ in range(arg):
            v, i = _decode(buf, i)
            out.append(v)
        return out, i
    if major == M_MAP:
        out = {}
        prev_key = None
        for _ in range(arg):
            if i >= len(buf):
                raise CanonError("truncated map")
            kb = buf[i]
            if kb >> 5 != M_UINT:
                raise CanonError("map key is not an unsigned integer (GR-22)")
            k, i = _decode(buf, i)
            if prev_key is not None and k <= prev_key:
                # not strictly ascending => wrong order or duplicate key.
                raise CanonError("map keys not strictly ascending (GR-22)")
            prev_key = k
            v, i = _decode(buf, i)
            out[k] = v
        return out, i
    # majors 1 (neg int), 3 (text), 6 (tag), 7 (float/simple) are forbidden.
    raise CanonError("forbidden major type %d (GR-21)" % major)


def decode_canonical(buf):
    """Decode a full record, requiring the whole buffer to be the canonical
    encoding of exactly one top-level item with no trailing bytes (GR-23)."""
    value, i = _decode(buf, 0)
    if i != len(buf):
        raise CanonError("trailing bytes after top-level item (GR-23)")
    return value


def is_canonical(buf):
    """True iff buf is exactly the canonical encoding of what it decodes to
    (GR-23: verify over received bytes). Decodes under the strict profile, then
    re-encodes and checks byte equality -- a total accept/reject predicate."""
    try:
        value = decode_canonical(buf)
    except CanonError:
        return False
    return encode(value) == bytes(buf)


# ----------------------------------------------------------------------------
# Ed25519 (RFC 8032) with the strict verification profile of GR-25..GR-28.
# Hand-rolled, pure-Python, NOT constant-time.
# ----------------------------------------------------------------------------

_p = 2**255 - 19
_L = 2**252 + 27742317777372353535851937790883648493
_d = (-121665 * pow(121666, _p - 2, _p)) % _p
_I = pow(2, (_p - 1) // 4, _p)  # sqrt(-1)


def _inv(x):
    return pow(x, _p - 2, _p)


# Base point B
def _recover_x(y, sign):
    if y >= _p:
        return None
    xx = (y * y - 1) * _inv(_d * y * y + 1) % _p
    x = pow(xx, (_p + 3) // 8, _p)
    if (x * x - xx) % _p != 0:
        x = (x * _I) % _p
    if (x * x - xx) % _p != 0:
        return None  # not a square: not a valid point
    if (x & 1) != sign:
        x = _p - x
    return x


_By = 4 * _inv(5) % _p
_Bx = _recover_x(_By, 0)
_B = (_Bx, _By, 1, (_Bx * _By) % _p)  # extended coords (X, Y, Z, T)


def _edwards_add(P, Q):
    (X1, Y1, Z1, T1) = P
    (X2, Y2, Z2, T2) = Q
    A = (Y1 - X1) * (Y2 - X2) % _p
    Bb = (Y1 + X1) * (Y2 + X2) % _p
    C = T1 * 2 * _d * T2 % _p
    D = Z1 * 2 * Z2 % _p
    E = Bb - A
    F = D - C
    G = D + C
    H = Bb + A
    return (E * F % _p, G * H % _p, F * G % _p, E * H % _p)


def _scalarmult(P, e):
    Q = (0, 1, 1, 0)  # neutral element
    while e > 0:
        if e & 1:
            Q = _edwards_add(Q, P)
        P = _edwards_add(P, P)
        e >>= 1
    return Q


def _encode_point(P):
    zi = _inv(P[2])
    x = P[0] * zi % _p
    y = P[1] * zi % _p
    return (y | ((x & 1) << 255)).to_bytes(32, "little")


def _decode_point(s):
    """Decode a 32-byte point with CANONICAL-ENCODING enforcement (GR-27).
    Returns the point in extended coords, or None if the encoding is
    non-canonical or not on the curve."""
    if len(s) != 32:
        return None
    y = int.from_bytes(s, "little")
    sign = (y >> 255) & 1
    y &= (1 << 255) - 1
    if y >= _p:
        return None  # non-canonical: y-coordinate not reduced (GR-27)
    x = _recover_x(y, sign)
    if x is None:
        return None
    if x == 0 and sign == 1:
        return None  # non-canonical: negative zero (GR-27)
    return (x, y, 1, (x * y) % _p)


def _is_identity(P):
    zi = _inv(P[2])
    return (P[0] * zi % _p) == 0 and (P[1] * zi % _p) == 1


def _in_prime_order_subgroup(P):
    """True iff P is a point of the large prime-order subgroup and is not a
    small-order or mixed-order point (GR-28). The test is `[L]P == identity`
    AND `P != identity`:
      - `[L]P == identity` holds only when order(P) divides L; L is prime, so
        this admits exactly the identity (order 1) and the prime-order points
        (order L), and REJECTS every mixed-order point (order 2L/4L/8L) and every
        small-order point of order 2/4/8 (whose order does not divide L).
      - the extra `P != identity` then rejects the one remaining small-order
        case, the identity itself (order 1).
    A small-order-encoding blacklist is deliberately NOT used: it would admit
    mixed-order points, on which the cofactored and cofactorless verification
    equations diverge. This uses a scalar multiply by L (a correctness check),
    which is not the `[8]`-cofactored verification equation GR-25 forbids."""
    if _is_identity(P):
        return False
    return _is_identity(_scalarmult(P, _L))


def secret_to_public(sk_seed):
    """Derive the 32-byte Ed25519 public key A from a 32-byte seed (RFC 8032)."""
    if len(sk_seed) != 32:
        raise ValueError("Ed25519 seed MUST be 32 bytes")
    h = hashlib.sha512(sk_seed).digest()
    a = int.from_bytes(h[:32], "little")
    a &= (1 << 254) - 8
    a |= (1 << 254)
    A = _scalarmult(_B, a)
    return _encode_point(A)


def sign(sk_seed, msg):
    """RFC 8032 Ed25519 signature over msg (already the full signing input)."""
    h = hashlib.sha512(sk_seed).digest()
    a = int.from_bytes(h[:32], "little")
    a &= (1 << 254) - 8
    a |= (1 << 254)
    prefix = h[32:]
    A = _encode_point(_scalarmult(_B, a))
    r = int.from_bytes(hashlib.sha512(prefix + msg).digest(), "little") % _L
    R = _encode_point(_scalarmult(_B, r))
    k = int.from_bytes(hashlib.sha512(R + A + msg).digest(), "little") % _L
    S = (r + k * a) % _L
    return R + S.to_bytes(32, "little")


def verify(public, sig, msg):
    """Strict verification (GR-25..GR-28). Returns True/False, never raises on
    bad input -- a non-conforming record is simply invalid.

    Enforces: canonical point encodings for A and R (GR-27); A and R in the
    prime-order subgroup, i.e. not small-/mixed-order (GR-28); S < L canonical
    scalar (GR-26); the RFC 8032 COFACTORLESS equation [S]B = R + [k]A (GR-25)."""
    if len(sig) != 64 or len(public) != 32:
        return False
    Rpt = _decode_point(sig[:32])          # GR-27 canonical R
    if Rpt is None:
        return False
    S = int.from_bytes(sig[32:], "little")
    if S >= _L:                            # GR-26 canonical scalar
        return False
    A = _decode_point(public)              # GR-27 canonical A
    if A is None:
        return False
    if not _in_prime_order_subgroup(A):    # GR-28 no small/mixed-order A
        return False
    if not _in_prime_order_subgroup(Rpt):  # GR-28 no small/mixed-order R
        return False
    k = int.from_bytes(hashlib.sha512(sig[:32] + public + msg).digest(), "little") % _L
    # cofactorless: [S]B  ==  R + [k]A   (GR-25, no [8] multiply)
    lhs = _scalarmult(_B, S)
    rhs = _edwards_add(Rpt, _scalarmult(A, k))
    # compare in affine coords
    return _encode_point(lhs) == _encode_point(rhs)


# ----------------------------------------------------------------------------
# The gossip-record signing input (GR-24) and a convenience sign/verify.
# ----------------------------------------------------------------------------

CONTEXT = b"ScrambNet-gossip-v1"
SIG_KEY = 7


def signing_input(record_fields):
    """GR-24: CONTEXT || 0x00 || canon(record without key 7). record_fields is a
    dict of int->value WITHOUT key 7 (the signature itself)."""
    if SIG_KEY in record_fields:
        raise CanonError("signing input is over the record WITHOUT key 7 (GR-24)")
    return CONTEXT + b"\x00" + encode(record_fields)


def sign_record(sk_seed, record_fields):
    """Return the full canonical record bytes (including key 7 = sig)."""
    m = signing_input(record_fields)
    sig = sign(sk_seed, m)
    full = dict(record_fields)
    full[SIG_KEY] = sig
    return encode(full)


N_ADDR = 256  # (s) max bytes of an addr blob (GR-21a)


def _record_shape_ok(fields):
    """GR-21a: the shapes of the known keys 0..7 are pinned (unknown keys >= 8
    are signed-but-ignored and may hold any GR-21-legal value). A composite
    field left unpinned (e.g. addrs) is a canonicalization-ambiguity by which
    two implementations split on a signature-valid record, so the shape is a
    reject predicate, not a convention."""
    if not isinstance(fields, dict):
        return False
    def is_uint(x):
        return isinstance(x, int) and not isinstance(x, bool) and x >= 0
    def is_bytes_len(x, n):
        return isinstance(x, (bytes, bytearray)) and len(x) == n
    # key 0 v: uint ; 1 id: bytes(32) ; 2 onion: bytes(32) ; 4 bw: uint ;
    # 5 created: uint ; 6 expiry: uint ; 7 sig: bytes(64)
    if not is_uint(fields.get(0)):
        return False
    if not is_bytes_len(fields.get(1), 32):
        return False
    if not is_bytes_len(fields.get(2), 32):
        return False
    if not is_uint(fields.get(4)):
        return False
    if not is_uint(fields.get(5)):
        return False
    if not is_uint(fields.get(6)):
        return False
    if not is_bytes_len(fields.get(SIG_KEY), 64):
        return False
    # key 3 addrs: array of [uint, bytes(<=N_ADDR)] pairs; MAY be empty.
    addrs = fields.get(3)
    if not isinstance(addrs, list):
        return False
    for item in addrs:
        if not (isinstance(item, list) and len(item) == 2):
            return False
        if not is_uint(item[0]):
            return False
        if not (isinstance(item[1], (bytes, bytearray)) and len(item[1]) <= N_ADDR):
            return False
    return True


def verify_record(record_bytes):
    """Full GR-21..GR-28 verification of a received record. Returns the decoded
    field dict on success, or None (silent uniform failure, GR-4/GR-29).

    Check order (GR-29a): canonical-encoding (GR-23) and field-shape (GR-21a)
    first, then the signature (GR-25..GR-28). A record that fails any of these
    is invalid and MUST NOT evict a stored record under GR-5 dedup (the caller
    runs dedup only on records this function accepts)."""
    if not is_canonical(record_bytes):          # GR-23 verify over received bytes
        return None
    fields = decode_canonical(record_bytes)
    if not isinstance(fields, dict) or SIG_KEY not in fields:
        return None
    if not _record_shape_ok(fields):            # GR-21a field shapes
        return None
    ident = fields[1]
    sig = fields[SIG_KEY]
    without_sig = {k: v for k, v in fields.items() if k != SIG_KEY}
    m = signing_input(without_sig)
    if not verify(bytes(ident), bytes(sig), m):  # GR-25..GR-28
        return None
    return fields


def demo():
    """Show the gossip-record profile end to end: sign a record, verify it,
    and show that the strict profile rejects a mixed-order public key that a
    permissive (ZIP-215) verifier would accept (GR-28)."""
    print("ScrambNet gossip-record profile (Part 2 §2A, GR-21..GR-30)")
    seed = bytes([3]) * 32
    A = secret_to_public(seed)
    fields = {0: 1, 1: A, 2: bytes([0x11]) * 32,
              3: [[0, bytes.fromhex("cafe")]], 4: 1000,
              5: 1731000000, 6: 1731600000}
    rec = sign_record(seed, fields)
    print("  record: %d bytes, canonical=%s" % (len(rec), is_canonical(rec)))
    out = verify_record(rec)
    print("  verify_record: %s (id matches: %s)"
          % ("accepted" if out else "REJECTED", out and out[1] == A))

    # a non-canonical copy (one trailing byte) must be rejected (GR-23)
    print("  + trailing byte  -> %s"
          % ("REJECTED" if verify_record(rec + b"\x00") is None else "accepted!"))

    # a mixed-order public key: canonical CBOR, canonical point, but not
    # prime-order; GR-28 rejects it where a small-order blacklist would not.
    Aprime = _decode_point(secret_to_public(bytes([7]) * 32))
    mixed = _encode_point(_edwards_add(Aprime, (0, _p - 1, 1, 0)))
    f2 = dict(fields)
    f2[1] = mixed
    bad = encode({**f2, SIG_KEY: sign(seed, signing_input(f2))})
    print("  mixed-order id   -> %s  (GR-28 [L]P-test; a blacklist would miss it)"
          % ("REJECTED" if verify_record(bad) is None else "accepted!"))
    print("  (Ed25519 here is cross-checked bit-for-bit against an independent "
          "library in test_gossip.py.)")


if __name__ == "__main__":
    demo()
