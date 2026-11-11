"""ScrambNet dispersal core -- reference implementation (DRAFT).

Executable companion to docs/en/spec/01-share-packet.md. Pure Python 3
standard library, written to be read: every requirement implemented here
is cited by number (SP-n, I-n).

NOT PRODUCTION CODE. No constant-time arithmetic, no networking, no onion
layer, no end-to-end AEAD: per SP-1 the dispersal layer only ever sees
opaque end-to-end ciphertext, so this module treats its input as opaque
bytes and the tests feed it random data. Emission scheduling (SP-9) is
out of scope here. Do not use this file to protect anything.
"""

import hashlib
import secrets

# Sizes from spec Part 1 (strawman values, marked (s) there).
SHARE_BYTES = 1792   # Shamir share length inside delta
TAG_BYTES = 16       # SP-7 recipient-keyed PRF tag
DELTA_BYTES = 1856   # payload field of the 2048-byte Sphinx packet
MAX_MESSAGE = SHARE_BYTES - 2  # SP-8: 2-byte length prefix inside the pad

# --- GF(2^8), AES polynomial 0x11B, log/exp tables on generator 0x03 ---

_EXP = [0] * 510
_LOG = [0] * 256
_x = 1
for _i in range(255):
    _EXP[_i] = _x
    _LOG[_x] = _i
    _x = (_x << 1) ^ _x          # multiply by the generator 0x03
    if _x & 0x100:
        _x ^= 0x11B
for _i in range(255, 510):
    _EXP[_i] = _EXP[_i - 255]
del _x, _i


def gf_mul(a: int, b: int) -> int:
    if a == 0 or b == 0:
        return 0
    return _EXP[_LOG[a] + _LOG[b]]


def gf_inv(a: int) -> int:
    if a == 0:
        raise ZeroDivisionError("0 has no inverse in GF(2^8)")
    return _EXP[255 - _LOG[a]]


def _eval(poly: bytes, x: int) -> int:
    """Evaluate poly[0] + poly[1]*x + ... at x (Horner)."""
    r = 0
    for c in reversed(poly):
        r = gf_mul(r, x) ^ c
    return r


# --- Shamir (n, k) secret sharing, per byte (spec Part 0, suite 0x01) ---

def _check_params(n: int, k: int) -> None:
    # SP-2 / Part 1 payload layout: k and n travel packed in one nibble each.
    if not (1 <= k <= n <= 15):
        raise ValueError("need 1 <= k <= n <= 15")


def split(secret: bytes, n: int, k: int, coeffs: bytes | None = None) -> list[bytes]:
    """Split `secret` into n shares, any k of which reconstruct it (SP-1).

    Each byte position is an independent degree-(k-1) polynomial with
    uniformly random coefficients; share i is the evaluation at x = i.
    `coeffs` exists only so test vectors can be deterministic.
    """
    _check_params(n, k)
    need = (k - 1) * len(secret)
    if coeffs is None:
        coeffs = secrets.token_bytes(need)
    elif len(coeffs) != need:
        raise ValueError(f"need exactly {need} coefficient bytes")
    shares = [bytearray(len(secret)) for _ in range(n)]
    for pos, s in enumerate(secret):
        poly = bytes([s]) + coeffs[pos * (k - 1):(pos + 1) * (k - 1)]
        for x in range(1, n + 1):
            shares[x - 1][pos] = _eval(poly, x)
    return [bytes(b) for b in shares]


def reconstruct(points: dict[int, bytes]) -> bytes:
    """Interpolate the secret (the value at x = 0) from {x: share}.

    Pass at least k consistent shares. With fewer than k the result is
    garbage by design -- and I-2 says more: it is *uniformly undetermined*,
    see floor_demo() for the enumeration that proves it.
    """
    xs = sorted(points)
    if not xs or any(not (1 <= x <= 15) for x in xs):
        raise ValueError("need >= 1 share with x in 1..15")
    lengths = {len(v) for v in points.values()}
    if len(lengths) != 1:
        raise ValueError("shares differ in length")
    # Lagrange basis evaluated at x = 0.
    basis = []
    for j in xs:
        num, den = 1, 1
        for m in xs:
            if m != j:
                num = gf_mul(num, m)
                den = gf_mul(den, m ^ j)
        basis.append(gf_mul(num, gf_inv(den)))
    out = bytearray(lengths.pop())
    for pos in range(len(out)):
        v = 0
        for lj, j in zip(basis, xs):
            v ^= gf_mul(lj, points[j][pos])
        out[pos] = v
    return bytes(out)


# --- SP-7: recipient-keyed share tags ---

def share_tag(recipient_key: bytes, msg_nonce: bytes, index: int) -> bytes:
    """tag = PRF(K_r, msg_nonce || index), keyed BLAKE2s per suite 0x01.

    Two shares of the same message share no observable value (SP-7); only
    the holder of K_r can recompute tags. Practical consequence this PoC
    makes explicit: the recipient recognizes shares by *precomputing* the
    tags of a window of expected nonces (e.g. a message counter), since
    msg_nonce itself travels inside the end-to-end layer.
    """
    return hashlib.blake2s(msg_nonce + bytes([index]),
                           key=recipient_key, digest_size=TAG_BYTES).digest()


# --- SP-8: padding to the share payload size ---

def pad(message: bytes) -> bytes:
    if len(message) > MAX_MESSAGE:
        raise ValueError("fragment above this layer (SP-8)")
    fill = secrets.token_bytes(MAX_MESSAGE - len(message))
    return len(message).to_bytes(2, "big") + message + fill


def unpad(padded: bytes) -> bytes:
    if len(padded) != SHARE_BYTES:
        raise ValueError("bad padded length")
    length = int.from_bytes(padded[:2], "big")
    if length > MAX_MESSAGE:
        raise ValueError("corrupt length prefix")
    return padded[2:2 + length]


# --- Part 1 section 4: share payload inside delta ---

def build_payload(tag: bytes, index: int, n: int, k: int, share: bytes) -> bytes:
    _check_params(n, k)
    if len(tag) != TAG_BYTES or len(share) != SHARE_BYTES or not (1 <= index <= n):
        raise ValueError("bad field size")
    body = tag + bytes([index]) + bytes([(k << 4) | n]) + share
    return body + secrets.token_bytes(DELTA_BYTES - len(body))


def parse_payload(payload: bytes) -> tuple[bytes, int, int, int, bytes]:
    # params byte is (k << 4) | n; return (k, n) in that order, matching
    # rendezvous.parse_slot so the two parsers never disagree on nibble order.
    if len(payload) != DELTA_BYTES:
        raise ValueError("bad payload size")
    tag = payload[:TAG_BYTES]
    index = payload[TAG_BYTES]
    params = payload[TAG_BYTES + 1]
    k, n = params >> 4, params & 0x0F
    share = payload[TAG_BYTES + 2:TAG_BYTES + 2 + SHARE_BYTES]
    return tag, index, k, n, share


# --- sender / recipient, dispersal layer only ---

def disperse(ciphertext: bytes, recipient_key: bytes, msg_nonce: bytes,
             n: int = 4, k: int = 3) -> list[bytes]:
    """SP-1: input MUST already be end-to-end ciphertext. SP-2 defaults.

    Returns n delta payloads; each belongs on its own disjoint circuit
    (OP-1) and MUST NOT be emitted as a simultaneous burst (SP-9) --
    both are outside this module.
    """
    shares = split(pad(ciphertext), n, k)
    return [build_payload(share_tag(recipient_key, msg_nonce, i + 1),
                          i + 1, n, k, s)
            for i, s in enumerate(shares)]


def recognize(payloads: list[bytes], recipient_key: bytes,
              nonce_window: list[bytes]) -> dict[bytes, bytes]:
    """Group arriving payloads by SP-7 tag and reconstruct what completes.

    Returns {msg_nonce: ciphertext} for every nonce with >= k shares.
    Payloads whose tag matches no expected (nonce, index) are ignored --
    to anyone without K_r, ours are equally unrecognizable (SP-7).
    """
    expected = {}
    for nonce in nonce_window:
        for index in range(1, 16):
            expected[share_tag(recipient_key, nonce, index)] = (nonce, index)
    groups: dict[bytes, dict[int, tuple[int, bytes]]] = {}
    for p in payloads:
        tag, index, k, n, share = parse_payload(p)
        hit = expected.get(tag)
        if hit is None or hit[1] != index:
            continue
        groups.setdefault(hit[0], {})[index] = (k, share)
    done = {}
    for nonce, got in groups.items():
        k = next(iter(got.values()))[0]
        if len(got) >= k:
            use = {x: s for x, (_, s) in sorted(got.items())[:k]}
            done[nonce] = unpad(reconstruct(use))
    return done


# --- I-2 made visible: brute-force enumeration of the floor ---

def floor_demo(k: int = 3, y: tuple[int, int] = (0x5A, 0xC3)) -> dict[int, int]:
    """With k-1 shares in hand, count, for every candidate secret byte s,
    how many degree-(k-1) polynomials are consistent with the shares.

    For k = 3 and shares y1 at x=1, y2 at x=2, enumerate all (c1, c2):
    x=1 forces s = y1 ^ c1 ^ c2; keep the triple iff x=2 also matches y2.
    The count comes back identical for all 256 candidates: the k-1 shares
    constrain the secret not at all, against unbounded compute (I-2).
    """
    if k != 3:
        raise NotImplementedError("demo enumerates the k = 3 case")
    y1, y2 = y
    counts = {s: 0 for s in range(256)}
    for c1 in range(256):
        for c2 in range(256):
            s = y1 ^ c1 ^ c2  # eval at x = 1
            if s ^ gf_mul(c1, 2) ^ gf_mul(c2, 4) == y2:  # eval at x = 2
                counts[s] += 1
    return counts


if __name__ == "__main__":
    # Round trip with the SP-2 strawman, losing one share on the way.
    key = secrets.token_bytes(32)
    nonce = (7).to_bytes(8, "big")  # message counter as nonce
    msg = b"the network carries packets, not opinions"
    payloads = disperse(msg, key, nonce, n=4, k=3)
    payloads.pop(1)  # one circuit failed: n - k = 1 loss is tolerated
    window = [i.to_bytes(8, "big") for i in range(16)]
    got = recognize(payloads, key, window)
    assert got == {nonce: msg}
    print(f"round trip: n=4 k=3, 1 share lost, message intact "
          f"({len(msg)} bytes in {DELTA_BYTES}-byte payloads, overhead x4)")

    counts = floor_demo()
    vals = set(counts.values())
    assert vals == {1}, vals
    print("floor (I-2): with k-1 shares, all 256 candidate secret bytes are "
          "consistent in exactly 1 way each -- uniform, nothing learned")
