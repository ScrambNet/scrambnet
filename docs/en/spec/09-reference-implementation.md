# ScrambNet Specification — Part 9: Reference-implementation requirements

**Status: DRAFT.** This part states, as numbered requirements (`RI-n`), what a
real node MUST do that the proof-of-concept deliberately omits — each rule tied
to the threat it answers and, where it applies, to the invariant (I-1…I-4) it
protects. The toy in `poc/` is an *executable specification*, not a node: it
says so in its own first lines ("NOT PRODUCTION CODE. No constant-time
arithmetic, no networking, no onion layer"). Everything here is the distance
between that toy and something you may point at a hostile network. Every number
is a strawman to be attacked by requirement number; the sharper invitation is in
§1, and §11 names what is still open.

## 1. The central tension: an information-theoretic floor is only as unconditional as the code that computes it

ScrambNet sells an **unconditional** content floor (I-2, proved in Part 7): below
`k` shares, the ciphertext is *statistically independent* of the secret, against
unbounded computation and any quantum computer. That proof is about **values** —
the share bytes an adversary holds carry no information about the secret. It says
nothing about **how a real machine computes those bytes**, and that is where the
floor can be lost without a single theorem being wrong.

A GF(2⁸) multiply by table lookup (the PoC's `_EXP`/`_LOG` tables,
`poc/dispersal.py`) indexes memory at an address that **depends on a secret share
byte**. On real hardware, cache state makes that access time observable to a
co-resident attacker. The lookup therefore leaks, through a timing side channel,
the very bytes the floor is built to hide. The floor would then be *unconditional
in theory and recoverable in practice*.

This is the most important sentence in this part, stated as a principle:

> **A timing or memory-disclosure side channel that reveals secret share bytes,
> coefficients, or the content key is not a "computational" break that I-2 is
> permitted to have. It is a break of I-2 itself.** Part 7 licenses exactly one
> computational assumption — the end-to-end AEAD *above* `k` (SP-1a) — and
> nothing else. A side channel that discloses sub-`k` secret bytes does not cost
> the adversary "work under an assumption"; it hands over the bytes. The proof
> of SA-1/SA-2 assumes the adversary sees **only** the `k−1` share values and
> the public parameters. A side channel adds a view the proof never granted, and
> the proof does not cover it.

Two consequences, which the rest of this part makes normative:

- The floor's **compute path** — every GF(2⁸) operation on secret-dependent data
  in Shamir split, reconstruct, and Lagrange interpolation — MUST be
  constant-time (RI-1). This is not hardening; it is the condition under which
  SA-1/SA-2 describe the real system, exactly as SA-3 (coefficient randomness) is.
- The floor's **memory residue** — shares, coefficients, derived keys — MUST not
  survive to be read from a heap dump, a swap file, or a core dump (RI-9). A
  floor that is information-theoretic on the wire but recoverable from `/proc` is
  not a floor.

The PoC is honest that it fails both: it is pure-Python table lookups with no
zeroization, correct but leaky, and it says so. This part is the list a real node
must satisfy instead. Where the PoC *already* enforces a rule (it refuses to
disperse plaintext that has not been through the AEAD — `send()` seals before it
splits), that is the bar, not a nicety, and RI-6 raises it to a MUST.

**Scope.** This part constrains the *implementation* of constructions fixed
elsewhere; it introduces no new wire format and changes no byte on the wire (that
would be an I-1/I-4 change and belongs in Parts 1–6). It MUST NOT be read to
relax any requirement it references; where it appears to, the referenced part
wins and the contradiction is a defect to report.

## 2. Constant-time field arithmetic (the floor's compute path)

- **RI-1 (constant-time GF(2⁸), protects I-2).** All GF(2⁸) arithmetic applied to
  secret-dependent data — Shamir `split` (polynomial evaluation over secret
  coefficients and the secret constant term), `reconstruct`/Lagrange
  interpolation (including the field **inversion** `gf_inv` in the basis
  denominator), and any multiply whose operand is a share byte, a coefficient, or
  a reconstructed secret byte — MUST be computed **without secret-dependent
  branches and without secret-dependent memory-address access**. Concretely, an
  implementation MUST NOT index a table (`_EXP`/`_LOG`, an S-box, or any array)
  at an offset derived from a secret value. Conforming techniques are a
  constant-time bitsliced or tower-field multiply, a carry-less-multiply
  (`CLMUL`) reduction, or a field provided by a library that *documents*
  constant-time behavior for these operations. Threat: a co-resident or
  remote-timing adversary recovers secret share bytes from cache or
  branch-timing — a **direct break of I-2** (see §1), not a computational one.
  This applies symmetrically to **split and reconstruct**: an endpoint that
  reconstructs leaks the secret it just recovered exactly as a splitter leaks the
  one it is dispersing.
- **RI-1a (inversion and division are not exempt).** The Lagrange denominator
  inverse (`gf_inv` in `poc/dispersal.py`, computed there as
  `_EXP[255 − _LOG[a]]`) operates on a value derived from the secret share set
  and MUST be constant-time; a data-dependent exponentiation or a table-lookup
  inverse is non-conforming. An implementation SHOULD prefer an inversion-free
  interpolation (e.g. batching the denominators and inverting once via Fermat
  `a^{254}` by a fixed addition chain, or Montgomery's trick) so that no
  secret-dependent division remains. The evaluation points `x_1…x_n` are **public**
  (Part 7 §2), so arithmetic on *them alone* need not be constant-time; the
  moment a public point is multiplied into a secret, the product is secret.
- **RI-1b (vectors do not certify timing).** Passing the roadmap-3.2 GF test
  vectors proves a multiply is *correct*, not that it is *constant-time*: the
  PoC's leaky tables pass those same vectors. An implementation MUST NOT treat
  vector conformance as evidence of RI-1 compliance. Constant-time behavior
  SHOULD be checked by a timing-analysis or statistical tool (e.g. dudect-style
  leakage tests) and, where the platform allows, by disabling compiler
  transformations that reintroduce secret-dependent branches (RI-9b).
- **RI-1c (the secret's whole lifetime is constant-time, not only its field ops,
  protects I-2).** Constant-time discipline is defined by **data flow, not by
  naming the GF operations**: any value tainted by a share byte, a coefficient, or
  a reconstructed secret byte inherits the RI-1 obligation until it is zeroized
  (RI-9), and that obligation reaches *past* the field layer. In particular, the
  reconstructed-secret length prefix (SP-8) MUST be parsed, and the recovered
  plaintext copied, sliced, and validated, **without a secret-dependent branch and
  without a secret-length-dependent memory access**; `unpad` MUST NOT branch on
  the decoded length in a way an observer can time, and no comparison, bounds
  check, or buffer move on a secret may be data-dependent. Threat: §1's own
  principle — "an endpoint that reconstructs leaks the secret it just recovered
  exactly as a splitter leaks the one it is dispersing" — is only enforced if the
  *whole* handling of the recovered secret is constant-time, not merely its GF
  arithmetic. A node that uses a verified constant-time field (RI-1) and a vetted
  constant-time AEAD (RI-8) but then branches on a recovered length satisfies
  every other MUST while leaking recovered-secret structure through timing, which
  is a direct I-2 break by the same argument as RI-1.

## 3. CSPRNG discipline (the floor is exactly as strong as its randomness)

The floor is no stronger than the randomness of the Shamir coefficients: Part 7
SA-3 is the "highest-assurance component" of the whole spec, and
`test_properties.test_coefficient_reuse_breaks_the_floor` shows reuse leaks the
secret with certainty. The same discipline governs every other secret the node
draws.

- **RI-2 (cryptographic DRBG from the OS, protects I-2 via SA-3).** All secret
  randomness — Shamir coefficients (SA-3), the per-packet circuit ephemeral `x`
  of CH-3, `msg_nonce`/message counters where not deterministic, `kpair`
  generation, and any `box_id` salt — MUST be produced by a cryptographically
  secure DRBG seeded from the operating-system CSPRNG (`getrandom`/`getentropy`,
  `/dev/urandom` after the pool is initialized, or an equivalent blocking-until-
  seeded source). An implementation MUST NOT use a non-cryptographic PRNG
  (an LCG, Mersenne Twister, `rand()`, a hash-of-counter, or a stream reused as
  "random") for any value in this list.
- **RI-2a (fork- and clone-safety — the classic catastrophe).** A process that
  `fork()`s, is restored from a checkpoint, is migrated, or is cloned as a VM or
  container image MUST NOT reuse DRBG state that produced output before the split.
  The implementation MUST reseed from the OS on fork/restore (e.g. a
  `pthread_atfork`/`MADV_WIPEONFORK` discipline, or a per-call OS draw) so that no
  two processes ever emit the same coefficient stream or the same ephemeral `x`.
  Threat: two identical VM clones split *different* messages under the **same
  coefficients**, and by SA-3 the pair of share sets becomes correlated with both
  secrets — the textbook randomness catastrophe, and a direct I-2 break. This is
  called out specifically because it is invisible to any single-process test.
- **RI-2b (health and startup checks).** Before emitting the first secret value,
  a node MUST confirm the OS entropy source is seeded (it MUST NOT fall back to a
  low-entropy source if the pool is not ready) and SHOULD run a startup
  self-test on the DRBG. A node SHOULD perform a continuous
  repetition/stuck-output test on raw entropy where it has access to it, and MUST
  fail closed — refuse to split or to build a packet — rather than proceed with a
  suspect generator. A generator that cannot be verified is treated as broken.
- **RI-2c (no injectable coefficients in production — but conformance vectors still
  run).** The PoC's `split(..., coeffs=...)` parameter exists only so vectors can be
  deterministic and the reuse break demonstrated. A production artifact MUST NOT
  expose any path — flag, config, env var, or symbol — that lets a caller supply,
  log, or pin Shamir coefficients or the ephemeral `x`; such a path is an SA-3
  foot-gun. The reconciliation with the roadmap-3.2 conformance vectors (RI-10),
  which require deterministic injected coefficients to reproduce, is a **build-time
  test gate**: the injection path MAY exist *only* behind a gate that is **absent
  from any production artifact** and unreachable at runtime in production. Vectors
  are matched against a test build that enables the gate; the production build MUST
  be identical to it except for the gated code's absence, and that equivalence
  SHOULD be verified by the build (e.g. a reproducible diff of the two). "Compiled
  out, not merely discouraged" means exactly this: present for the test binary,
  physically absent from the shipped one — never a runtime switch.

## 4. Nonce and key-rotation state across restarts

Two different secrets must never be reused across a restart: the AEAD/tag nonce
(SP-7b) and the relay `onion` static epoch (CH-5). A restart is the moment a node
is most tempted to "start fresh" and reuse a value it already used.

- **RI-3 (monotonic nonce high-water mark survives restarts, protects SP-7b and
  SP-1a).** Per `kpair`, the sender's `msg_nonce` (a strictly increasing message
  counter, SP-7b) MUST be persisted and MUST NOT roll back across a restart,
  crash, or clock change. The implementation MUST `fsync` (or the platform
  equivalent durable barrier) the high-water mark **to stable storage before the
  nonce it covers is used on the wire**, so a crash between use and persistence
  can only *skip* nonces, never repeat them. A node MUST NOT reuse or decrease a
  `msg_nonce` under one `kpair`. Threat: a reused `msg_nonce` is **doubly fatal**
  (SP-7b) — it collides SP-7 tags (making a share set linkable across colluding
  drops) **and**, because `msg_nonce` is the ChaCha20-Poly1305 nonce (SP-1a),
  destroys AEAD confidentiality as a two-time pad. Rolling the counter back after
  a restored backup is the realistic failure, and it is a confidentiality break,
  not a glitch.
- **RI-3a (reserve-ahead to bound fsync cost).** An implementation MAY persist the
  high-water mark in blocks (reserve `B` nonces with one durable write, hand them
  out from memory, persist again before the block is exhausted) to avoid an fsync
  per message. A crash then wastes at most the unused tail of a block — acceptable,
  because the counter space is large and skipping is safe while repeating is fatal.
  It MUST NOT, under any crash-recovery path, hand out a nonce at or below the last
  durably persisted mark.
- **RI-3b (a restore is not a restart — detect rollback or retire the key, protects
  SP-7b/SP-1a).** RI-3/RI-3a defend against a *crash* (the persisted mark only ever
  moves forward); they do **not** defend against a VM snapshot, filesystem
  snapshot, or backup **restore** that rewinds the persisted mark itself —
  precisely the "rolling the counter back after a restored backup" RI-3 names as
  the realistic failure. A node MUST NOT assume its persisted nonce store is
  monotonic across such a restore. It MUST therefore either (a) bind the
  high-water mark to a per-boot/per-restore nonce-**salt** (or a monotonic
  generation counter) persisted in the *same durable write* as the reservation, so
  a rewound store is detectable, and on detection **retire the `kpair`** — derive a
  fresh content/tag key, treating a reused salt under a rewound counter as
  compromise — or (b) refuse to emit under the affected `kpair` on any sign of a
  restore (the system clock moving backwards, or the persisted generation counter
  decreasing) until a fresh `kpair` is negotiated out of band (Part 6). Reserve-ahead
  (RI-3a) MUST carry the generation counter in the reservation's durable write, so a
  restore cannot replay a whole reserved block undetected. Threat: without this, a
  snapshot restore re-emits an entire block of already-used `msg_nonce` values — the
  doubly-fatal two-time pad of RI-3, on a path RI-3a's crash-only guard cannot see.
- **RI-4 (onion static epoch state and safe retirement, protects CH-5/CH-6).** A
  relay MUST persist which `onion` static epoch it is in (the active private key,
  its `created`/`expiry`, and the in-flight grace window) so a restart does not
  silently re-publish an expired key, resurrect a retired one, or mint a second
  "fresh" static inside the same declared epoch. On rotation (≤7 days, CH-5) the
  relay MUST, once the in-flight grace has passed, **zeroize the private half of
  the retired static** (RI-9) and MUST NOT retain it; a relay that keeps old
  statics enlarges its own CH-6 linkage-exposure window and is non-conforming.
  Clients remain bound by GR-4/CH-5 to reject any record whose `expiry` exceeds
  `created + 7 days` (GR-2 key 6), so a node that forgets its epoch cannot extend
  the window by republishing. Threat: a restart that rolls the static back into a
  window the client already saw, or that fails to destroy a retired static,
  reopens exactly the CH-5a linkage exposure the rotation ceiling exists to bound.

## 5. Replay-cache persistence

ScrambNet rejects replays at two layers, and both are stateful: the circuit layer
drops a seen `gamma` per key epoch (SP-5), and the storage layer drops a redeposit
of an already-stored `(box_id, slot)` (SP-7b, RZ-7). A restart that forgets this
state reopens a replay window.

- **RI-5 (replay state survives restarts, bounded to the epoch, protects SP-5 /
  SP-7b).** A relay MUST persist, or safely and completely rebuild, its Sphinx
  replay cache of seen `gamma` values **for the current key epoch**, and a drop
  MUST persist its set of stored `(box_id, slot)` deposits, so that a restart or
  crash does not accept a packet or a deposit it has already seen within the live
  epoch. Threat: a relay that restarts with an empty replay cache will re-admit
  every packet an adversary captured and re-injects inside the epoch — a reopened
  replay window, which at the drop layer can also multiply or displace honest mail
  against the RZ-7 per-box cap.
- **RI-5a (the cache is bounded — by two *different* retention windows, not "the
  epoch").** The two replay caches are each bounded in memory, but by **distinct**
  windows that an implementation MUST NOT conflate:
    - the Sphinx `gamma` cache is bounded by the **onion-static key epoch** (CH-5,
      ≤7 days) — a `gamma` is only replayable while the key that keyed it is live;
    - the `(box_id, slot)` deposit-dedup set is bounded by the **slot expiry**
      (RZ-7, 7 days), **not** by the 1-day `box_id` rotation (RZ-10). The box id
      rotates daily for *addressing*, but a deposited slot is *stored* for up to 7
      days (plus the RZ-14 boundary grace), so a redeposit is droppable for as long
      as the slot it would collide can still be stored — up to ~7 box epochs. Sizing
      this set to one day undersizes it ~7×.
  An implementation MUST discard each cache's state once its own window has passed
  (the `gamma` cache at key-epoch end, the deposit set at slot expiry), which caps
  memory at roughly the key-epoch's packet volume and the 7-day deposit volume
  respectively. It MAY bound memory further with a counting structure (e.g. a
  sized Bloom/cuckoo filter) **only if** it is tuned so that false positives stay
  below an operationally negligible rate; a false positive drops an honest packet
  (a self-inflicted DoS), a false negative admits a replay (a security failure), so
  the structure MUST be sized to make the latter impossible within its retention
  window and the former rare. A node that cannot persist a cache MUST fail closed
  for a window it cannot cover (treat the forgotten span as replayable and, for the
  `gamma` cache, rotate the key epoch) rather than silently accept replays.
- **RI-5b (rebuild must be complete, or treated as a rotation — and a restore is
  not a rebuild).** An implementation that rebuilds replay state after a crash
  (rather than persisting it continuously) MUST either reconstruct it completely
  for the live window or treat the gap as the start of a new key epoch (new keys,
  so old `gamma` values are no longer acceptable). A partial rebuild that leaves
  part of the window unprotected is non-conforming. Furthermore, a VM/filesystem
  **restore** that rewinds the cache to an *earlier, complete-looking* state is not
  a crash and RI-5b's completeness check cannot detect it: a restored relay comes
  back with a cache from *before* the packets an adversary captured, and re-admits
  them. A node MUST treat any sign of a restore (the same clock-rewind or
  generation-counter decrease as RI-3b) as a mandatory **key-epoch rotation**, so
  the pre-restore `gamma` values are no longer acceptable regardless of what the
  rewound cache contains.

## 6. Misuse-resistant API (make the insecure thing impossible)

I-1 and the `[soundness]` discipline demand that the API make the insecure
operation *unrepresentable*, not merely documented as unwise. The ordering of
SP-1 (encrypt **then** split) and the fail-closed rule of SP-7a are the two places
an API most easily inverts.

- **RI-6 (the API MUST refuse plaintext-without-AEAD, protects SP-1/SP-1a).** The
  dispersal entry point MUST refuse any input that has not already passed the
  end-to-end AEAD (SP-1a): it disperses **ciphertext only**, never plaintext.
  There MUST NOT be a public "split these raw bytes" path that bypasses the
  encrypt-then-split ordering of SP-1 — i.e. no way to reach `split()` without
  the AEAD seal in front of it. The PoC meets this bar already: `send()` calls
  `e2e.seal` before `disperse`, and `dispersal.py` is documented to "never touch
  plaintext." A real node MUST keep that door shut at the type level, not by
  convention. Threat: splitting plaintext directly destroys the *computational
  belt* (tier 2 of Part 7) — the shares then reconstruct straight to plaintext for
  any `≥k` adversary, with no AEAD behind them — and inverts the composition the
  whole design rests on.
- **RI-6a (type-separate ciphertext from plaintext).** An implementation SHOULD
  represent "plaintext" and "end-to-end ciphertext" as distinct, non-
  interchangeable types, so the SP-1 ordering cannot be inverted by passing the
  wrong buffer and a "split raw bytes" call is a compile-time error rather than a
  runtime check. Where the language cannot enforce this, the node MUST interpose a
  runtime guard that is on by default and cannot be disabled by configuration.
- **RI-6b (raw field entry points MUST be module-private).** Type separation
  (RI-6a) is not enough on its own: the raw `split`/`reconstruct` and any direct
  field entry point MUST be module-private (not exported), so the *only* public
  dispersal symbols are the one that takes the AEAD-ciphertext type (RI-6) and the
  one that returns an authenticated-open result (RI-7). A public `split(raw_bytes)`
  or `reconstruct(...)` symbol is itself the defect, independent of what a caller
  passes it — in a language where `bytes` is `bytes`, an exported raw-split lets a
  lower-level caller bypass the AEAD gate while type-checking cleanly. The PoC
  exposes these at module scope *because it is an executable spec*; a real node
  MUST NOT.
- **RI-7 (reconstruction MUST fail closed, in constant time, protects SP-7a).** The
  AEAD tag is the **sole** integrity arbiter (SP-7a): Shamir reconstruction has
  none of its own, so a flipped share byte or a lied-about `(k,n)` yields a
  consistent-but-wrong candidate that only the AEAD rejects. The reconstruction API
  MUST return a message **only** after the end-to-end AEAD verifies, and MUST
  discard — never surface, log, or act on — any candidate whose tag fails. It MUST
  NOT expose an "unauthenticated reconstruct" result to application code. **The
  fail-closed discard MUST also be constant-time with respect to *why* it failed:**
  the reconstruct-then-open path MUST take indistinguishable time and emit no
  distinguishable response (CH-9/I-4) whether the AEAD tag verified, the `(k,n)`
  byte was lied about (RI-7a), or the share bytes were corrupted — an adversary who
  can feed reconstruction candidates (the SP-7a hostile-drop residual, or a `≥k`
  coalition replaying share sets) MUST NOT learn which, by timing or by response,
  else the reject path becomes a padding-oracle-style distinguisher even though the
  tag *comparison* (RI-8) is constant-time. The PoC pins the fail-closed behavior
  (`receive()` drops on the `ValueError` from `e2e.open_`,
  `test_tampered_share_fails_closed`); a real node MUST not add a path around it,
  nor a timing side door through it. Threat: handing up an unauthenticated
  reconstruction turns the accepted SP-7a denial-of-service residual into the
  delivery of attacker-chosen garbage; timing the rejection turns it into an oracle.
- **RI-7a (parse the `params` byte defensively, do not trust it).** The `(k,n)`
  byte is attacker-controlled on a hostile share (SP-7a) and nibble-order-locked
  by vectors (SP-7a / roadmap 3.2). An implementation MUST validate it against the
  vector-locked order and against `1 ≤ k ≤ n ≤ 15` (as `_check_params` does) before
  use, and MUST treat a reconstruction under a lied `(k,n)` as an ordinary
  fail-closed drop (RI-7), never as a reason to allocate unbounded memory or index
  out of bounds.

## 7. The AEAD and tag comparison (the belt must also be constant-time)

The computational belt (tier 2, Part 7 §5) is only as sound as its implementation.
The PoC's AEAD is correct against RFC 8439 but is explicitly **not** constant-time
("it is correct … but leaks through timing, so a real node MUST use a vetted
constant-time library").

- **RI-8 (constant-time AEAD and tag comparison, protects SP-1a / SP-7).** A node
  MUST use a ChaCha20-Poly1305 implementation whose data path and whose
  **authentication-tag comparison** are constant-time, and MUST compare the SP-7
  share tag and the SP-7a AEAD tag with a constant-time equality primitive (no
  early-exit `memcmp`, no data-dependent branch on tag bytes). Threat: a
  non-constant-time tag check is a classic forgery oracle — byte-by-byte timing on
  the comparison lets an adversary forge a valid tag — which attacks the belt
  (SP-1a) and the share-recognition tag (SP-7) directly. The Poly1305 and X25519
  arithmetic MUST likewise be constant-time (RI-11); a variable-time
  implementation of either leaks key material through timing.

## 8. The onion layer the toy omits

The PoC has "no onion layer": `dispersal.py` operates only on the `delta`
payload's share, and the Sphinx header (`alpha`/`beta`/`gamma`) and its per-hop
cryptography exist only as the Part 1 §5 specification. A real node MUST implement
that layer, and its cryptography is in scope here because it carries secret
material (the hop secrets and the client ephemeral) under the same side-channel
threat as the floor.

- **RI-10 (implement the CH-2 per-hop derivation, protects I-1/I-4).** A node MUST
  implement the Sphinx circuit handshake of Part 1 §5 exactly: per hop, derive the
  shared secret `s_i = X25519(alpha_i, onion_i)` from the blinded group element
  and the relay static (CH-2), and derive the routing-info stream key, the `gamma`
  MAC key, and the `delta` AEAD key from `s_i` by HKDF-BLAKE2s under the fixed
  labels `sphinx-rho`, `sphinx-mu`, `sphinx-delta` (CH-2; exact label bytes and
  chaining vector-locked under roadmap 3.2). It MUST perform the Sphinx blinding
  (re-randomize `alpha` per hop) and enforce the replay discipline of SP-5.
  There is **no separate handshake transcript** (CH-1); a node that emits or
  expects any Noise/handshake message on a circuit is non-conforming (CH-1).
  *Flag:* the cross-implementation test vectors for this derivation are roadmap
  3.2 and MUST be matched once published; until then, two implementations are not
  yet proven to interoperate at this layer (I-1), and this is stated openly rather
  than assumed.
- **RI-11 (constant-time X25519 and the keyless-ephemeral discipline, protects
  CH-3/CH-6/I-2).** The X25519 scalar multiplication on every hop MUST be
  constant-time (a Montgomery-ladder implementation with no secret-dependent
  branch or memory access); a variable-time X25519 leaks the hop scalar and thus
  the hop secret. The per-packet client ephemeral scalar `x` behind `alpha_0`
  (CH-3) MUST be freshly drawn from the CSPRNG (RI-2) per packet, MUST never be
  reused across packets, and MUST be zeroized immediately after the packet is
  built (RI-9) — its destruction is what makes CH-6's epoch-granular forward
  secrecy real (a retained `x` lets a later relay-static seizure recompute the hop
  secret the design promises is gone). A relay MUST likewise keep its `onion`
  static under RI-2's key-handling and RI-4's rotation/retirement, and compute with
  it in constant time.
- **RI-11a (reject the degenerate shared secret, the X25519-correct way).** X25519
  deliberately exposes no cheap on-curve/order test (RFC 7748), so "validate the
  `alpha` point" is not the buildable check; the required, buildable one is: compute
  `s_i = X25519(alpha_i, onion_i)` and, **in constant time, reject if the resulting
  shared secret is all-zero** (the low-order / small-subgroup outcome) *before*
  deriving any hop key from it. This denies a malicious predecessor a forced
  small-order or known-key hop. Because every byte on the wire is uniform
  (SP-4/I-4), the check is on the *computed secret*, not a cleartext flag, and a
  relay MUST process a rejected `alpha` in time and bytes **indistinguishable from
  an ordinary replay-drop** (SP-5/CH-9/I-4) — no distinguishable response, no timing
  tell. The full point-validation/encoding rule is vector-locked under roadmap 3.2,
  but the all-zero-output rejection is normative *here* so the requirement is
  buildable without waiting on that file (I-1).

## 9. Memory zeroization, swap, and fault safety

A floor that is unconditional on the wire but recoverable from a heap dump, a swap
file, or a core dump is not a floor (§1). Memory disclosure reveals the very bytes
below `k` that I-2 protects, so zeroization is an I-2 requirement, not hygiene.

- **RI-9 (hold secrets in zeroizable storage and erase them after use, protects
  I-2).** Shamir shares, polynomial coefficients, the reconstructed secret, every
  derived key (`content_key`, the SP-7 `tag` key, the `box_id` key, each Sphinx hop
  key `s_i` and its derivatives), the pre-shared `kpair`, the client ephemeral `x`
  (RI-11), and the relay `onion` static (RI-4) MUST be held in storage the node can
  overwrite in place and MUST be zeroized as soon as they are no longer needed. The
  obligation is stated as *storage choice first* because a bare "zeroize" is
  **physically impossible** in some of this spec's own target languages: in CPython
  (the reference PoC's language) a secret in an immutable `bytes` object may be
  interned, copied by the allocator, and freed without any reachable overwrite, and
  a copying/compacting GC (Go, Java, …) may relocate a secret so no single erase
  reaches every copy. Therefore:
    - In a runtime that provides **deterministic, in-place mutable** secret storage,
      the node MUST zeroize with a primitive the compiler cannot elide as a dead
      store (`explicit_bzero`/`memset_s`/`SecureZeroMemory`/a `volatile` barrier or
      the language's audited `Zeroize`) — a plain `memset` on a to-be-freed buffer
      is routinely optimized away.
    - Where the language **cannot** guarantee that (immutable byte strings, a
      copying/compacting GC, value-copy semantics), the node MUST hold every secret
      in **pinned/native/off-heap** memory it *can* zeroize (RI-9b's native-memory
      clause is then a **MUST**, not a SHOULD) and MUST NOT keep the secret in a
      runtime-managed object (a `bytes`/`str`, a GC-heap array) at all.
  The requirement is thus "use zeroizable storage, then erase it" — satisfiable in
  every language — rather than "erase an object the runtime will not let you reach."
  Threat: these are exactly the sub-`k` secret bytes the floor hides; leaving them
  in freed heap, a reused buffer, a relocated GC copy, or a logged structure lets a
  later memory read reconstruct them, which is an I-2 break by memory disclosure.
- **RI-9a (keep secrets out of swap and core dumps).** Secret buffers SHOULD be
  locked into RAM (`mlock`/`mlockall`/`VirtualLock`) so they are never paged to a
  persistent swap file, and the process SHOULD disable core dumps
  (`RLIMIT_CORE = 0` or the platform equivalent) or exclude secret pages from
  them. A node that cannot prevent swapping of secret pages SHOULD use an
  encrypted-swap deployment and MUST document the residual. Threat: a swap file or
  a crash dump is a durable, disk-resident copy of the sub-`k` bytes — the floor,
  spilled to storage where it long outlives the process.
- **RI-9b (defeat optimizer and language hazards).** An implementation MUST ensure
  the compiler and language runtime do not reintroduce the leaks these rules
  forbid: no secret-dependent branch resurrected by optimization (RI-1), no
  copied-and-forgotten secret from a reallocating container, a moved value, a
  garbage-collected or copying-GC heap, string interning, or an exception/stack
  trace that captures a secret buffer. In managed-memory languages where a buffer
  may be copied by the runtime, a node SHOULD hold secrets in pinned/native memory
  it can zeroize deterministically, and MUST NOT rely on the garbage collector to
  erase them.
- **RI-12 (fault and exception safety — no partial or linkable artifact, protects
  I-2/I-4).** A crash, exception, or cancellation **mid-split** MUST NOT emit a
  partial share set, a subset of shares on the wire, or any artifact that links the
  shares of one message, and MUST NOT leave secret state un-zeroized. An
  implementation MUST build all `n` shares and commit to emission as an all-or-
  nothing step relative to failure, zeroizing coefficients and shares on any error
  path before unwinding. Threat: a sender that crashes after emitting some but not
  all shares, or that logs an intermediate share in a stack trace, hands an
  observer a correlated subset (undercutting SP-7's unlinkability and, if it
  reveals `≥k` of one message, the floor) — and an un-zeroized unwind leaves the
  secret in memory (RI-9). Fault handling MUST fail closed: on any error during
  split, disperse, or reconstruct, produce nothing and wipe, rather than produce
  something partial.

## 10. How these requirements map to the invariants and threats

| `RI` | Protects | Threat it denies (the real-node attack) |
|---|---|---|
| RI-1 / 1a / 1b / 1c | I-2 | cache-/branch-timing recovery of sub-`k` bytes, incl. the recovered-secret handling past the field ops |
| RI-2 / 2a / 2b / 2c | I-2 (SA-3) | weak/forked/clonable RNG → correlated coefficients |
| RI-3 / 3a / 3b | SP-7b, SP-1a | nonce rollback on restart **or snapshot/backup restore** → tag collision + two-time pad |
| RI-4 | CH-5 / CH-6 | static-epoch rollback or retained retired static |
| RI-5 / 5a / 5b | SP-5, SP-7b | forgotten (or restore-rewound) replay state reopens the replay window; the two caches have different retention windows |
| RI-6 / 6a / 6b | SP-1 / SP-1a | split-before-encrypt destroys the computational belt; a public raw-split symbol bypasses the gate |
| RI-7 / 7a | SP-7a | unauthenticated **or timing-distinguishable** reconstruction delivers garbage / becomes an oracle |
| RI-8 | SP-1a, SP-7 | non-constant-time tag check → forgery oracle |
| RI-10 | I-1, I-4 | the unimplemented onion layer, built interoperably |
| RI-11 / 11a | CH-3 / CH-6, I-2 | variable-time X25519 or a reused/retained ephemeral |
| RI-9 / 9a / 9b | I-2 | heap/swap/coredump disclosure of the sub-`k` bytes |
| RI-12 | I-2, I-4 | partial/linkable artifact or un-zeroized crash unwind |

The through-line: everything that touches a sub-`k` secret value (share,
coefficient, reconstructed byte, content key, hop secret, client ephemeral) is
held to the floor's own standard — compute it in constant time (RI-1/8/11),
generate it from a sound, fork-safe CSPRNG (RI-2), persist no reusable secret
across a restart (RI-3/4/5), never let the API skip the AEAD (RI-6/7), and erase
it before it can be read back (RI-9/12). A reviewer breaks this part by finding a
real-node path on which such a value is computed in variable time, drawn from a
reused stream, repeated across a restart, surfaced unauthenticated, or left
readable in memory — and that path is then an I-2 break, not a mere hardening gap.

## 11. What this part does **not** decide

- **Networking, transport, and traffic shaping.** The chameleon transport (Part
  4), batch/mix strategy and jitter (SP-6/OP-5), and share-emission timing
  (SP-9/OP-4) are out of scope here; this part constrains the *cryptographic*
  implementation, not the scheduler. The timing-correlation residual between
  shares remains OP-4, unaddressed by any RI-n (SA-2 and this part are about
  values, not emission times).
- **Path selection and disjointness.** Verifying that `n` share paths do not share
  an AS or jurisdiction (OP-1, Part 3) is not an implementation-of-a-primitive
  question and is not required here; RI-7a only guards against *trusting* a
  lied-about `(k,n)`, not against a non-disjoint path set.
- **Sybil/eclipse and the gossip layer.** A conforming node's correct crypto does
  not by itself resist a resourceful adversary buying position (OP-2, GR-20a); that
  residual lives in Part 2 and is untouched by this part.
- **The replay structure's exact sizing and the fork-detection mechanism.** RI-5a
  bounds the replay cache to the epoch and forbids a false-negative-prone filter,
  but the concrete data structure, its parameters, and the persistence medium are
  implementation choices to be pinned against the roadmap-3.2 vectors and the
  deployment's packet volume, not fixed here.
- **Test vectors and conformance.** The vectors that certify two implementations
  interoperate — the GF tables as normative, the Sphinx per-hop derivation, the
  encrypt→split→deposit→poll→reconstruct→decrypt path — are **roadmap 3.2** and
  are referenced (RI-1b, RI-7a, RI-10, RI-11a) but not reproduced here. RI-1b is
  explicit that those vectors certify correctness, never timing; a side-channel
  test suite is a separate, recommended obligation (RI-1b) that this part asks for
  but does not specify.
- **Post-quantum primitive swap.** Suite `0x02` (a PQ hop KEM, Part 1 §5 closing)
  changes which primitive RI-11 constrains, not the requirement that it be
  constant-time; the I-2 floor is PQ-safe regardless (SP-1a), so nothing here is
  blocked on it.

## 12. Requirements introduced here

- **RI-1 / RI-1a / RI-1b / RI-1c** — constant-time GF(2⁸) multiply, inverse, and
  division, **extended to the recovered secret's whole lifetime** (the SP-8 length
  parse and all handling of a reconstructed byte), not only the field ops; vectors
  certify correctness, not timing. **[protects I-2]**
- **RI-2 / RI-2a / RI-2b / RI-2c** — CSPRNG discipline: cryptographic DRBG from the
  OS, fork/clone-safety, health checks, no injectable coefficients (test-gated, not
  shipped). **[protects I-2 via SA-3]**
- **RI-3 / RI-3a / RI-3b** — persisted, non-rolling-back `msg_nonce` high-water
  mark, fsync-before-use, **and a restore/snapshot is treated as rollback** (detect
  or retire the `kpair`). **[protects SP-7b / SP-1a]**
- **RI-4** — persisted `onion` static-epoch state and zeroizing retirement.
  **[protects CH-5 / CH-6]**
- **RI-5 / RI-5a / RI-5b** — persisted replay state for `gamma` (bounded by the key
  epoch) and `(box_id, slot)` (bounded by the **7-day slot expiry**, not the 1-day
  box rotation); a restore that rewinds a cache is a mandatory key-epoch rotation.
  **[protects SP-5 / SP-7b]**
- **RI-6 / RI-6a / RI-6b** — API refuses plaintext-without-AEAD; type-separate
  ciphertext; raw `split`/`reconstruct` are module-private. **[protects SP-1 /
  SP-1a]**
- **RI-7 / RI-7a** — fail-closed **and constant-time-reject** reconstruction;
  defensive `(k,n)` parse. **[protects SP-7a]**
- **RI-8** — constant-time AEAD and constant-time tag comparison. **[protects
  SP-1a / SP-7]**
- **RI-9 / RI-9a / RI-9b** — zeroizable storage first (pinned/native where the
  runtime forbids in-place erase), then anti-dead-store zeroization; no swap, no
  core dumps; optimizer/GC hazards. **[protects I-2]**
- **RI-10** — implement the CH-2 Sphinx per-hop derivation and replay/blinding
  discipline; vectors are roadmap 3.2. **[protects I-1 / I-4]**
- **RI-11 / RI-11a** — constant-time X25519; keyless, per-packet, zeroized
  ephemeral; reject the all-zero shared secret in constant time. **[protects
  CH-3 / CH-6 / I-2]**
- **RI-12** — fault/exception safety: no partial or linkable artifact, zeroize on
  unwind, fail closed. **[protects I-2 / I-4]**

None of these is a theorem; each is a condition under which the theorems of Part 7
and the guarantees of Parts 1–6 describe a **real node** rather than the toy. The
toy omits every one of them on purpose and says so. Break this part by naming a
real-node code path that computes, stores, or discloses a sub-`k` secret in a way
no RI-n above forbids — that path is a floor broken in practice, and finding it is
the invitation.
