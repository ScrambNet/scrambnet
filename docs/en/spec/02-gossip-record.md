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
| 2 | `onion` | bytes(32) | X25519 static for the Sphinx per-hop key agreement (Part 1 §5, CH-2/CH-4); MUST rotate ≤ 7 days (s) |
| 3 | `addrs` | array | endpoints: `[transport-id uint, blob bytes]` pairs |
| 4 | `bw` | uint | claimed sustained bandwidth, kB/s — a *claim*, see GR-7 |
| 5 | `created` | uint | unix time, MUST be rounded down to the hour (GR-5) |
| 6 | `expiry` | uint | unix time, MUST be ≤ `created` + 7 days (s) |
| 7 | `sig` | bytes(64) | Ed25519 over the §2A signing input (GR-24); the profile for encoding and verification is §2A |

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

## 2A. Canonical encoding and the verification profile

GR-1 names "canonical CBOR (RFC 8949 §4.2.1)" and GR-4 requires signature
validity before store or forward, but §4.2.1 leaves encoding choices open and
Ed25519 verification famously diverges between libraries (Chalkias et al.,
*Taming the Many EdDSAs*; the ZIP-215 vs RFC 8032 split). For an I-1 network
either gap is fatal: two nodes that disagree on a record's canonical bytes, or on
whether a signature is valid, reject each other's valid records (a partition) or
split on a crafted record (a security-relevant split-view feeding the ID-8/ID-10
equivocation and PS-17 steering threats). This section pins both to the byte.
All of GR-21..GR-28 are constituents of "signature validity" as GR-4 uses the
term and MUST be enforced before a record is stored or forwarded, with GR-4's
silent uniform failure. The whole profile is made mechanically checkable by the
`records` vectors (GR-30) and demonstrated in `poc/gossip.py`, whose Ed25519 is
cross-checked bit-for-bit against an independent library.

- **GR-21 (shortest-form, definite-length, four types only).** Every integer and
  every length in a record MUST use the shortest CBOR head (preferred
  serialization, RFC 8949 §4.2.1): a decoder MUST reject any non-shortest head
  (e.g. `0x18 0x0a` for `10`). All maps, arrays, and byte strings MUST be
  definite-length; indefinite-length items MUST be rejected. The only CBOR major
  types permitted anywhere in a record are unsigned integer (major 0), byte
  string (major 2), array (major 4), and map (major 5) — exactly those GR-2 uses.
  Negative integers, text strings, floats, tags, simple values (including
  `false`/`true`/`null`), and any other major type or head MUST be rejected.
  This, with GR-21a, makes canonicalization **total**: every byte string either
  decodes to exactly one record or is rejected (I-1).
- **GR-21a (the shape of keys 0–7 is pinned, not only their CBOR type).** A
  field whose value is a composite type is a canonicalization ambiguity unless
  its inner shape is pinned: two implementations would otherwise split on a
  signature-valid record whose composite field one reads as well-formed and the
  other does not (key 3 `addrs` is the live case — it is never crypto-decoded, so
  no later check rescues the split). Therefore the shapes of the known keys MUST
  be enforced as a reject predicate, not treated as convention: key 0 `v` and key
  4 `bw`, key 5 `created`, key 6 `expiry` MUST be unsigned integers (GR-21); key
  1 `id` and key 2 `onion` MUST be byte strings of exactly 32 bytes; key 7 `sig`
  MUST be a byte string of exactly 64 bytes; key 3 `addrs` MUST be an array (which
  MAY be empty) each of whose elements MUST be an array of exactly two items, item
  0 an unsigned integer (the transport id) and item 1 a byte string of length
  `≤ N_addr = 256` (s) (the endpoint blob). Any other shape of a known key MUST be
  rejected as a canonicalization failure (GR-23/GR-29). Unknown keys ≥ 8 are
  signed-but-ignored (GR-2) and MAY carry any GR-21-legal value of any shape;
  only keys 0–7 are shape-pinned.
- **GR-22 (ascending integer key order, totally pinned for unknown keys).** Map
  keys MUST be unsigned integers encoded in shortest form (GR-21) and MUST appear
  in strictly ascending numeric order. Because keys are shortest-form unsigned
  integers, RFC 8949 §4.2.1's bytewise-lexicographic order of the encoded key
  **coincides exactly with ascending numeric order for all key values** (a
  one-byte head `0x00`–`0x17` always sorts before any multi-byte head, and within
  a fixed width big-endian order is numeric order); the §4.2.1 "bytewise ≠
  numeric past 23" subtlety exists only for non-shortest encodings, which GR-21
  forbids. Unknown keys ≥ 8 are permitted for forward compatibility (GR-2) and
  MUST sort by this same ascending-numeric rule. Keys MUST be unique; a map
  containing the same key twice MUST be rejected (the classic signature-bypass
  where two parsers disagree on which duplicate wins). There is thus exactly one
  legal key ordering for any set of keys, known or unknown (I-1).
- **GR-23 (verify over received bytes; the wire encoding MUST already be
  canonical).** A verifier MUST require the received record bytes to be the
  canonical encoding defined by GR-21/GR-21a/GR-22 and MUST reject any record
  whose received bytes are not canonical — wrong key order, non-shortest head,
  indefinite length, a disallowed type, a duplicate key, a mis-shaped known field
  (GR-21a), a top-level item that is not a map (major 5), or any trailing byte
  after the top-level map. (Because every container is definite-length, GR-21,
  the only place "trailing bytes" can occur is after the top-level item; an
  implementation MUST NOT invent an inner-trailing-bytes check that would reject a
  canonical record.) The verifier MUST NOT re-canonicalize and then verify over
  the re-encoded bytes; it verifies the signature over **exactly the received
  bytes** (GR-24). This is what makes GR-2's "unknown keys are covered by the
  signature but ignored for semantics" total: canonicalization is defined over the
  **full** map including unknown keys, the ordering of unknowns is pinned (GR-22),
  and a verifier need never reproduce a signer's encoding of a key it does not
  understand — it only checks that the bytes it received are themselves canonical.
  A node that tolerates a non-canonical wire record where another node rejects it
  is an I-1 defect.
- **GR-24 (the signing input is byte-exact and domain-separated).** The message
  signed for GR-2 key 7 is

  ```
  "ScrambNet-gossip-v1" ‖ 0x00 ‖ canon( record without key 7 )
  ```

  where the label is exactly the 19 ASCII bytes `ScrambNet-gossip-v1`, `0x00` is a
  single separator byte, and `canon(record without key 7)` is the
  GR-21/GR-21a/GR-22 canonical encoding of the record map with **key 7 omitted
  entirely** — the map header count reflects the remaining keys (e.g. 7, not 8),
  and key 7 is absent, **not** present-with-an-empty value — including every
  unknown key ≥ 8 in ascending order. The label-plus-separator is a
  domain-separation prefix (matching the suite-`0x01` label convention of
  `"e2e-content"`/`"box"`/`"tag"`) that MUST be present, so a record signature can
  never be reinterpreted as a signature over any other protocol's or version's
  message. The signature is pure Ed25519 (RFC 8032, no pre-hash) over these exact
  bytes. To verify, a node reconstructs this signing input from the received
  canonical record (GR-23) with key 7 removed and checks the key-7 signature
  against it under public key `A = id` (GR-28). This is the sole definition of the
  signing input; GR-2's key-7 row defers to it.
- **GR-25 (one verification equation: RFC 8032 cofactorless).** Signature
  verification MUST use the RFC 8032 cofactorless equation `[S]·B = R + [k]·A`,
  where `k = SHA-512(R ‖ A ‖ M) mod L`, `B` is the Ed25519 base point, `M` is the
  GR-24 signing input, and `R`, `A`, `S` are taken from the signature and `id`.
  Implementations MUST NOT use the cofactored (`[8]`-multiplied, ZIP-215-style)
  verification equation, and MUST NOT use a library whose acceptance set differs
  from this profile unless it is wrapped to match exactly. ScrambNet verifies
  records one at a time (GR-4), so the batch-verification motive for a cofactored
  equation does not apply; a single pinned equation is required so every node
  agrees bit-for-bit on validity (I-1). This prohibition forbids the `[8]`-
  cofactored *verification equation* only; it does **not** forbid the scalar
  multiplications GR-28 uses for subgroup membership.
- **GR-26 (canonical scalar S).** A record MUST be rejected unless
  `0 ≤ S < L`, where `L = 2^252 + 27742317777372353535851937790883648493` is the
  Ed25519 group order. A signature with `S ≥ L` (a non-reduced scalar) is the
  classic Ed25519 malleability and MUST be rejected even if the arithmetic would
  otherwise check, so no second encoding of the same signature is accepted by one
  library and rejected by another (I-1).
- **GR-27 (canonical point encodings for R and A).** The 32-byte encodings of `R`
  (from the signature) and `A` (the `id`) MUST be canonical: the encoded
  y-coordinate MUST satisfy `y < p` (`p = 2^255 − 19`), and an encoding with
  `y ≥ p`, or with the sign bit set on the non-canonical encoding of `x = 0`, MUST
  be rejected. A non-canonical point encoding is a second name for a point and is
  exactly an input on which libraries diverge; rejecting it keeps the acceptance
  set total (I-1).
- **GR-28 (`id` is the public key; A and R MUST be prime-order — tested by
  `[L]·P`, not a blacklist).** GR-2 key 1 `id` **is** the Ed25519 public key `A`
  and the relay's name: verification uses it directly, with no directory or key
  lookup (I-3, no authority). A record MUST be rejected unless both `A` and `R`
  decode (GR-27) to points of the **large prime-order subgroup** — equivalently,
  neither may be a small-order or mixed-order point. This membership MUST be
  tested as `[L]·P = 𝒪` (the identity) **and** `P ≠ 𝒪`, computed by scalar
  multiplication by the group order `L`: the first condition admits only the
  identity and the order-`L` points (since `L` is prime, no order in {2,4,8}
  divides it), and the `P ≠ 𝒪` condition then rejects the identity itself. A
  small-order-encoding **blacklist MUST NOT** be used as the test: it admits
  mixed-order points (order `2L`/`4L`/`8L`, which are not among the eight
  small-order encodings), and a mixed-order `A` or `R` is precisely an input on
  which the cofactored and cofactorless equations diverge — so a blacklist-only
  implementation would accept a signature a conforming node rejects (I-1). After
  GR-26/GR-27/GR-28 the acceptance set is the single strict set every conforming
  node computes identically. A record whose `id` is not a valid canonical
  prime-order point has no verifiable signer and MUST be dropped silently (GR-4).
- **GR-29 (these are GR-4 checks; failure is silent and uniform).** GR-21 through
  GR-28 are constituents of "signature validity" as GR-4 uses the term. A node
  MUST perform them before storing or forwarding a record, and MUST drop a failing
  record silently with no observable distinction — by error, response, or timing —
  between a canonicalization failure, a mis-shaped field, an invalid signature, a
  bad point, a size-cap violation (GR-1), expiry, or timestamp-rounding failure
  (GR-4/GR-5). The uniform silent drop is the I-4-flavored property GR-4 already
  requires; the constant-work discipline that makes it hold against a timing
  observer is a MUST, enforced as Part 9 RI-1b requires (a drop whose work
  betrays its reason is non-conforming), not a best effort.
- **GR-29a (check order: a record proves itself before it can affect state).**
  The checks MUST be applied in this order: (1) the GR-1 size cap (a record larger
  than the cap is dropped unread); (2) canonical encoding and field shape
  (GR-21/GR-21a/GR-22/GR-23) and signature validity (GR-24..GR-28); (3) only then
  may the record participate in GR-5 dedup and freshness. A record that fails (1)
  or (2) MUST NOT evict, replace, or otherwise affect any stored record. Without
  this order a relay that dedups before verifying can be made to discard an
  honest, signed record in favour of a forged one bearing a higher `created`
  (which then fails verification and is dropped, having already evicted the good
  record) — a denial of service GR-5 would otherwise invite.
- **GR-30 (conformance is defined by the records vectors).** A conforming
  implementation MUST reproduce the canonical encoding and the signing input of
  every positive record vector (roadmap 3.2, `vectors.json` `records` section)
  byte-for-byte, MUST verify every positive vector, and MUST reject every negative
  vector **for the specific GR-clause the vector names**. Accepting a record a
  vector marks "reject", rejecting a positive vector, or rejecting a negative
  vector for the wrong reason, is non-conformance: it is exactly the divergence
  (a record one node accepts and another rejects, or vice versa) that this section
  exists to prevent (I-1). Vector conformance certifies agreement on the
  accept/reject predicate; it does not certify timing (GR-29, cf. RI-1b).

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

## 5. The bandwidth-probing protocol (closing GR-7)

GR-7 says `bw` is a claim and SHOULD be verified by "randomized probing over
circuits that do not reveal the prober," then declares the probing design open.
This section is that design. The probe answers exactly one question — *what
throughput can I, this client, push through this relay right now over a circuit
that does not name me?* — and it answers it for the asking client alone. There is
**no** published, shared, or authoritative bandwidth number: Tor's bandwidth
authorities are precisely the central allocator I-3 denies us (PS-10, GR-9), so
every client derives its own verified figure and weights its own path selection
(PS-7) by it.

### 5.1 The measurement, and what it is a pure function of

- **GR-11 (verified bandwidth is a per-client self-measurement, never a published
  figure).** `[claim-critical]` A client's verified bandwidth for relay `R`,
  written `vbw(R)`, MUST be computed as a deterministic function of inputs the
  client observed **itself**:
  ```
      vbw(R, epoch) = probe(circuits_through_R, bytes_sent, timestamps_seen)
  ```
  and of nothing a relay, a peer, or any third party asserts. `vbw` is a local
  variable, not a network value: two honest clients probing the same `R` will
  derive **different** `vbw(R)` (their paths, their congestion, their moment), and
  this is correct — there is no true scalar "bandwidth of `R`" to agree on, only
  *throughput a given client achieved over a given path at a given time* (GR-18).
  A client MUST treat an un-probed relay's `bw` claim as the **low-bandwidth
  default** (PS-7), never as its figure; a claim the client has not itself
  measured carries zero weight in selection.

- **GR-12 (the probe is a sealed round-trip over a circuit — the prober is never
  named).** `[claim-critical]` A probe MUST be carried as ordinary circuit traffic:
  the client builds a circuit whose **measured relay `R` is the middle hop**, sends
  a bounded train of share-packet-shaped cells (Part 1: fixed `P = 2048` bytes,
  SP-3) addressed through `R`, and measures the round-trip throughput of the train
  as it returns over the same circuit. `R` sees a cell arrive from its predecessor
  and leave to its successor — exactly what it sees for real relayed traffic — and
  **cannot see the client**: the prober sits at least one hop beyond `R`'s view, as
  in any Sphinx circuit (SP-4). The probe MUST NOT use any cell type, flag, length,
  or cadence that distinguishes it from relayed user traffic (I-4, and GR-13
  below). A relay that could tell a probe from a payload could pass the probe and
  fail the payload; so, by construction, it cannot be given the chance.

```
  THE PROBE OVER A CIRCUIT  (R is measured; the prober is never in R's view)

   client (prober)        guard G        relay R  (under test)       tail T
   ───────────────        ───────        ──────────────────         ──────
        │                    │                  │                      │
        │  build circuit  C = [ G , R , T ]  (R is the MIDDLE hop)     │
        │───────────────────▶│                  │                      │
        │     train of N fixed-size cells, indistinguishable from      │
        │     real relayed share packets (SP-3/SP-4, I-4)              │
        │════════════════════╪═════════════════▶│═════════════════════▶│
        │                    │                  │   T echoes the train │
        │◀═══════════════════╪══════════════════╪══════════════════════│
        │   measure: bytes_acked / (t_last − t_first)  = this probe's   │
        │            throughput sample for R, THIS path, THIS moment    │
        │                    │                  │                      │
      vbw(R) ← robust aggregate of many such samples over time (GR-16) │

   What R sees:  cells from G  →  cells to T.   Identical to carrying real
   traffic.  R does NOT see "client", does NOT see "this is a probe", and
   cannot behave well only-when-watched because it cannot tell it is watched.
   The cost is PAID by the prober: it sends N·P bytes it will not get back
   as useful work (GR-14).  R cannot be made to flood a victim, because the
   train returns to the PROBER, never to an attacker-named third party (GR-15).
```

### 5.2 The five properties the probe must have

- **GR-13 (indistinguishability — a relay cannot behave well only when watched).**
  `[claim-critical]` The anti-gaming property is wire uniformity (I-4): **probe
  traffic MUST be byte-for-byte and timing-for-timing indistinguishable from the
  real relayed traffic a relay is asked to carry**, so that the relay cannot
  condition its forwarding on "am I being measured?" Concretely the probe cells
  MUST be full Part-1 share packets (`P = 2048` bytes, SP-3), MUST be emitted under
  the same batching/jitter discipline a real sender uses (SP-6, SP-9), and MUST NOT
  carry any probe-specific marker. A relay that under-serves real traffic and
  over-serves probes would have to distinguish them; I-4 denies it the information
  to do so. The measured `vbw(R)` is therefore a lower bound on what `R` *would*
  forward for this client's real traffic, because `R` cannot tell the two apart —
  which is the whole point: *attack this by finding a bit the relay can key on.*

- **GR-14 (the probe costs the prober a bounded, pre-paid amount).** A single
  probe of `R` MUST send at most `B_probe` bytes (strawman: `B_probe = 1 MiB`
  spread over `≥ τ` seconds, `τ = 4 s` (s)) and MUST be rate-limited to at most one
  in-flight probe per target relay and at most `Q` concurrent probes total per
  client (strawman `Q = 8` (s)). The prober spends real bytes it does not recover
  as useful work; this is the cost that makes probing self-limiting. A client MUST
  NOT probe a relay more often than once per `T_probe` (strawman: hours, not
  minutes (s)) — bandwidth changes slowly relative to how fast a measurement ages,
  so frequent re-probing buys little and costs linearly (GR-16).

- **GR-15 (the probe cannot become a DoS amplifier).** `[claim-critical]` The
  measured relay MUST only ever return probe traffic **to the prober, over the same
  circuit it arrived on** — never to any address the prober's cells could name.
  Because the tail hop `T` echoes the train back along `C` to the client that built
  `C`, a probe is a **closed loop**: the work a probe induces is bounded by what the
  prober itself sent (amplification factor ≤ 1 by construction, not by policy), and
  there is no field in which an attacker could write a victim's address to have `R`
  flood it. This is the structural difference from any "ask the relay to send a
  test stream to address X" design, which would be a reflector and is **forbidden**:
  a probe MUST NOT accept a destination it does not itself terminate. An
  implementation that lets the probe target a third party is non-conforming.

- **GR-16 (one probe measures a path-moment; `vbw` is a robust aggregate of many).**
  A single probe is a sample of *one path at one instant*, contaminated by the
  guard's and tail's own capacity, by cross-traffic, and by congestion anywhere on
  `C`. A client MUST therefore (a) probe `R` through **several independent circuits**
  (distinct guards and tails, GR-8 source-mixed where possible), (b) attribute to
  `R` the **maximum sustained throughput observed** across those circuits over a
  window (the max, because any single circuit's bottleneck is a *lower* bound on
  `R` — the fastest path best isolates `R`'s own capacity), and (c) treat the
  result as an **estimate with a confidence that decays with age** (strawman:
  half-life of a few epochs (s)). `vbw(R)` MUST be floored conservatively: an
  un-corroborated single probe counts as low, not high (PS-7 discipline).

- **GR-17 (probe results are not gossiped as bandwidth; only the discipline is
  shared).** A client MUST NOT publish, gossip, or accept from a peer a scalar
  "verified bandwidth of `R`" — that would reconstruct the bandwidth authority I-3
  forbids (a peer-reported figure is a claim no better than `bw` itself, GR-9). What
  MAY be gossiped is a relay's **reachability/liveness** as one source class among
  GR-8's classes, and a client MAY use a peer's agreement that a relay *exists and
  responds* as a corroborating vantage (PS-15 style), but the **throughput number
  each client uses for weighting MUST be its own** (GR-11). Sybil peers can inflate
  how *many* reports say "`R` is fast," but cannot inflate what the client's own
  probe measured — this is the GR-9/PS-10 "count only verified" rule applied to
  bandwidth.

### 5.3 What a probe can and cannot tell you (degrade honestly)

- **GR-18 (a probe measures throughput, not honesty, not location, not identity).**
  A probe answers *"can this path move bytes?"* and nothing else. It MUST NOT be
  read as evidence that:
  - **the relay is honest** — a relay can forward probe traffic perfectly and still
    log, delay, or correlate real traffic; throughput is orthogonal to the
    guard+exit correlation threat (threat model), which path *disjointness* (Part 3)
    addresses, not bandwidth;
  - **the relay is where the map says** — a probe times a round trip; it does not
    locate `R` in an AS or jurisdiction (that is Part 8's map, PS-4, with its own
    declared error), and a fast probe says nothing about co-location (Part 8 §10);
  - **the relay is a single distinct party** — a sybil operator with real capacity
    probes *as* fast as it is, because it genuinely has the bandwidth (see §6: a
    resourceful adversary is not a sybil, it is an expensive real adversary).
  A conforming client MUST present verified bandwidth only as what it is — a
  freshness-decaying, path-contaminated throughput estimate the client measured
  itself — and MUST NOT let a high `vbw` substitute for disjointness (Part 3) or
  diversity (GR-8) in any selection decision.

---

## 6. Sybil and eclipse, bounded (tightening GR-8/GR-9)

Identities are free (GR-9), so an adversary inflates the **raw** record count at
will. The defenses below do not stop that; they bound what the inflation *buys*,
and the bound is the curve the simulator measures (§7.1).

### 6.1 The eclipse bound from source mixing

- **GR-19 (the GR-8 cap gives a stated eclipse bound; the assumption is class
  independence).** `[claim-critical]` Let the client mix its sample across `m`
  independent source classes (GR-8: at minimum social-graph bridge, gossip
  exchange, direct probing — so `m ≥ 3`), with the per-class cap that **no single
  class contributes more than fraction `f`** of the stored sample (strawman
  `f = 1/2` (s)). Let an adversary fully control `a` of those `m` classes (every
  record delivered through a controlled class is adversarial) and nothing in the
  others. Then the adversary's share of the client's sample is bounded by
  ```
        A(a, f)  ≤  min( 1 ,  a · f ).
  ```
  A **full eclipse** — the adversary supplying the client's entire view, so that
  every honest relay is invisible and path selection draws only adversary circuits
  — requires `A = 1`, hence
  ```
        a  ≥  ⌈ 1 / f ⌉       classes under full adversary control.
  ```
  With the strawman `f = 1/2`, **full eclipse requires the adversary to own at least
  2 of the ≥3 classes**; owning any **one** class caps the adversary at `f = 1/2` of
  the sample and a full eclipse is **structurally impossible** (the honest classes
  still deliver ≥ `1 − f` of the view). This is the exact quantity GR-8 asserted
  without stating: the cap converts "eclipse" from "own enough relays" into "own
  enough *independent classes*," which is a strictly harder, and differently
  resourced, problem.

- **GR-19a (name the assumption, and where it fails).** The bound in GR-19 holds
  **only if the classes are genuinely independent** — if compromising the
  social-graph bridge distribution tells the adversary nothing about, and gives it
  no control over, the gossip peers or the probe targets. It **fails** precisely
  when one party controls more than one class at once:
  - an adversary who owns **both** the social-graph bridge **and** the gossip peers
    controls `a = 2` classes and, at `f = 1/2`, reaches `A = 1` — a full eclipse the
    cap does not prevent, because the cap bounds *per class*, and two classes that
    are secretly one party are not two classes;
  - correlated failure (one hosting provider, one jurisdiction, one software
    monoculture behind two nominal classes) collapses `m` toward 1 silently.
  Therefore the cap's protection is **exactly as strong as the independence of the
  classes**, and a conforming client MUST (a) source its classes from
  demonstrably different trust origins (a friend-introduced bridge is not
  independent of gossip if the friend is the gossip peer), and (b) treat a sample
  in which the classes *agree too perfectly* on an unusual view as the same anomaly
  signal Part 8 uses for map divergence (ID-10) and Part 3 uses for steering
  (PS-17) — gossip it, do not trust it. Independence is an **assumption the client
  must actively maintain**, not a property it gets for free from counting classes.

### 6.2 The sybil bound

- **GR-20 (sybils inflate raw count, never verified resources or real edges).**
  `[claim-critical]` Because identities are free (GR-9), a sybil adversary sets the
  **raw record count** to any value it likes. Two client-side quantities it
  **cannot** inflate bound the damage:
  1. **Verified bandwidth it does not have.** `vbw` (GR-11) is the client's own
     measurement; a sybil of 10 000 zero-bandwidth identities measures as 10 000
     relays of ~0 verified bandwidth and carries ~0 selection weight (PS-7). To gain
     *weight* the adversary must actually move the bytes — see GR-20a.
  2. **Genuine social-graph edges.** A Lox-style bridge class (GR-8) hands trust
     along *human* edges; a sybil can mint identities but not the edges that
     introduce them, so the social-graph class admits sybils only at the rate real
     people vouch for them (which is the whole reason that class exists).
  The operational consequence is **PS-10, now quantified**: the viable-size
  estimate MUST count **only independently verified relays and observed AS
  diversity**, so inflating the raw count from `N` to `10N` sybils moves the
  verified-size estimate by **0** (none of the sybils pass verification), and a
  client cannot be tricked into full `n, k` parameters whose diversity is fake. What
  "count only verified" buys, in one line: **the size that drives parameter choice
  is invariant under sybil inflation** — the adversary can make the network *look*
  arbitrarily large and change nothing a client acts on.

- **GR-20a (a resourceful adversary is not a sybil — it is a real, expensive,
  accepted adversary).** `[claim-critical]` The flip side of GR-20 is stated
  honestly: an adversary that **actually has** the bandwidth, the social vouching,
  and the AS/jurisdiction diversity is **not** defeated by any sybil defense,
  because it is **not a sybil** — it is a genuine `k`-path adversary that paid for
  its positions. This is the designed residual risk the threat model already
  accepts (the `k`-path row: "raise `n`, `k` to taste"), not a gap in this part.
  The sybil defenses raise the adversary's cost from *free* (mint identities) to
  *real resources proportional to the influence sought*; they do not and cannot make
  influence unpurchasable. A client MUST NOT present "sybil-resistant" as "adversary
  with real resources cannot gain position" — the first is true, the second is false
  and is a different, named, accepted threat.

---

## 7. What this does not solve (OP-2 remains open)

**OP-2 is not solved here, and no requirement above claims it is.** A central
allocator — Tor's bandwidth authority, Walking Onions' signed snapshot — *would*
solve both sybil and eclipse by fiat: it would publish one trusted view, and
sybils could not inject into it nor could an adversary feed a victim a private
view of it. I-3 forbids that allocator, because the party that can publish the one
trusted view is also the party that can be coerced, subpoenaed, or seized to
publish a *poisoned* one, and a discovery mechanism with that single point is the
kill switch the whole project refuses. Having refused it, we are left with a
**bound, not a cure**:

- **There is no overlay-only mechanism that makes gossip sampling fully
  sybil/eclipse-proof.** Every defense above is a *client-side resource-verification
  or source-mixing discipline*, and each has a declared seam:
  - the eclipse bound (GR-19) holds only under class independence, and **collapses
    when one party owns ≥ `⌈1/f⌉` classes** (GR-19a) — an adversary rich enough to
    be the friend who hands you the bridge **and** the peers you gossip with
    eclipses you, and the overlay cannot tell "two classes" from "one party wearing
    two hats";
  - the sybil bound (GR-20) stops *free* inflation but not *paid* position
    (GR-20a) — verification raises cost, it does not cap it;
  - the bandwidth probe (§6) measures throughput, not honesty or location (GR-18) —
    a relay can ace every probe and still be the adversary's, and a fast sybil with
    real capacity is a real adversary (GR-20a). A probe closes GR-7's *design*
    question; it does not close OP-2.
- **Bootstrap under eclipse is the hard residual.** A client eclipsed from its first
  contact (GR-10) sees only adversary classes, measures only adversary relays as
  "fast," and hears only adversary agreement — every corroboration mechanism in
  this part needs *one honest vantage* to function, and an adversary who supplies
  the client's entire world from the first packet denies it that vantage. This is
  the same shape as Part 8's TOFU bootstrap (ID-8): the defenses **detect** a bad
  view once one honest source is reached and make keeping a client eclipsed
  *forever* expensive — they do not **prevent** the initial eclipse. "Detect and
  make permanent eclipse costly," not "prevent eclipse," is the honest claim, and it
  is the claim the UI states.

**What the design does, precisely, is bound the attack along three axes:**
resource-verification (GR-11/GR-20: free sybils buy nothing), source-mixing
(GR-19: eclipse needs ≥ `⌈1/f⌉` independent classes, not just many relays), and the
social graph (GR-20: edges cannot be minted). The residual that remains after all
three is: **an adversary with real resources, real social vouching across multiple
genuinely-independent-looking classes, and the ability to supply a fresh client's
entire first view can sybil-inflate influence it paid for and eclipse a client it
surrounds — and the overlay cannot, from inside, prove it is being surrounded.**
That residual is OP-2, and it is open.

### 7.1 The bounds are the simulator's curves

These requirements are falsifiable, not rhetorical: a sybil/eclipse model is being
measured by `poc/sybil_sim.py` alongside `network_sim.py`'s existing `infer_error` sweep (the
simulator already models a partial per-client `gossip_sample` — the exact view an
eclipse adversary shapes — and already separates ground truth from the client's
belief). The design's bounds are the curves it MUST measure:

- **the eclipse curve:** adversary sample fraction `A` vs. number of controlled
  classes `a`, which MUST track `min(1, a·f)` of GR-19 and MUST show the knee at
  `a = ⌈1/f⌉` (full eclipse) — and MUST show that at `a = 1` the honest view never
  falls below `1 − f`;
- **the sybil-inflation curve:** verified-size estimate (PS-10) vs. raw sybil count,
  which MUST be **flat** — the GR-20 claim that inflating raw count moves the
  verified estimate by zero is exactly this flatness, and a non-flat curve falsifies
  GR-20;
- **the churn interaction:** eclipse probability vs. sample churn rate, since a
  client that re-samples faster meets an honest vantage sooner (the "detect, make
  permanent eclipse costly" claim is a rate, and the simulator must put a number on
  it).

If the simulator shows the eclipse curve beating `min(1, a·f)`, or the
sybil-inflation curve sloping up, the bound is wrong and this extension is broken —
attack the model, then this text. The one thing that cannot be made a curve is the
first-contact eclipse of a client with no honest vantage at all: that has no
overlay-internal measurement, because the victim, by definition, cannot see outside
the adversary's world. It is the OP-2 residual, declared, and it is why this part
says *bound*, not *solve*.

---

## Requirements introduced here

- **GR-21 / GR-21a** — canonical CBOR: shortest-form, definite-length, four major
  types only; and the inner shape of keys 0–7 (incl. `addrs` = array of
  `[uint, bytes]` pairs) pinned as a reject predicate so no composite field is a
  split.
- **GR-22** — strictly ascending unsigned-integer map keys (== bytewise order of
  the shortest-form key for all keys, known or unknown); duplicate keys rejected.
- **GR-23** — verify over the received bytes: the wire encoding MUST already be
  canonical (top-level map, no trailing bytes), never re-canonicalized.
- **GR-24** — the signing input is `"ScrambNet-gossip-v1" ‖ 0x00 ‖ canon(record
  without key 7)`; the sole definition, domain-separated against cross-protocol
  reuse.
- **GR-25** — one verification equation: RFC 8032 cofactorless `[S]B = R + [k]A`;
  the cofactored/ZIP-215 equation and divergent libraries are forbidden.
- **GR-26 / GR-27** — canonical scalar `S < L`; canonical point encodings for `R`
  and `A` (`y < p`).
- **GR-28** — `id` is the public key; `A` and `R` MUST be prime-order, tested by
  `[L]·P = 𝒪 ∧ P ≠ 𝒪` (a small-order blacklist is forbidden — it admits
  mixed-order points on which cofactored and cofactorless verification diverge).
- **GR-29 / GR-29a** — all of GR-21..GR-28 are GR-4 "signature validity",
  uniform-silent-drop (constant work, RI-1b); check order is size cap →
  canonical+signature → only then GR-5 dedup, so an unverified record never evicts
  a verified one.
- **GR-30** — conformance is defined by the `records` vectors: reproduce every
  positive vector byte-for-byte, reject every negative vector for its named clause.
- **GR-11** — verified bandwidth is a per-client self-measurement (`vbw`), never a
  published or shared figure; un-probed claims count as low.
- **GR-12** — the probe is a sealed round-trip with the measured relay as the
  middle hop; the prober is never in the relay's view.
- **GR-13** — indistinguishability: probe traffic MUST be byte- and timing-identical
  to real relayed traffic (I-4), so a relay cannot serve probes and starve payloads.
- **GR-14** — a probe costs the prober a bounded, pre-paid byte budget, rate-limited
  per target and in aggregate.
- **GR-15** — the probe is a closed loop (returns only to the prober); it can name no
  third-party destination, so it cannot amplify into a DoS reflector.
- **GR-16** — `vbw` is a robust aggregate over several independent circuits, taking
  the max sustained throughput, with age-decaying confidence and a conservative floor.
- **GR-17** — throughput numbers are never gossiped as bandwidth; only liveness/
  reachability is a shareable source class — each client weights by its own measurement.
- **GR-18** — honest degradation: a probe measures throughput, not honesty, not
  location, not distinct identity.
- **GR-19** — the GR-8 cap yields the eclipse bound `A ≤ min(1, a·f)`; full eclipse
  needs `a ≥ ⌈1/f⌉` controlled classes (≥2 at `f = 1/2`).
- **GR-19a** — the bound assumes class independence and fails when one party owns
  ≥ `⌈1/f⌉` classes; independence is maintained, not free.
- **GR-20** — sybils inflate raw record count but never verified bandwidth or real
  social edges; the verified-size estimate (PS-10) is invariant under sybil inflation.
- **GR-20a** — a resourceful adversary is not a sybil but a real, expensive, accepted
  `k`-path adversary; verification raises cost, it does not make position unpurchasable.

GR-11 and GR-19 are the load-bearing two: each client measures its own bandwidth
(no authority), and the source-mixing cap converts eclipse from "own enough relays"
into "own enough independent classes." Both are **bounded, not absolute** — GR-11's
probe cannot read honesty or location (GR-18), and GR-19 collapses when the classes
are secretly one party (GR-19a). OP-2 is not solved: there is no overlay-only
mechanism that makes gossip sampling fully sybil/eclipse-proof, and a client
eclipsed from its first contact has no honest vantage to detect it. The design
bounds the attack from resource-verification, source-mixing, and the social graph;
it does not eliminate it. That is the honest residual, and the simulator's curves
are where it is held to its own numbers. Break it the same way the rest of the spec
is broken: find a probe bit a relay can key on (defeating GR-13), a way the probe
names a victim (defeating GR-15), a sybil that moves the verified-size estimate
(defeating GR-20), or an eclipse that beats `min(1, a·f)` under genuinely
independent classes (defeating GR-19) — and you have broken this extension.


## 8. What this part does not decide

Sybil/eclipse resistance beyond GR-8/GR-9 (OP-2), probing protocol (GR-7),
zero-contact bootstrap (OP-7). Numbered issues exist for each.
