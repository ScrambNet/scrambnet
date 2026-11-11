# ScrambNet Specification — Part 1: Share Packet

**Status: DRAFT.** Strawman sizes are marked `(s)`. Attack them by requirement number.

## 1. Scope

The share packet is the only unit that crosses the overlay: it carries one share of
one message through one onion circuit. Everything in this part serves two goals:
the unconditional floor (I-2) and wire uniformity (I-4).

## 2. Layering

```
plaintext message
  └─ end-to-end AEAD (pre-shared pair key, SP-1a)  [computational]
       └─ Shamir split: n shares, threshold k      [unconditional floor]
            └─ per-share onion encryption, own circuit, Sphinx format
                 └─ chameleon transport (Part 4)
```

- **SP-1.** The sender MUST apply end-to-end encryption *before* dispersal, and
  dispersal MUST be applied to the end-to-end ciphertext. With fewer than `k`
  shares the adversary learns nothing about the ciphertext unconditionally
  (Shamir); with `k` or more shares it still faces the end-to-end AEAD. The
  unconditional floor and the computational belt compose; neither replaces the
  other. The belt is demonstrated end to end in `poc/e2e.py`
  (encrypt → split → reconstruct → decrypt, fail-closed on tamper).
- **SP-1a (content-key establishment, and the post-quantum consequence).**
  The end-to-end AEAD key MUST be derived from the **pre-shared symmetric pair
  secret** `kpair` carried by the contact card (Part 6, RZ-2), by a
  label-separated KDF: `content_key = HKDF-BLAKE2s(kpair, "e2e-content")`,
  distinct from the SP-7 tag key and the box-id key derived from the same
  `kpair`. There MUST be no asymmetric key agreement in the content path. This
  is a deliberate choice with a load-bearing consequence: a `≥k`,
  record-everything adversary with a future large-scale quantum computer still
  cannot read content, because there is no Diffie-Hellman transcript for Shor
  to break — only a symmetric secret the parties already share, and Grover
  costs the AEAD at most a halving of its key strength (hence a ≥256-bit
  derived key is RECOMMENDED where margin matters). "Harvest now, decrypt
  later" is therefore defeated at **both** tiers: below `k` by Shamir
  (unconditional), at or above `k` by a symmetric AEAD under a pre-shared key
  (no public-key assumption to harvest). The honest cost is the **bootstrap**:
  `kpair` must first reach the recipient over a prior confidential channel (the
  out-of-band contact-card exchange, Part 6). Any residual public-key or PQ-KEM
  assumption lives there, in the card exchange — not in the content path — and
  carrying a card exchange that is itself post-quantum is an orthogonal,
  layered choice, not a precondition for the floor. The AEAD suite is
  ChaCha20-Poly1305 (suite `0x01`); `msg_nonce` (SP-7) is the AEAD nonce, which
  binds the two layers and makes a reused nonce doubly fatal (SP-7 tag
  collision *and* AEAD confidentiality loss — see SP-7).
- **SP-2.** Default dispersal parameters for messaging: `n = 4`, `k = 3` (s).
  Bulk transfer profiles MAY use Rabin IDA instead of Shamir, and MUST be
  labeled as computational in the client UI, because IDA has no unconditional
  floor (OP-3).

## 3. Wire format

- **SP-3.** Every packet on every link MUST be exactly `P = 2048` bytes (s).
- **SP-4.** Every byte of the packet MUST be indistinguishable from uniform
  random to an observer without the relevant keys, at every hop (Sphinx
  property; I-4). In particular there is no cleartext version, suite, length,
  hop counter, or share index.

Layout (sizes strawman, 3-hop maximum):

| Field | Size (s) | Visible to |
|---|---|---|
| `alpha` — Sphinx group element (X25519) | 32 B | everyone (uniform) |
| `beta` — Sphinx routing info, 3 × 48 B, padded | 144 B | peeled per hop |
| `gamma` — per-hop MAC | 16 B | current hop |
| `delta` — payload, AEAD-wrapped per hop | 1856 B | exit → recipient leg |

- **SP-5.** Relays MUST maintain a replay cache of seen `gamma` values per key
  epoch and MUST drop replays silently (standard Sphinx replay defense).
- **SP-6.** Relays MUST emit packets in constant-size batches with
  implementation-defined jitter in fast mode, and MUST follow the mix strategy
  (stop-and-go or Poisson mix, TBD) in paranoid mode. The strategy choice is
  OP-5 territory and deliberately unresolved here.

## 4. Share payload (inside `delta`, end of the circuit)

Decrypted by the recipient only:

| Field | Size (s) | Notes |
|---|---|---|
| `tag` | 16 B | recipient-keyed PRF tag, see SP-7 |
| `index` | 1 B | share index `1..n` |
| `params` | 1 B | packed `k`, `n` (4 bits each) |
| `share` | 1792 B | Shamir share bytes |
| `pad` | rest | random |

- **SP-7 (no cross-path linkability).** Two shares of the same message MUST NOT
  carry any equal or correlatable value observable by anyone except the
  recipient. Share-set membership is signaled only by `tag`:
  `tag = PRF(K_r, msg_nonce ‖ index)` where `K_r` is a recipient-held key and
  `msg_nonce` is carried inside the end-to-end layer. An exit relay, or a
  coalition of exits, MUST NOT be able to tell whether two packets belong to
  the same message. This requirement is load-bearing: without it, dispersal
  degrades into an enumeration convenience for the adversary.
- **SP-7a (share integrity: accepted fail-closed residual).** The `tag` says
  *which* message a packet claims to belong to; it does **not** authenticate
  the `share` bytes or the `params` (`k,n`) byte. Shamir reconstruction has no
  integrity of its own, so a hostile drop or exit that flips bits in one share
  — or lies about `k,n` — yields a consistent-but-wrong plaintext candidate
  that Shamir cannot detect. This is **caught one layer up**: the end-to-end
  AEAD (SP-1a) fails its tag on any corrupted reconstruction and the recipient
  discards the message rather than acting on garbage (demonstrated in
  `poc/dispersal.py`, test `test_tampered_share_fails_closed`). The residual is
  therefore **not a confidentiality loss but a targeted denial of service**: a
  single malicious vantage point on one of the `n` share paths can make a
  specific message fail to reconstruct, at the cost of one flipped bit. The
  verdict for this draft is to **accept and document** that residual rather
  than add a per-share MAC, for two reasons: (1) a per-share authenticator
  would spend payload bytes and introduce a second key to manage without
  removing the DoS — a drop that can corrupt a share can equally *drop* it, and
  `n−k` such losses are already tolerated by design; (2) the AEAD already makes
  the failure safe (fail-closed), so the open question is availability, not
  secrecy. The honest mitigations are redundancy (`n−k` margin), path
  disjointness so no single vantage point sits on `k` of the `n` paths (OP-1),
  and retry over fresh paths. A future revision MAY add an optional per-share
  binding for availability-critical profiles; it is deliberately not mandated
  here. `k,n` is vector-locked (nibble order, Part 3 §3.2 vectors) so an
  implementation cannot *accidentally* disagree, only a malicious party can lie.
- **SP-7b (no equal tag across colluding drops, and nonce ownership).** The
  property that must hold: no two packets a coalition of drops can see carry an
  equal `tag` unless the sender reused a `(msg_nonce, index)` pair. *Argument:*
  `tag = PRF(K_r, msg_nonce ‖ index)` with `msg_nonce` a fixed 8 bytes and
  `index` a fixed 1 byte, so the PRF input is an unambiguous fixed-width
  encoding of `(msg_nonce, index)` — the map `(msg_nonce, index) ↦ input` is
  injective. A keyed BLAKE2s PRF gives equal outputs only on equal inputs
  (bar a ~`2^-128` collision), so equal tags imply an equal `(msg_nonce, index)`.
  The `n` shares of one message share one `msg_nonce` but use *distinct* indices
  `1..n`, hence distinct inputs, hence distinct tags: a coalition of drops
  cannot tell two shares of one message apart from two unrelated packets. Two
  *different* messages collide a tag only if they reuse a `msg_nonce`.
  Therefore **nonce ownership is a MUST**: a sender MUST NOT reuse a
  `msg_nonce` under one `kpair`. Reuse is doubly fatal — it collides SP-7 tags
  (making a share set linkable) *and*, because `msg_nonce` is the AEAD nonce
  (SP-1a), it destroys ChaCha20-Poly1305 confidentiality (a two-time pad, pinned
  by `test_nonce_reuse_is_detectable_catastrophe`). A strictly increasing
  per-`kpair` message counter satisfies this; the counter's high-water mark MUST
  survive restarts. At the storage layer, a drop MUST drop a redeposit of an
  already-stored `(box_id, slot)` (replay) and evicts oldest-first under the
  per-box cap (RZ-7), so a replayed deposit neither multiplies nor displaces
  honest mail beyond the declared cap.
- **SP-8.** A message that does not fill the share payload (`1792` bytes, less
  the 2-byte length prefix) MUST be padded with random bytes before splitting;
  a message that exceeds it is fragmented at a layer above this one
  (fragmentation design TBD, interacts with OP-4). Shamir's honest price: every
  share is as long as the secret, so an (n, k) dispersal transmits ×`n` the
  ciphertext volume (OP-3).
- **SP-9 (timing).** The sender MUST NOT emit the `n` shares as a simultaneous
  burst. Shares SHOULD be emitted with randomized per-share delay; the
  distribution and its cost on latency are OP-4 and unresolved. Clients MAY
  emit decoy shares (packets with random `tag`) at a configurable rate.

## 5. What this part does not decide

Path selection and disjointness enforcement (OP-1), mix parameters (OP-5),
fragmentation (SP-8), decoy economics (SP-9) are open on purpose. Each has a
numbered issue; argue there, with numbers.
