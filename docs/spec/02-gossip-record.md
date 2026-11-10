# ScrambNet Specification — Part 2: Gossip Record

**Status: DRAFT.** Strawman values marked `(s)`. The sybil/eclipse questions this
part leans on are OP-2 and deliberately open.

## 1. Scope

The gossip record is the self-signed descriptor by which a relay exists. There is
no directory, no authority, no registration (I-3): a relay is the set of records
it signs, and the network's map is whatever verifiable sample each client holds.

## 2. Record format

- **GR-1.** A record is a canonical CBOR map (RFC 8949 §4.2.1), at most
  `1024` bytes (s) encoded. Larger records MUST be dropped unread.
- **GR-2.** Fields (integer keys; unknown keys MUST be ignored for forward
  compatibility, but are covered by the signature):

| Key | Name | Type | Notes |
|---|---|---|---|
| 0 | `v` | uint | format version, `1` |
| 1 | `id` | bytes(32) | Ed25519 identity public key — the relay's name |
| 2 | `onion` | bytes(32) | X25519 key for circuit handshakes; MUST rotate ≤ 7 days (s) |
| 3 | `addrs` | array | endpoints: `[transport-id uint, blob bytes]` pairs |
| 4 | `bw` | uint | claimed sustained bandwidth, kB/s — a *claim*, see GR-7 |
| 5 | `created` | uint | unix time, MUST be rounded down to the hour (GR-5) |
| 6 | `expiry` | uint | unix time, MUST be ≤ `created` + 7 days (s) |
| 7 | `sig` | bytes(64) | Ed25519 over the canonical encoding with key 7 absent |

- **GR-3.** A relay MUST NOT publish geographic or jurisdictional claims about
  itself. Clients infer AS and jurisdiction from `addrs` with their own data
  (OP-1); self-declared location is an attack surface, not information.
- **GR-4.** Signature validity, size cap, expiry, and timestamp rounding MUST all
  be checked before a record is stored or forwarded; failures are dropped
  silently — no error that distinguishes "malformed" from "expired" may be
  observable by the sender of the record.
- **GR-5.** `created` rounding exists to stop clock-skew fingerprinting of
  relays. Clients MUST treat two records with the same `id` as one relay and
  keep only the freshest `created`.

## 3. Exchange and sampling

- **GR-6.** Records travel over established circuits and over the local mesh
  (Part 5), piggybacked in fixed-size batches: a gossip batch is `8` records (s)
  padded to constant size, exchanged at most once per peer per `10` minutes (s).
  A node answers a sample request with a uniform sample of its stored records;
  it MUST NOT answer with a sample biased by the requester's identity (the
  obvious eclipse lever).
- **GR-7.** `bw` is a claim. Clients SHOULD verify claims by randomized probing
  over circuits that do not reveal the prober, and SHOULD weight path selection
  by verified bandwidth, not claimed. Probing design is open (OP-2).
- **GR-8 (source mixing).** A client's stored sample MUST mix records from
  independent source classes — at minimum: social-graph bridge (Lox-style),
  gossip exchange, and direct probing — and MUST NOT allow any single class to
  exceed a configurable fraction (strawman 1/2) of the sample. This is the
  eclipse defense until OP-2 produces something stronger.
- **GR-9.** New identities are cheap by design (no registration), so nothing in
  this part may assume sybil-resistance from identity cost. Any mechanism that
  needs sybil-resistance must get it from verified resources (bandwidth,
  long-term uptime observed by the client itself) or the social graph — never
  from the record alone.

## 4. Bootstrap

- **GR-10.** A fresh client MUST be able to start from a single out-of-band
  bridge line (a QR code, a printed string, a message from a friend) containing
  one record plus one transport hint. Zero-contact bootstrap is OP-7 and open.

## 5. What this part does not decide

Sybil/eclipse resistance beyond GR-8/GR-9 (OP-2), probing protocol (GR-7),
zero-contact bootstrap (OP-7). Numbered issues exist for each.
