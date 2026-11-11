# ScrambNet — Roadmap

**Status: living document.** This is the work plan, not a promise of dates — a
pseudonymous volunteer project moves when hands are free. It is ordered by
dependency and honesty: the items that could prove the project *wrong* come
first, because if the load-bearing claim does not hold, nothing downstream
matters. Every item names what "done" looks like so progress is checkable, not
asserted.

The six tiers below are mirrored as
[GitHub milestones](https://github.com/ScrambNet/scrambnet/milestones), with the
open-problem issues (OP-n) grouped under the tier that addresses them — a
navigable view of what is done (Tier 0 and Tier 1 are closed) and what is open.

It was built from three parallel reviews — network design, cryptography, and
security/operations — and the hardest findings are kept in plain sight rather
than smoothed over. Items reference the specification parts (`SP-n`, `GR-n`,
`PS-n`, `RZ-n`), the invariants (`I-1…I-4`), and the open problems
(`OP-1…OP-9`).

Effort scale: **S** ≈ days · **M** ≈ 1–2 weeks · **L** ≈ weeks, real design
risk · **XL** ≈ a research sub-project that may return a partial or negative
result. The last two are not failures to avoid; they are the honest shape of
unsolved problems.

---

## Tier 0 — Correct what we already know is wrong (now)

These came out of the reviews as concrete defects or overclaims. They are cheap
and they protect the project's credibility, which is its only real asset at this
stage.

- **0.1 — Reconcile public claims with proven scope.** `[claim-critical]`
  The content floor is information-theoretic **only below `k` shares**; above
  `k`, content secrecy is computational (the AEAD). And "harvest now, decrypt
  later" is defeated **only** for the below-`k` adversary — a `≥k`, record-
  everything, future-quantum adversary still breaks content *unless the
  end-to-end key agreement is itself post-quantum or pre-shared*. README,
  COMPARISON, and the threat model must state the regime (below-`k` vs above-`k`)
  and the assumption (AEAD-key secrecy) on every sentence about the floor.
  **Done:** no unqualified "information-theoretic content protection" remains in
  any public document. **Effort S.**

- **0.2 — Specify and demonstrate the end-to-end AEAD layer.** `[claim-critical]`
  SP-1 ("encrypt before dispersal") is the whole composition claim, but the PoC
  splits *plaintext* — there is no AEAD anywhere, so the composition is asserted,
  never shown. Specify the e2e layer (key establishment from the contact card's
  `kpair` vs an ephemeral exchange — a choice that decides the post-quantum
  story), and extend the PoC to actually encrypt → split → reconstruct → decrypt.
  **Done:** the PoC demonstrates SP-1 end to end; the key-establishment choice is
  made and its PQ consequence recorded. **Effort M.**

- **0.3 — Share integrity under a malicious drop.** `[soundness]`
  The SP-7 tag says *which* message a packet claims to belong to, but nothing
  authenticates the share bytes or the `k,n` byte. A single hostile drop or exit
  can flip bits in a share; Shamir cannot detect it, so `k` corrupted-consistent
  shares reconstruct to garbage (the AEAD above catches it — fail-closed — but
  this is a cheap *targeted denial of service* on a box). Decide: explicit
  per-share binding, or an accepted-and-documented fail-closed-with-retry
  residual. **Done:** a verdict with the construction if needed, written into
  SP-7. **Effort M.**

- **0.4 — Publish the project PGP key.** `[opsec, immediate gap]`
  SECURITY.md *promises* a key that does not exist. The first wave of reviewers
  (the mailing lists) has no confidential channel. Generate a pseudonym-bound
  key for `scrambnet@proton.me`, commit its fingerprint, replace the "reasonable
  time" hand-wave with a real disclosure window, and state how the key itself
  rotates (even the disclosure key must not be an irreplaceable singleton, I-3).
  **Done:** a sensitive report can be encrypted to a real, published key today.
  **Effort S.**

*(0.1's nibble-order parser bug and the UTC-epoch-boundary polling gap found in
review are already noted for the test vectors in 3.2 and the KDF item in 2.2.)*

---

## Tier 1 — Prove or break the load-bearing claim (cryptographic spine)

The project's entire differentiator is I-2. These four items, in sequence,
either establish it rigorously or reveal where it is overstated. Nothing else is
worth building until this spine holds.

- **1.1 — Formalize the encrypt-then-Shamir composition.** `[claim-critical]`
  A written theorem (or counterexample) stating *exactly* what is unconditional
  (the ciphertext is hidden below `k`, with no computational assumption) and what
  is not (the plaintext above `k` rests on the AEAD). Confirm the AEAD key never
  appears in anything a below-`k` adversary sees. **Done:** one precise sentence
  each for the unconditional and the computational tier, provably disjoint.
  **Effort M.**

- **1.2 — Prove the floor over the whole secret, not one byte.** `[claim-critical]`
  The PoC's brute-force demo covers a *single byte*; the property tests check
  only a marginal. Prove joint independence of any `k−1` shares over the full
  secret (standard, given independent uniform per-position coefficients), and add
  a test that would fail under coefficient reuse or a low-entropy RNG. Document
  **"coefficient randomness is floor-critical"** as a first-class requirement.
  **Done:** cited joint-independence proof + a test that catches RNG failure.
  **Effort S–M.**

- **1.3 — SP-7 tag: replay, forgery, cross-drop linkability.** `[soundness]`
  The property that must not fail: two shares of one message must never carry an
  equal observable value across colluding drops. Shares to distinct drops use
  distinct indices, so tags differ — *prove* no `(nonce, index)` pair is ever
  reused across drops, or fix it. Plus: nonce-ownership rules (a reused
  `msg_nonce` both collides tags and breaks the AEAD catastrophically), and
  storage-layer replay/eviction defenses. **Done:** proof sketch of no-equal-tag,
  nonce discipline written into SP-7, replay handled at the drop. **Effort M–L.**

- **1.4 — Unify the rendezvous key-derivation discipline.** `[soundness]`
  Today `K_tag` comes from HKDF-BLAKE2s but `box_id` from raw keyed BLAKE2s, both
  on the same `kpair` — unprincipled. Derive one master PRK from `kpair`, then
  label-separated sub-keys. Specify the **UTC-epoch-boundary grace rule** (a
  sender depositing at 23:59 and a recipient polling at 00:01 must not miss mail —
  a real delivery bug). Justify the 16-byte `box_id` width. **Done:** one KDF
  discipline, the epoch grace rule, regenerated vectors. **Effort M.**

---

## Tier 2 — The central network problem (OP-1) and its apparatus

The floor is only *operationally* real if the `n` paths are genuinely disjoint.
Verifying that from a client's own data — against relays that lie about
everything except their signatures — is the project's stated central problem.
The deepest honest point, which the deliverables must state out loud: **from the
overlay you cannot verify *true* disjointness, only consistency against a
bounded-trust dataset; an adversary that co-locates relays while advertising
disjoint prefixes is likely undetectable.** The job is to bound what that
adversary gains, not to pretend it away.

- **2.1 — Simulator realism pass.** `[keystone]` **DONE.**
  `network_sim.py` now separates *ground truth* (which the adversary exploits)
  from the client's *belief* (a noisy, gap-ridden inference dataset), with an
  injectable inference-error rate exercising "unknown ⇒ assume shared"; adds
  **persistent guards** across a message stream, a **partial gossip sample** per
  client, and an **AS-level adversary** that counts the drop as an exit vantage.
  The demo prints break and linkage curves vs inference error (both rise
  monotonically; linkage erodes far faster than content, the honest shape of the
  gap) and vs gossip fraction (a thin view forces fallback, where break jumps).
  Written up as PS-11. `test_network_sim.py` locks the belief-vs-truth
  separation. The zero-error, full-view numbers are now visibly the best case,
  not the expected one. **Effort L.** Unblocks almost everything below.

- **2.2 — Draft the Part 3 verification procedure.** `[flagship]`
  The expansion the OP-1 issue asks for: given a sample, an inference dataset, and
  per-relay confidence, produce `n` circuits **and a machine-checkable
  certificate of the disjointness level achieved, with a confidence** — never an
  assumption. State the limit honestly ("disjoint under dataset D with D's error
  bars"), and name the co-location-gaming adversary as a declared residual,
  quantified by 2.1. **Done:** a hostile implementer can build the selector from
  the text; every threshold cites a simulator figure. **Effort L.** Depends on
  2.1 and 2.3.

- **2.3 — The trustless IP-to-AS inference dataset.** `[research risk]` `I-3`
  **DONE — written as spec Part 8 (ID-1…ID-12a).** The research risk resolved
  the way the roadmap flagged: **not** a canonical signed map (its signer set is
  a directory authority by another name, I-3-forbidden), but a **reproducible,
  content-addressed artifact** rebuilt byte-for-byte from pinned public inputs
  (RouteViews + RIPE RIS BGP, five RIR delegation files) — two clients agree by
  equal `BLAKE2s` hash, and **reproduction, not signature, is the authority-free
  arbiter**. Published via a **permissionless** append-only Merkle transparency
  log (RFC 6962-style) whose gossiped roots + consistency proofs make split-view
  equivocation detectable; multiple logs, none canonical. Bootstrap is declared
  **TOFU** (detect, don't prevent); a bad first map is bounded — it erodes
  linkage, never the I-2 floor, and cannot forge reproduction. Merge seam with
  4.1: same trust *anchor* (reproducibility) but **separate** signer/appender
  sets. The declared residual (§10): an adversary co-locating relays behind
  truthfully-disjoint BGP prefixes is labelled disjoint by the *correct* map —
  a non-zero error rate the map **measures and ships**, feeding the simulator's
  `infer_error` (ID-12). **Effort XL.**

- **2.4 — Discovery robustness: sybil and eclipse (OP-2).**
  Model the sampled view under GR-6/GR-8 with per-source-class adversary
  fractions, churn, and the "no class > ½" cap; implement eclipse and sybil
  adversaries; check whether PS-10's "count only verified relays" actually blunts
  sybil size-inflation. Then specify the bandwidth-probing protocol (GR-7) — a
  probe that measures a relay without revealing the prober or becoming a DoS
  amplifier, the hard replacement for Tor's bandwidth authority we denied
  ourselves. **Done:** eclipse-probability and sybil-inflation curves; a
  buildable probe spec. **Effort L.**

---

## Tier 3 — Harden the constructions for a real implementation

- **3.1 — Reference-implementation crypto requirements. (DONE)** `[soundness]`
  What a real node must do that the toy omits, each tied to a threat, is now
  spec **Part 9** (`RI-1..RI-12`), built on one principle: an information-theoretic
  floor is only as unconditional as the code that computes it, so a timing or
  memory-disclosure side channel that reveals sub-`k` secret bytes is a break of
  I-2 itself, not a permitted computational one. Covers **constant-time GF(2⁸)**
  extended to the recovered secret's whole lifetime (the PoC's table lookups are a
  cache-timing channel on secret share bytes), **CSPRNG discipline** incl.
  fork/clone/snapshot-safety (the floor is exactly as strong as the coefficient
  RNG, SA-3), nonce + onion-static rotation across restarts **and snapshot
  restores**, replay-cache persistence (two caches, two retention windows),
  misuse-resistance (the API MUST refuse plaintext-without-AEAD and fail closed in
  constant time), the real-node Sphinx layer (constant-time X25519, keyless
  ephemeral, all-zero-secret rejection), and memory zeroization (zeroizable storage
  first, since a bare erase is impossible for CPython `bytes`). An adversarial
  review found two conforming-but-insecure paths (a recovered-secret timing leak
  past the field ops; nonce reuse after a snapshot restore) and a Python-impossible
  zeroization MUST; all three fixed before publication. **Done.** **Effort L.**

- **3.2 — Formal test vectors and cross-implementation conformance. (DONE)** `I-1`
  `vectors.json` now covers every keyed construction with a reference output a
  second implementation must reproduce: **HKDF-BLAKE2s** (the PRK under
  `content_key`/`k_tag`/`box_id`), **box ids across epochs** (`rendezvous`), the
  **full content path** `e2e_dispersal` (encrypt → split → reconstruct → decrypt,
  pinning the composition, not only its parts), **Ed25519 + canonical-CBOR
  records** (Part 2 §2A, positives and negatives — done in 3.4), the **GF tables
  pinned normative** (`gf_tables`, by hash and in full), and the **`k,n` nibble
  order vector-locked** (`params = (k<<4)|n`; the two PoC parsers once disagreed).
  The **Sphinx per-hop derivation** (CH-2) is **declared pending** rather than
  hand-waved — the toy implements no onion layer, so its vectors cannot be
  generated honestly yet; `test_vectors.py`'s coverage guard ensures they cannot
  be added later without a conformance check. `poc/test_vectors.py` is the
  conformance harness (it asserts every section reproduces *and* that no section
  lacks a check); `poc/CONFORMANCE.md` documents what a second implementation must
  reproduce; the generators are deterministic. 101 tests. **Done:** the vectors
  and the harness exist; a second implementation in another language passes every
  vector by construction. **Effort M.**

- **3.3 — Resolve the circuit handshake: Noise XK is deleted. (DONE)**
  The suite named `Noise_XK_25519_ChaChaPoly_BLAKE2s` but nothing specified it,
  and Sphinx already does per-hop key agreement — so **what was Noise XK for?**
  The answer, after an adversarial review that tried and failed to name a circuit
  operation Sphinx cannot perform, is **nothing**: the keyless ScrambNet client
  has no initiator static for XK to hide, so a second handshake only re-ran the
  same DH, added round-trips, and put a second wire format on the link (I-4). It
  is removed. The circuit handshake **is** the Sphinx header, now specified to
  I-1 completeness in Part 1 §5 (CH-1..CH-9): ephemeral(client)·static(relay) DH,
  forward-secret at epoch granularity with a ≤7-day static-key exposure window
  (CH-6), and the one regression the deletion costs — a late static seizure
  exposing one hop's linkage within the live epoch — bounded and closable without
  a handshake (CH-5a). **Done.** **Effort L.**

- **3.4 — Gossip-record signatures and canonical CBOR. (DONE)** `I-1`
  Canonical CBOR is signature-critical: two implementations that disagree on a
  record's canonical bytes reject each other's valid records. Part 2 §2A
  (GR-21..GR-30) pins both halves to the byte: the **canonical-CBOR profile**
  (shortest-form, definite-length, four major types, ascending unsigned-integer
  keys — which, because shortest-form makes bytewise order equal numeric order,
  is totally pinned even for unknown keys — duplicate-key rejection, the inner
  shape of keys 0–7, and *verify over the received bytes* rather than
  re-canonicalize); and the **strict Ed25519 profile** (RFC 8032 cofactorless
  `[S]B = R + [k]A`, canonical `S < L`, canonical point encodings, and
  prime-order `A`/`R` tested by `[L]P = 𝒪 ∧ P ≠ 𝒪` — *not* a small-order
  blacklist, which would admit the mixed-order points on which cofactored and
  cofactorless verification diverge). An adversarial review found the `addrs`
  shape unpinned, the prime-order test under-specified (a blacklist passes
  small-order but splits on mixed-order), a vector realizability gap, and a
  GR-2↔GR-24 signing-input contradiction; all fixed before landing. Reference
  implementation `poc/gossip.py` (pure-Python, stdlib only, Ed25519 cross-checked
  bit-for-bit against an independent library), cross-impl vectors in
  `vectors.json` `records` (1 positive + 1 unknown-key + 13 negatives, each
  tagged with the GR-clause it trips), `test_gossip.py` (12 tests, 89 total).
  **Done:** canonicalization pinned, vectors exist. **Effort S.**

---

## Tier 4 — Governance and operations (protects the project now and users later)

The reviews agreed on one framing: the project has **no users yet**, which is a
gift — the governance and build-trust skeleton can be laid down calmly *now*,
while changing it breaks no one. The expensive mistake is to ship a reference
node with an ad-hoc update story and then need an authority-shaped migration to
fix it.

- **4.1 — Update governance without a kill switch (OP-8).** `[most important non-crypto item]`
  A design-decision record fixing the *shape*: reproducible builds are the trust
  anchor; signatures only *locate* a build; update adoption is client-local and
  opt-in, never a push. The hard 80% is human, not cryptographic — *who* signs,
  how they are chosen and replaced pseudonymously, and how a quorum avoids quietly
  becoming the directory authority I-3 forbids. **The strongest answer may be
  minimalist:** reproducible builds + cross-published hashes + *no* auto-update
  and *no* authoritative signer set, because every signer set is a coercion
  target. **Done:** the document survives a hostile reading hunting for the
  back-door authority; the I-3 self-audit names the untrusted substitute for
  every party. **Effort L.**

- **4.2 — Reproducible-build pipeline and supply chain.** `I-1, I-3`
  Design (ready for when the Rust node starts): toolchain pinning, a hermetic or
  Nix-style build, a `rebuild-and-compare` a stranger can run, cross-published
  attestations, a minimal and vendored dependency tree, and the explicit
  reconciliation of "contributors must be pseudonymous (no identity-bound signing
  keys)" with "verify the artifact" — all trust flows through reproducibility,
  none through author identity. **Done:** two parties on different machines
  produce hash-identical artifacts from the tagged source, via a procedure naming
  no trusted singleton. **Effort L.**

- **4.3 — Dead-drop economics and retrieval metadata (OP-9).**
  Simulate a flooding attack with a price tag (client puzzles vs the RZ-7 caps),
  honest about the gap that a puzzle hard enough to deter a botnet may be
  unaffordable on the cheap phone the project claims to serve. Simulate the
  polling discipline (RZ-9) against a drop that *profiles* a box, and its cost on
  metered mobile. **Done:** defended parameters with the residual stated in
  numbers. **Effort M.**

- **4.4 — Operator exposure and the neutrality posture.** `[politically fraught]`
  An honest (not legal-advice) brief on what running each role reveals and risks,
  leaning on the true claim that a drop stores unreadable noise and a relay
  forwards fixed-size noise with no clear-web exit; plus a written abuse-handling
  posture — what the project will and will not do when the network is used for
  harm, given that it *cannot* read or target content by design, and why that
  inability is a security property, not an evasion. **Done:** each role has a
  plain-language exposure statement; the posture is consistent with the
  neutrality clause and introduces no moderation lever. **Effort M.**

---

## Tier 5 — The layers still unwritten

- **5.1 — Chameleon transports (Part 4, OP-7).** `[arms race]`
  A transport threat model and an honest realism assessment: uTLS fingerprint
  drift, ECH's 2026 deployment reality, active probing, flow correlation. The
  "blocking me costs more than it earns" economic argument has real historical
  counter-examples — name them, and ask the uncomfortable question of whether a
  pseudonymous volunteer project has the *sustained-maintenance* capacity an arms
  race demands. Resolve whether share-dispersal across diverse covers *helps*
  (more cover types) or *hurts* (more fingerprints to get wrong). **Effort L.**

- **5.2 — Blackout / mixed-mesh link diversity (Part 5, OP-6).** `[research risk]`
  The largest unwritten design: phones as battery-bound leaves, dual-radio
  PCs/SBCs as an 802.11s backbone, and **dispersal across independent gateways**
  extending I-3 to the physical neighborhood exit. The hard parts: addressing
  without global reachability; verifying gateway independence when the AS map is
  unreachable inside a blackout and location is self-declared (OP-1 recurs in
  radio space); whether the 2048-byte Sphinx packet survives hours-long
  store-and-forward or needs its own framing. And the irreducible residual to
  state, not solve: **a mesh node in a hot blackout is a physically locatable
  act** no overlay can hide — so mesh participation is always an explicit opt-in.
  **Effort XL.**

---

## The same problem wearing three masks

One finding recurred across all three reviews and deserves to be named: the
inability to **verify a party's independence without self-declaration** appears
for *relays* (OP-1 path disjointness), for *release signers* (OP-8 jurisdictional
diversity), and for *mesh gateways* (OP-6 physical independence). A solution to
one may transfer to the others. It is, arguably, the deepest open problem in the
whole project — and the honest answer in each case may be a *bounded, declared
residual* rather than a verification. That is consistent with the one rule above
all the others here: **state where the umbrella ends.**

---

## Suggested critical path

**Done:** Tier 0 (0.1–0.4) — overclaims reconciled to the two-tier regime,
the e2e AEAD implemented, the share-integrity verdict (SP-7a) written, the
project PGP key published. Tier 1 (1.1–1.4) — the spine holds: Part 7 proves
the floor (SA-1…SA-4), the coefficient-randomness and key-separation conditions
are stated and tested, SP-7b nails no-equal-tag and nonce ownership, and one
KDF discipline plus the UTC-epoch grace rule (RZ-13/RZ-14) are in. The
load-bearing claim I-2 is now argued, not asserted; the invitation is to break
Part 7.
**Next:** Tier 2 — 2.1 (simulator keystone) and 2.3 (the XL dataset, started
early) → 2.2 (flagship Part 3 verification); 4.1 (governance) and 4.2
(reproducible builds) can proceed independently at any time.
**Closing out:** 2.4, Tier 3 hardening, Tier 4 economics, then the unwritten
Tiers 5.1 and 5.2.

Two items carry a real chance of a *partial or negative* result — 2.3 (trustless
reproducible BGP data may not be fully achievable) and 5.2 (invariant-preserving
mesh may be only partly reachable). That is not a reason to defer them; it is the
reason to be honest about them in a document that promises no acts of faith.
