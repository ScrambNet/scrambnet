# ScrambNet Specification — Part 1: Share Packet

**Status: DRAFT.** Strawman sizes are marked `(s)`. Attack them by requirement number.

## 1. Scope

The share packet is the only unit that crosses the overlay: it carries one share of
one message through one onion circuit. Everything in this part serves two goals:
the unconditional floor (I-2) and wire uniformity (I-4).

## 2. Layering

```
plaintext message
  └─ end-to-end AEAD (recipient keys)            [computational]
       └─ Shamir split: n shares, threshold k    [unconditional floor]
            └─ per-share onion encryption, own circuit, Sphinx format
                 └─ chameleon transport (Part 4)
```

- **SP-1.** The sender MUST apply end-to-end encryption *before* dispersal, and
  dispersal MUST be applied to the end-to-end ciphertext. With fewer than `k`
  shares the adversary learns nothing about the ciphertext unconditionally
  (Shamir); with `k` or more shares it still faces the end-to-end AEAD. The
  unconditional floor and the computational belt compose; neither replaces the
  other.
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
- **SP-8.** A message that does not fill `k × share` bytes MUST be padded before
  splitting; a message that exceeds it is fragmented at a layer above this one
  (fragmentation design TBD, interacts with OP-4).
- **SP-9 (timing).** The sender MUST NOT emit the `n` shares as a simultaneous
  burst. Shares SHOULD be emitted with randomized per-share delay; the
  distribution and its cost on latency are OP-4 and unresolved. Clients MAY
  emit decoy shares (packets with random `tag`) at a configurable rate.

## 5. What this part does not decide

Path selection and disjointness enforcement (OP-1), mix parameters (OP-5),
fragmentation (SP-8), decoy economics (SP-9) are open on purpose. Each has a
numbered issue; argue there, with numbers.
