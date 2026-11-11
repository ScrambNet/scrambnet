"""ScrambNet rendezvous -- reference implementation (DRAFT).

Executable companion to docs/spec/06-rendezvous.md. Pure Python 3 standard
library. Requirements implemented here are cited by number (RZ-n); sizes come
from Part 1 via dispersal.py.

NOT PRODUCTION CODE. Drops are in-process objects and time is a parameter:
this file demonstrates the protocol's *shape* -- what a drop stores, what it
can observe, what the recipient does -- not a deployment. Canonical CBOR
encoding of cards is out of scope here (no dependencies by policy).
"""

import hashlib
import hmac
import secrets

import dispersal as d

SLOT_BYTES = 1840        # RZ-6: delta minus the 16-byte box id
BOX_ID_BYTES = 16
B_SLOTS = 8              # RZ-9 (s): retrieval always returns exactly this many
BOX_CAP = 64             # RZ-7 (s): slots per box, oldest-first eviction
SLOT_TTL_EPOCHS = 7      # RZ-7 (s): expiry, with epoch = one day
EPOCH_SECONDS = 86400    # RZ-3 (s)
POLL_PERIOD = 900        # RZ-9 (s): poll every 15 min ...
POLL_JITTER = 300        # ... plus/minus uniform 5 min


def hkdf_blake2s(key: bytes, info: bytes, length: int = 32) -> bytes:
    """HKDF (RFC 5869) with HMAC-BLAKE2s, suite 0x01. Zero-filled salt."""
    prk = hmac.new(b"\x00" * 32, key, "blake2s").digest()
    out, t, i = b"", b"", 1
    while len(out) < length:
        t = hmac.new(prk, t + info + bytes([i]), "blake2s").digest()
        out += t
        i += 1
    return out[:length]


def epoch_of(unix_time: float) -> int:
    return int(unix_time // EPOCH_SECONDS)


class Card:
    """RZ-2/RZ-3: per-relationship contact card (encoding out of PoC scope).

    Everything derives from kpair. The drop index MUST enter the box
    derivation: with one id per epoch, two colluding drops could link the
    pair's boxes within that epoch.
    """

    def __init__(self, recipient_id: bytes, kpair: bytes, drops: list):
        self.recipient_id = recipient_id
        self.kpair = kpair
        self.drops = drops                      # RZ-5: chosen by the recipient
        self.k_tag = hkdf_blake2s(kpair, b"tag")   # the SP-7 key for this pair

    def box_id(self, drop_index: int, epoch: int) -> bytes:
        """RZ-3/RZ-10: per-drop, per-epoch rotating box identifier."""
        msg = b"box" + bytes([drop_index]) + epoch.to_bytes(8, "big")
        return hashlib.blake2s(msg, key=self.kpair,
                               digest_size=BOX_ID_BYTES).digest()


# --- slot: the Part 1 section 4 share payload, pad 16 bytes shorter (RZ-6) ---

def build_slot(tag: bytes, index: int, n: int, k: int, share: bytes) -> bytes:
    body = tag + bytes([index]) + bytes([(k << 4) | n]) + share
    return body + secrets.token_bytes(SLOT_BYTES - len(body))


def parse_slot(slot: bytes) -> tuple[bytes, int, int, int, bytes]:
    tag = slot[:d.TAG_BYTES]
    index = slot[d.TAG_BYTES]
    params = slot[d.TAG_BYTES + 1]
    share = slot[d.TAG_BYTES + 2:d.TAG_BYTES + 2 + d.SHARE_BYTES]
    return tag, index, params >> 4, params & 0x0F, share


class Drop:
    """A relay in the drop role. It stores what it cannot read, answers in
    fixed sizes, and keeps the only log it could ever keep -- which is
    exactly the OP-9 residual, printed by the demo below."""

    def __init__(self, name: str = "drop"):
        self.name = name
        self.boxes: dict[bytes, list[tuple[int, bytes]]] = {}
        self.log: list[tuple] = []              # what this vantage point sees

    def deposit(self, now: float, plaintext: bytes) -> None:
        """RZ-6/RZ-7: fire-and-forget; no response of any kind."""
        if len(plaintext) != BOX_ID_BYTES + SLOT_BYTES:
            return                              # silent, as every failure
        box, slot = plaintext[:BOX_ID_BYTES], plaintext[BOX_ID_BYTES:]
        self.log.append(("deposit", int(now), box.hex()[:8]))
        q = self.boxes.setdefault(box, [])
        q.append((epoch_of(now), slot))
        if len(q) > BOX_CAP:
            q.pop(0)                            # RZ-7: oldest-first eviction

    def retrieve(self, now: float, box_id: bytes) -> list[bytes]:
        """RZ-8/RZ-9: knowledge of box_id authorizes; the answer is always
        exactly B_SLOTS slots, dummies indistinguishable from real ones."""
        self.log.append(("poll", int(now), box_id.hex()[:8]))
        self._expire(now)
        real = [s for (_, s) in self.boxes.get(box_id, [])][:B_SLOTS]
        out = real + [secrets.token_bytes(SLOT_BYTES)
                      for _ in range(B_SLOTS - len(real))]
        secrets.SystemRandom().shuffle(out)
        return out

    def _expire(self, now: float) -> None:
        cut = epoch_of(now) - SLOT_TTL_EPOCHS   # RZ-8: expiry, not fetch,
        for box in list(self.boxes):            # deletes slots
            kept = [(e, s) for (e, s) in self.boxes[box] if e > cut]
            if kept:
                self.boxes[box] = kept
            else:
                del self.boxes[box]


# --- sender and recipient, rendezvous layer only ---

def deposit_message(card: Card, msg: bytes, msg_nonce: bytes, now: float,
                    n: int = 4, k: int = 3) -> None:
    """RZ-5/RZ-6: one share per drop, n distinct drops. Emission timing
    (SP-9) and the circuits to each drop (OP-1) are outside this module."""
    shares = d.split(d.pad(msg), n, k)
    epoch = epoch_of(now)
    for i, share in enumerate(shares):
        slot = build_slot(d.share_tag(card.k_tag, msg_nonce, i + 1),
                          i + 1, n, k, share)
        card.drops[i].deposit(now, card.box_id(i, epoch) + slot)


def poll_all(card: Card, now: float, nonce_window: list[bytes]) -> dict[bytes, bytes]:
    """RZ-9: one fixed-size retrieval per drop; recognition by SP-7 tags,
    exactly as on the wire -- a dummy slot simply matches no expected tag."""
    expected = {d.share_tag(card.k_tag, nonce, i): (nonce, i)
                for nonce in nonce_window for i in range(1, 16)}
    groups: dict[bytes, dict[int, tuple[int, bytes]]] = {}
    epoch = epoch_of(now)
    for i, drop in enumerate(card.drops):
        for slot in drop.retrieve(now, card.box_id(i, epoch)):
            tag, index, k, n, share = parse_slot(slot)
            hit = expected.get(tag)
            if hit is None or hit[1] != index:
                continue
            groups.setdefault(hit[0], {})[index] = (k, share)
    done = {}
    for nonce, got in groups.items():
        k = next(iter(got.values()))[0]
        if len(got) >= k:
            use = {x: s for x, (_, s) in sorted(got.items())[:k]}
            done[nonce] = d.unpad(d.reconstruct(use))
    return done


def poll_schedule(start: float, end: float) -> list[float]:
    """RZ-9: fixed cadence with jitter, independent of user activity."""
    rng = secrets.SystemRandom()
    t, out = start, []
    while t < end:
        out.append(t)
        t += POLL_PERIOD + rng.uniform(-POLL_JITTER, POLL_JITTER)
    return out


if __name__ == "__main__":
    t0 = 1_767_000_000.0
    drops = [Drop(f"drop{i}") for i in range(4)]
    card = Card(secrets.token_bytes(32), secrets.token_bytes(32), drops)

    # The recipient polls on schedule whether or not anything is coming.
    msg = b"meet where the buses cross"
    nonce = (1).to_bytes(8, "big")
    window = [i.to_bytes(8, "big") for i in range(8)]
    deposited = False
    got = {}
    for t in poll_schedule(t0, t0 + 4 * 3600):
        if not deposited and t > t0 + 2 * 3600:   # mail arrives mid-schedule
            deposit_message(card, msg, nonce, t - 60)
            drops[1].boxes.clear()                # and one drop loses its disk
            deposited = True
        got |= poll_all(card, t, window)
    assert got == {nonce: msg}
    print("round trip: 4 drops, 1 lost its storage, message reconstructed "
          "from any 3 (overhead x4, as declared)")

    # What the drop saw: the OP-9 residual, and nothing else.
    polls = [e for e in drops[0].log if e[0] == "poll"]
    gaps = [int(b[1] - a[1]) for a, b in zip(polls, polls[1:])]
    print(f"drop0 log: {len(polls)} polls, gaps {min(gaps)}-{max(gaps)}s "
          "(same cadence before and after mail existed: nothing to profile "
          "but the cadence itself -- OP-9)")

    # Unlinkability of boxes across drops and across epochs (RZ-3/RZ-10).
    e = epoch_of(t0)
    assert card.box_id(0, e) != card.box_id(1, e)
    assert card.box_id(0, e) != card.box_id(0, e + 1)
    print("box ids: distinct per drop and rotated per epoch -- colluding "
          "drops cannot link the pair, yesterday cannot name today")
