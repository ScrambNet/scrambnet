"""ScrambNet end-to-end layer -- reference implementation (DRAFT).

Executable companion to docs/en/spec/01-share-packet.md, requirement SP-1:
"the sender MUST apply end-to-end encryption *before* dispersal, and dispersal
MUST be applied to the end-to-end ciphertext." Until this module existed the
PoC split plaintext, so the whole composition claim (unconditional floor under
a computational belt) was asserted by comment and never executed. This file is
the belt. dispersal.py and rendezvous.py now sit on top of it.

NOT PRODUCTION CODE. The AEAD below is ChaCha20-Poly1305 (suite 0x01)
implemented in pure Python for readability and to honour this PoC's "no
dependencies" policy -- it is NOT constant-time and leaks through timing;
a real node MUST use a vetted constant-time library. Do not protect anything
with this file.

Key establishment (the choice SP-1's post-quantum story hinges on):
  This PoC derives the AEAD key from the *pre-shared symmetric* `kpair` that
  the contact card already carries (RZ-2: "everything derives from kpair").
  There is NO asymmetric key agreement in the content path. The consequence,
  which is the reason the choice is made this way and which belongs in the
  spec: a >=k, record-everything adversary with a future quantum computer
  still cannot read content, because there is no Diffie-Hellman transcript for
  Shor to break -- only a symmetric secret the parties already share. An
  ephemeral X25519 exchange would have been simpler to bootstrap but would
  have handed exactly that adversary the plaintext once large quantum
  computers exist. "Harvest now, decrypt later" is therefore defeated at BOTH
  tiers under this choice: below k by Shamir (unconditional), at/above k by a
  symmetric AEAD under a pre-shared key (no public-key assumption to harvest).
  The honest cost is the bootstrap: the pre-shared `kpair` must reach the
  recipient over some prior confidential channel (the contact-card exchange),
  which is out of scope here and is where any residual public-key / PQ-KEM
  assumption would actually live.
"""

import hmac
import struct

AEAD_KEY_BYTES = 32
AEAD_NONCE_BYTES = 12   # ChaCha20-Poly1305 nonce
TAG_BYTES = 16          # Poly1305 tag

# msg_nonce as carried by SP-7 is 8 bytes (a message counter in the PoC).
# It is widened to the 12-byte AEAD nonce by left-padding with zeros; the
# same 8-byte value keys both the SP-7 tag and this AEAD, binding the two
# layers. Reusing a msg_nonce under one kpair is therefore doubly fatal:
# it collides SP-7 tags AND destroys ChaCha20-Poly1305 confidentiality.
MSG_NONCE_BYTES = 8


# --- ChaCha20 (RFC 8439) ---

def _rotl32(v: int, c: int) -> int:
    v &= 0xFFFFFFFF
    return ((v << c) | (v >> (32 - c))) & 0xFFFFFFFF


def _quarter(s: list, a: int, b: int, c: int, d: int) -> None:
    s[a] = (s[a] + s[b]) & 0xFFFFFFFF; s[d] = _rotl32(s[d] ^ s[a], 16)
    s[c] = (s[c] + s[d]) & 0xFFFFFFFF; s[b] = _rotl32(s[b] ^ s[c], 12)
    s[a] = (s[a] + s[b]) & 0xFFFFFFFF; s[d] = _rotl32(s[d] ^ s[a], 8)
    s[c] = (s[c] + s[d]) & 0xFFFFFFFF; s[b] = _rotl32(s[b] ^ s[c], 7)


_CONST = (0x61707865, 0x3320646e, 0x79622d32, 0x6b206574)  # "expand 32-byte k"


def _chacha_block(key: bytes, counter: int, nonce: bytes) -> bytes:
    st = list(_CONST)
    st += list(struct.unpack("<8I", key))
    st += [counter & 0xFFFFFFFF]
    st += list(struct.unpack("<3I", nonce))
    work = st[:]
    for _ in range(10):                 # 20 rounds = 10 column + 10 diagonal
        _quarter(work, 0, 4, 8, 12)
        _quarter(work, 1, 5, 9, 13)
        _quarter(work, 2, 6, 10, 14)
        _quarter(work, 3, 7, 11, 15)
        _quarter(work, 0, 5, 10, 15)
        _quarter(work, 1, 6, 11, 12)
        _quarter(work, 2, 7, 8, 13)
        _quarter(work, 3, 4, 9, 14)
    out = [(work[i] + st[i]) & 0xFFFFFFFF for i in range(16)]
    return struct.pack("<16I", *out)


def _chacha20(key: bytes, counter: int, nonce: bytes, data: bytes) -> bytes:
    out = bytearray(len(data))
    for off in range(0, len(data), 64):
        ks = _chacha_block(key, counter + off // 64, nonce)
        chunk = data[off:off + 64]
        for i, b in enumerate(chunk):
            out[off + i] = b ^ ks[i]
    return bytes(out)


# --- Poly1305 (RFC 8439) ---

def _poly1305(key: bytes, msg: bytes) -> bytes:
    r = int.from_bytes(key[:16], "little") & 0x0FFFFFFC0FFFFFFC0FFFFFFC0FFFFFFF
    s = int.from_bytes(key[16:32], "little")
    p = (1 << 130) - 5
    acc = 0
    for off in range(0, len(msg), 16):
        block = msg[off:off + 16]
        n = int.from_bytes(block + b"\x01", "little")  # append the 1 bit
        acc = ((acc + n) * r) % p
    acc = (acc + s) & ((1 << 128) - 1)
    return acc.to_bytes(16, "little")


def _pad16(b: bytes) -> bytes:
    return b"\x00" * ((16 - len(b) % 16) % 16)


# --- ChaCha20-Poly1305 AEAD (RFC 8439 section 2.8) ---

def aead_encrypt(key: bytes, nonce: bytes, plaintext: bytes,
                 aad: bytes = b"") -> bytes:
    """Return ciphertext || 16-byte Poly1305 tag."""
    if len(key) != AEAD_KEY_BYTES or len(nonce) != AEAD_NONCE_BYTES:
        raise ValueError("bad key or nonce length")
    poly_key = _chacha_block(key, 0, nonce)[:32]   # counter 0 derives the MAC key
    ct = _chacha20(key, 1, nonce, plaintext)       # counter 1+ encrypts
    mac_data = (aad + _pad16(aad) + ct + _pad16(ct)
                + struct.pack("<Q", len(aad)) + struct.pack("<Q", len(ct)))
    tag = _poly1305(poly_key, mac_data)
    return ct + tag


def aead_decrypt(key: bytes, nonce: bytes, ciphertext: bytes,
                 aad: bytes = b"") -> bytes:
    """Verify the tag and return plaintext, or raise. Fail-closed."""
    if len(key) != AEAD_KEY_BYTES or len(nonce) != AEAD_NONCE_BYTES:
        raise ValueError("bad key or nonce length")
    if len(ciphertext) < TAG_BYTES:
        raise ValueError("ciphertext too short to carry a tag")
    ct, tag = ciphertext[:-TAG_BYTES], ciphertext[-TAG_BYTES:]
    poly_key = _chacha_block(key, 0, nonce)[:32]
    mac_data = (aad + _pad16(aad) + ct + _pad16(ct)
                + struct.pack("<Q", len(aad)) + struct.pack("<Q", len(ct)))
    expect = _poly1305(poly_key, mac_data)
    if not hmac.compare_digest(expect, tag):       # constant-time compare
        raise ValueError("AEAD authentication failed (fail-closed, SP-1)")
    return _chacha20(key, 1, nonce, ct)


# --- key derivation and the SP-1 belt ---

def _hkdf_blake2s(key: bytes, info: bytes, length: int = 32) -> bytes:
    """HKDF-BLAKE2s, suite 0x01 -- the same construction rendezvous.py uses.
    Duplicated here only to keep e2e importable without a rendezvous cycle."""
    prk = hmac.new(b"\x00" * 32, key, "blake2s").digest()
    out, t, i = b"", b"", 1
    while len(out) < length:
        t = hmac.new(prk, t + info + bytes([i]), "blake2s").digest()
        out += t
        i += 1
    return out[:length]


def content_key(kpair: bytes) -> bytes:
    """Derive the end-to-end AEAD key from the pre-shared pair secret.

    Label-separated from the SP-7 tag key (info=b"tag" in the card) and from
    the box-id key, so one PRK-family governs the relationship with no two
    uses sharing a derived key (the 1.4 KDF-discipline direction).
    """
    return _hkdf_blake2s(kpair, b"e2e-content", AEAD_KEY_BYTES)


def _widen_nonce(msg_nonce: bytes) -> bytes:
    if len(msg_nonce) != MSG_NONCE_BYTES:
        raise ValueError(f"msg_nonce must be {MSG_NONCE_BYTES} bytes")
    return b"\x00" * (AEAD_NONCE_BYTES - MSG_NONCE_BYTES) + msg_nonce


# The AEAD adds a 16-byte tag, so the plaintext a single packet can carry is
# the dispersal layer's share-payload budget (dispersal.MAX_MESSAGE) minus the
# tag. A sender MUST fragment above this at a higher layer (SP-8). Kept as a
# bare integer here so e2e.py stays importable without a dispersal cycle;
# dispersal.MAX_MESSAGE == 1790 (SHARE_BYTES - 2), checked by the tests.
MAX_PLAINTEXT = 1790 - TAG_BYTES   # == 1774 bytes


def seal(kpair: bytes, msg_nonce: bytes, plaintext: bytes) -> bytes:
    """SP-1 sender side: plaintext -> end-to-end ciphertext, ready to disperse.

    The ciphertext is what Shamir then splits. Below k shares it is
    unconditionally hidden (the floor); at or above k shares it is this AEAD
    under a key no below-k adversary ever sees. The msg_nonce binds this layer
    to the SP-7 tag that will mark the shares. A plaintext longer than
    MAX_PLAINTEXT belongs to a fragment above this layer (SP-8); the pad step
    in dispersal raises ValueError if it is exceeded.
    """
    key = content_key(kpair)
    return aead_encrypt(key, _widen_nonce(msg_nonce), plaintext)


def open_(kpair: bytes, msg_nonce: bytes, ciphertext: bytes) -> bytes:
    """SP-1 recipient side: reconstructed ciphertext -> plaintext, or raise.

    Called after dispersal has reassembled the ciphertext from k shares. A
    corrupted or forged reconstruction fails the Poly1305 tag and raises
    rather than returning garbage -- the fail-closed behaviour 0.3 relies on.
    """
    key = content_key(kpair)
    return aead_decrypt(key, _widen_nonce(msg_nonce), ciphertext)


if __name__ == "__main__":
    import secrets

    # RFC 8439 section 2.8.2 known-answer test: proves this pure-Python AEAD
    # is the real ChaCha20-Poly1305, not a look-alike.
    kat_key = bytes(range(0x80, 0xA0))
    kat_nonce = bytes.fromhex("070000004041424344454647")
    kat_aad = bytes.fromhex("50515253c0c1c2c3c4c5c6c7")
    kat_pt = (b"Ladies and Gentlemen of the class of '99: If I could offer you "
              b"only one tip for the future, sunscreen would be it.")
    kat = aead_encrypt(kat_key, kat_nonce, kat_pt, kat_aad)
    expect_ct = bytes.fromhex(
        "d31a8d34648e60db7b86afbc53ef7ec2a4aded51296e08fea9e2b5a736ee62d6"
        "3dbea45e8ca9671282fafb69da92728b1a71de0a9e060b2905d6a5b67ecd3b36"
        "92ddbd7f2d778b8c9803aee328091b58fab324e4fad675945585808b4831d7bc"
        "3ff4def08e4b7a9de576d26586cec64b6116")
    expect_tag = bytes.fromhex("1ae10b594f09e26a7e902ecbd0600691")
    assert kat == expect_ct + expect_tag, "ChaCha20-Poly1305 KAT mismatch"
    print("AEAD: RFC 8439 known-answer vector matches -- real ChaCha20-Poly1305")

    # The SP-1 belt round-trips, and tampering fails closed.
    kpair = secrets.token_bytes(32)
    nonce = (42).to_bytes(8, "big")
    pt = b"encrypt before you disperse"
    ct = seal(kpair, nonce, pt)
    assert open_(kpair, nonce, ct) == pt
    bad = bytearray(ct); bad[0] ^= 1
    try:
        open_(kpair, nonce, bytes(bad))
        raise SystemExit("tamper went undetected -- SP-1 belt is broken")
    except ValueError:
        pass
    print("SP-1 belt: seal -> open round-trips; a flipped ciphertext bit "
          "fails closed (no plaintext returned)")
