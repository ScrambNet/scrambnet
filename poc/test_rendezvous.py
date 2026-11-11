"""Tests for the rendezvous PoC. Run: python3 test_rendezvous.py"""

import json
import pathlib
import secrets
import unittest

import dispersal as d
import rendezvous as rz

T0 = 1_767_000_000.0


def make_card(n_drops=4):
    drops = [rz.Drop(f"drop{i}") for i in range(n_drops)]
    return rz.Card(secrets.token_bytes(32), secrets.token_bytes(32), drops)


class Derivations(unittest.TestCase):
    def test_box_ids_distinct_per_drop_and_epoch(self):
        card = make_card()
        e = rz.epoch_of(T0)
        ids = {card.box_id(i, e) for i in range(4)}
        ids |= {card.box_id(i, e + 1) for i in range(4)}
        self.assertEqual(len(ids), 8)  # RZ-3/RZ-10: no collisions anywhere

    def test_two_cards_unlinkable(self):
        # RZ-2: same recipient, two correspondents, nothing in common.
        rid = secrets.token_bytes(32)
        a = rz.Card(rid, secrets.token_bytes(32), [])
        b = rz.Card(rid, secrets.token_bytes(32), [])
        self.assertNotEqual(a.k_tag, b.k_tag)
        self.assertNotEqual(a.box_id(0, 1), b.box_id(0, 1))

    def test_hkdf_deterministic(self):
        k = bytes(32)
        self.assertEqual(rz.hkdf_blake2s(k, b"tag"), rz.hkdf_blake2s(k, b"tag"))
        self.assertNotEqual(rz.hkdf_blake2s(k, b"tag"), rz.hkdf_blake2s(k, b"box"))


class Slots(unittest.TestCase):
    def test_slot_roundtrip(self):
        tag = secrets.token_bytes(d.TAG_BYTES)
        share = secrets.token_bytes(d.SHARE_BYTES)
        s = rz.build_slot(tag, 2, 4, 3, share)
        self.assertEqual(len(s), rz.SLOT_BYTES)
        self.assertEqual(rz.parse_slot(s), (tag, 2, 3, 4, share))

    def test_deposit_plus_boxid_is_delta_sized(self):
        # RZ-6: box_id || slot fills delta exactly.
        self.assertEqual(rz.BOX_ID_BYTES + rz.SLOT_BYTES, d.DELTA_BYTES)


class DropBehaviour(unittest.TestCase):
    def test_retrieve_always_fixed_size(self):
        drop = rz.Drop()
        self.assertEqual(len(drop.retrieve(T0, secrets.token_bytes(16))), rz.B_SLOTS)
        # RZ-9: dummies are format-identical to real slots.
        for slot in drop.retrieve(T0, secrets.token_bytes(16)):
            self.assertEqual(len(slot), rz.SLOT_BYTES)

    def test_deposit_silent_on_garbage(self):
        drop = rz.Drop()
        drop.deposit(T0, b"short")                 # RZ-7: no exception, no state
        drop.deposit(T0, secrets.token_bytes(10))
        self.assertEqual(drop.boxes, {})

    def test_cap_eviction_oldest_first(self):
        drop = rz.Drop()
        box = secrets.token_bytes(16)
        first = rz.build_slot(secrets.token_bytes(16), 1, 4, 3,
                              secrets.token_bytes(d.SHARE_BYTES))
        drop.deposit(T0, box + first)
        for _ in range(rz.BOX_CAP):
            drop.deposit(T0, box + rz.build_slot(secrets.token_bytes(16), 1, 4, 3,
                                                 secrets.token_bytes(d.SHARE_BYTES)))
        self.assertEqual(len(drop.boxes[box]), rz.BOX_CAP)
        self.assertNotIn(first, [s for _, s in drop.boxes[box]])

    def test_expiry_by_epoch(self):
        drop = rz.Drop()
        box = secrets.token_bytes(16)
        drop.deposit(T0, box + rz.build_slot(secrets.token_bytes(16), 1, 4, 3,
                                             secrets.token_bytes(d.SHARE_BYTES)))
        later = T0 + (rz.SLOT_TTL_EPOCHS + 1) * rz.EPOCH_SECONDS
        drop.retrieve(later, box)                  # retrieval triggers expiry
        self.assertEqual(drop.boxes, {})


class EndToEnd(unittest.TestCase):
    def test_roundtrip_with_one_dead_drop(self):
        card = make_card()
        msg = secrets.token_bytes(300)
        nonce = (5).to_bytes(8, "big")
        rz.deposit_message(card, msg, nonce, T0)
        card.drops[2].boxes.clear()
        window = [i.to_bytes(8, "big") for i in range(8)]
        self.assertEqual(rz.poll_all(card, T0 + 60, window), {nonce: msg})

    def test_wrong_card_sees_nothing(self):
        card = make_card()
        msg = secrets.token_bytes(100)
        rz.deposit_message(card, msg, (1).to_bytes(8, "big"), T0)
        stranger = rz.Card(secrets.token_bytes(32), secrets.token_bytes(32),
                           card.drops)
        window = [i.to_bytes(8, "big") for i in range(8)]
        self.assertEqual(rz.poll_all(stranger, T0 + 60, window), {})

    def test_schedule_within_bounds(self):
        times = rz.poll_schedule(T0, T0 + 6 * 3600)
        gaps = [b - a for a, b in zip(times, times[1:])]
        self.assertTrue(all(rz.POLL_PERIOD - rz.POLL_JITTER <= g <=
                            rz.POLL_PERIOD + rz.POLL_JITTER for g in gaps))


class Vectors(unittest.TestCase):
    def setUp(self):
        here = pathlib.Path(__file__).resolve().parent
        self.v = json.loads((here / "vectors.json").read_text())["rendezvous"]

    def test_derivations(self):
        kpair = bytes.fromhex(self.v["kpair"])
        card = rz.Card(bytes(32), kpair, [])
        self.assertEqual(card.k_tag.hex(), self.v["k_tag"])
        for key, expect in self.v["box_ids"].items():
            drop_index, epoch = (int(x) for x in key.split("_"))
            self.assertEqual(card.box_id(drop_index, epoch).hex(), expect)


if __name__ == "__main__":
    unittest.main(verbosity=2)
