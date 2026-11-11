# ScrambNet Specification — Part 6: Rendezvous and Delivery

**Status: DRAFT.** Strawman values marked `(s)`. The retrieval-metadata and
economics questions this part opens are OP-9 and deliberately unresolved.

## 1. Scope

How a message reaches someone who is not — and must not be — in anyone's map.
Recipients do not have network locations; they have **contact cards** and
**dead drops**. The sender deposits shares; the recipient retrieves them from
behind its own circuits. Nobody ever delivers *to* a person.

## 2. Nobody gossips about people

- **RZ-1.** A recipient MUST NOT be discoverable through gossip. Only relays
  publish records (Part 2). Anything that makes a person's participation
  queryable is a defect (compare L0: there is no list of users because there
  is no moment at which a user signs up).

## 3. Contact cards

- **RZ-2.** A contact card is **per relationship**: the card given to
  correspondent A MUST be unlinkable to the card given to correspondent B —
  distinct pair key, distinct boxes. Compromise of one correspondent exposes
  one relationship, not the recipient's world.
- **RZ-3.** Card contents (canonical CBOR, like Part 2):

| Key | Name | Type | Notes |
|---|---|---|---|
| 0 | `v` | uint | format version, `1` |
| 1 | `id` | bytes(32) | recipient Ed25519 identity key |
| 2 | `kpair` | bytes(32) | pair secret; everything below derives from it |
| 3 | `drops` | array | `d` embedded relay records (full Part 2 records) |
| 4 | `validity` | uint | unix expiry; SHOULD track the embedded records' expiry |

  Derivations (HKDF-BLAKE2s, suite 0x01): the SP-7 tag key for this pair is
  `K_tag = HKDF(kpair, "tag")`; box identifiers are
  `box_id(epoch) = PRF(kpair, "box" ‖ epoch)` truncated to 16 bytes, with
  `epoch = floor(unix_time / 86400)` (s).
- **RZ-4.** Cards travel out of band (QR code, printed string, a friend) or
  over an existing ScrambNet channel. One contact is the floor, as in GR-10.

## 4. Drops and deposit

- **RZ-5.** The drop set holds `d = n = 4` (s) relays, chosen by the
  *recipient*, which SHOULD be mutually independent in the same sense path
  selection demands (OP-1 applies to drops too). The `n` shares of one message
  MUST be deposited at `n` distinct drops — SP-7 extended to storage: no
  single drop ever holds two shares of anything.
- **RZ-6.** A deposit is an ordinary Part 1 packet whose circuit ends at the
  drop. The final-hop plaintext of `delta` is `box_id` (16 B) ‖ `slot`
  (1840 B); the slot is the Part 1 §4 share payload with its trailing pad
  16 bytes shorter. The drop stores the slot under `box_id` verbatim: it can
  read neither tag semantics nor share content (one share < `k`, and SP-7
  makes shares mutually unlinkable even across colluding drops).
- **RZ-7.** Deposits are fire-and-forget. The drop MUST NOT emit any response
  that distinguishes success, unknown box, or full box (silent uniformity, as
  GR-4). Storage rules: fixed slots of 1840 B, at most `64` (s) slots per box,
  slot expiry `7` days (s), oldest-first eviction.

## 5. Retrieval

- **RZ-8.** The recipient polls each of its drops over its own circuits.
  Knowledge of `box_id` authorizes retrieval (it is secret-derived and
  unguessable); slots are deleted on expiry, not on fetch (deletion-on-fetch
  semantics are OP-9 territory: an adversary who steals a `box_id` must not be
  able to silently eat mail).
- **RZ-9 (polling discipline).** Polling MUST follow a schedule independent of
  user activity: fixed cadence with jitter (strawman: every `15` minutes ±
  uniform `5`), continuing when the user is idle, with decoy polls to decoy
  box ids at the same cadence. A retrieval response is always exactly `b = 8`
  (s) slots, padded with dummy slots indistinguishable from real ones. The
  drop learns a box's polling cadence and deposit times within one epoch —
  that is the designed residual, bounded by RZ-10 and attacked in OP-9.
- **RZ-10 (epochs).** `box_id` rotates per epoch. A drop MUST NOT be able to
  link the same pair's boxes across epochs; nothing in the retrieval protocol
  may carry a value stable across epochs.

## 6. Refresh and failure

- **RZ-11.** A card is renewed in-band: the recipient deposits the next card
  (new `kpair`, new drops) into the pair's existing boxes as an ordinary
  message, before `validity` runs out. If every drop of a pair is dead or the
  card has expired, the pair re-exchanges out of band: one contact is the
  floor, again.
- **RZ-12.** Anyone holding a card can fill its boxes. The per-box cap (RZ-7)
  bounds flooding damage to one relationship; deposit pricing (client
  puzzles?) and drop storage economics are open (OP-9).

## 7. What this part does not decide

Retrieval metadata minimization (smarter-than-polling retrieval, PIR-style
tricks and their real costs), deletion semantics, deposit pricing, drop
incentives (OP-9); drop-set independence verification (OP-1); polling over
the mesh during blackout (OP-6). Numbered issues exist for each.
