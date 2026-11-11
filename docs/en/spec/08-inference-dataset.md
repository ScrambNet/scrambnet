# ScrambNet Specification — Part 8: The Inference Dataset

**Status: DRAFT, and a declared research risk.** This part decides how a client
obtains the IP-to-AS (and coarse jurisdiction) map that Part 3 infers from
(PS-4), under I-3 — no authority — against relays and dataset hosts that lie
about everything except what a hash or a signature binds. Strawman values marked
`(s)`. The map's disjointness-verification *use* is OP-1; its *distribution* is
roadmap item 2.3.

The headline decision is stated in §1 and defended through the rest. Read §1 and
§9 (the residual) first: between them they say what this part buys and what it
admits it cannot buy.

## 1. The decision, in two sentences

- **There is no canonical map and no map authority.** The dataset is a
  **reproducible, content-addressed artifact** that any party rebuilds byte-for-
  byte from public inputs; two clients agree not because they trust a signer but
  because they computed the **same hash** (ID-1, ID-5). A canonical root signed
  by a fixed set would be a directory authority under another name, and I-3
  forbids it.
- **Agreement is by reproduction; publication is by an append-only transparency
  log that anyone may write; trust at first fetch is TOFU, declared as such.**
  The log does not *bless* a map — it timestamps and makes equivocation
  detectable (ID-6, ID-7). A fresh client's first map is a trust-on-first-use
  moment that later gossip lets it **detect** as bad, not **prevent** (§7).

So the honest outcome the roadmap flagged is the real one: **TOFU map +
transparency log + anomaly gossip, not a canonical map.** Everything below is the
construction that makes "reproduce it yourself, and detect anyone who lied"
concrete, and §9 is the residual that no amount of construction removes.

## 2. Scope and the trap this part is avoiding

Part 3 (PS-4, PS-5) requires each client to infer the AS and coarse jurisdiction
of a relay *from its `addrs`*, using the client's **own** dataset, never a
relay's self-declaration (GR-3). This part is only about **where that dataset
comes from and how two clients know they hold the same one** without a trusted
party anywhere in the chain — build, publication, or bootstrap.

The trap is subtle and must be named: the easiest "trustless" design is a signed,
canonical snapshot published by a small set of maintainers. That is exactly the
Walking-Onions authority this project denied itself for relays (GR-1 scope), now
re-smuggled in for geography. A map signer who can quietly ship a map that
mislabels a block of ASes can make an adversary's co-located relays *look*
disjoint to every client — a geography-granularity eclipse that defeats Part 3
as surely as a bad relay directory would. So the signer set is the threat, and
the design must not have one with that power.

- **ID-1 (no map authority). [normative]** No step of obtaining, validating, or
  updating the dataset MUST require trusting that a particular party produced,
  signed, or blessed the map; equivalently, obtaining and validating the map
  MUST be possible using only untrusted substitutes. The only trusted
  operations are: (a) recomputing a hash, and (b) rebuilding the artifact from
  public inputs and comparing. Any
  design element that cannot be replaced by an untrusted substitute performing
  (a) or (b) is a defect under I-3 and MUST be removed or declared in §9.

## 3. What the map is

- **ID-2 (artifact shape).** The dataset is a single compressed artifact, the
  **map**, containing, for the IPv4 and IPv6 space:
  - an **IP-prefix → origin-AS** table (longest-prefix-match lookup), and
  - an **AS → coarse-jurisdiction** table, where "jurisdiction" is a
    **country-level** label derived from RIR allocation, deliberately coarse —
    finer granularity is noise this part will not pretend to resolve (§9).
  The map carries a self-describing header: format version `1`, the snapshot
  **epoch** (ID-4), the exact input manifest (ID-3), and the build-tool version.
  The artifact is addressed by `H = BLAKE2s(artifact)` (the suite hash, Part 0);
  `H` is the map's only name. There is no human-readable version string that
  could be trusted in place of `H`.
- **ID-2a (lookup is total).** Every lookup MUST return either a concrete
  `(AS, jurisdiction)` or the explicit value **`unknown`**. `unknown` is a
  first-class answer, not an error, and Part 3 (PS-5) already treats it
  conservatively (`unknown` shares with everything). The map MUST NOT guess to
  avoid an `unknown`; a fabricated answer is worse than an admitted gap, because
  it silently defeats PS-5.

## 4. How the map is built (reproducibly, from public inputs)

The build is a **pure function of named public inputs to a byte-identical
artifact**. Determinism is the whole game: if two honest parties can diverge, hash
equality (ID-5) stops meaning "same map" and the design collapses into needing an
authority to break ties.

- **ID-3 (public inputs, pinned by content). [normative]** The map MUST be built
  only from inputs that are public, reproducible, and themselves content-pinned
  in the artifact's manifest by their own hashes:
  - **BGP routing tables** for origin-AS: the **RouteViews** project collectors
    and the **RIPE RIS** collectors (MRT `RIB` dumps). These are the standard
    public, multi-vantage BGP archives; using several collectors from both
    projects is itself a diversity measure (no single collector's view is
    authoritative, ID-3a).
  - **RIR delegation statistics** for the AS → country mapping: the five RIRs'
    published **delegated-extended** files (ARIN, RIPE NCC, APNIC, LACNIC,
    AFRINIC). These give allocation country codes for AS numbers and address
    blocks without anyone self-declaring.
  The manifest MUST list every input file by URL-independent content hash and by
  its source-stated timestamp, so that the inputs — not a server — define the
  build. A party rebuilds by fetching inputs with those hashes from **any** mirror
  (I-3: the source is replaceable; the bytes are pinned).
- **ID-3a (multi-vantage origin resolution).** Origin AS for a prefix MUST be
  resolved across **all** manifested collectors by a fixed rule (ID-4b), not from
  one collector. A prefix seen with conflicting origins across vantage points is
  resolved deterministically and, where the conflict is real (MOAS — multiple-
  origin AS), recorded as a **set**, which Part 3 treats as "possibly any of
  these," i.e. conservatively shared (§9). The map MUST NOT silently pick one.

### 4.1 Determinism hazards and how the build pins them

Each hazard below is a place two honest builders could produce different bytes.
The build procedure MUST eliminate each; a build that does not is non-conforming
because it cannot support ID-5.

- **ID-4 (snapshot epoch — dump timing). [normative]** BGP and RIR data change
  continuously, so "the current dump" is not a function. The build MUST pin a
  single **epoch boundary**: a UTC instant on a fixed cadence (strawman: the
  **00:00 UTC** snapshot on a **weekly (s)** cadence — Part 0 commits already use
  UTC), and MUST use, for each manifested collector/RIR, the **last dump whose
  source-stated timestamp is ≤ the epoch boundary**. Two builders targeting the
  same epoch therefore select the same input files regardless of when they run.
  The epoch is in the artifact header (ID-2) and in `H`'s preimage.
- **ID-4a (ordering).** All tables MUST be emitted in a **fixed total order**:
  prefixes sorted by (address-family, numeric network address, prefix length);
  AS entries by numeric ASN; jurisdictions by their fixed country-code string.
  No map-iteration order, hash-table order, or input-file order may reach the
  output.
- **ID-4b (tie-breaking is specified, not implementation-defined). [normative]**
  Every place the data is ambiguous MUST have a rule written in this part, with no
  "pick one" left to the implementer:
  - *Origin AS across collectors:* take the origin set observed; if it is a
    single AS, emit it; if multiple (MOAS), emit the full set sorted ascending.
    Never collapse a MOAS to one AS by popularity — that is a guess (§9).
  - *Overlapping prefixes:* longest-prefix-match semantics are preserved by
    storing all prefixes; the lookup, not the build, resolves specificity.
  - *AS-to-country conflict across RIRs:* if the delegation files disagree on an
    AS's country, emit `unknown` for that AS's jurisdiction. A disagreement among
    public registries is exactly a case the map must not resolve by fiat.
- **ID-4c (floating inputs forbidden).** The build MUST NOT consult any input not
  in the manifest — no live DNS, no WHOIS at build time, no geolocation database
  under a licence that forbids redistribution or is not reproducible, no
  commercial IP-intelligence feed. Every byte of output traces to a hashed public
  input. (This rules out the convenient-but-unverifiable feeds; their accuracy is
  not worth the authority they reintroduce.)
- **ID-4d (canonical container).** The artifact's compression and framing MUST be
  deterministic (fixed codec, fixed level, no timestamps or filenames in the
  container metadata). The build is specified tightly enough that a conforming
  build tool is itself reproducible (roadmap 4.2), and a cross-implementation
  **map test vector** (an input manifest → expected `H`) MUST exist so a second
  implementation can prove it builds the identical artifact (ties to roadmap 3.2).

## 5. How two clients agree they hold the same map

- **ID-5 (agreement is hash equality, nothing more). [normative]** Two clients
  hold the same map **if and only if** their artifact hashes `H` are equal.
  Comparison is a 32-byte equality check; it needs no signer, no quorum, no
  authority. Clients gossip `H` (ID-8); equal `H` is proof of the same map,
  unequal `H` is proof they differ and MUST be reported to the user as a
  **divergence** (ID-9), never silently reconciled toward either side.
- **ID-5a (rebuild is the arbiter).** When two clients hold different `H` for the
  same epoch, the dispute is resolvable by **anyone**, with no appeal to
  authority: rebuild from the manifested inputs (ID-3) and see which `H` the
  public inputs actually produce. A map whose `H` cannot be reproduced from its
  stated manifest is, by definition, not the map of those inputs, and MUST be
  rejected (ID-5b). This is the property that lets the system have no authority:
  *truth is reproducibility, not signature.*
- **ID-5b (reject the unreproducible).** A client that has the inputs (or fetches
  them) and finds that `H ≠ BLAKE2s(rebuild(manifest))` MUST discard that map and
  SHOULD gossip the discrepancy as an anomaly (ID-10). A client without the
  bandwidth to rebuild MAY accept a map on TOFU/consensus terms (§6, §7) but MUST
  track it as **unverified** until it (or a peer it then agrees with) rebuilds.

## 6. The transparency log (and why it is not the authority)

Hash equality tells two clients they *differ*; it does not by itself defend
against an adversary feeding **different** clients **different** maps and keeping
each client internally consistent — a **split-view (equivocation) attack**. The
transparency log exists for exactly that threat and for nothing more.

- **ID-6 (what the log is).** The log is an **append-only Merkle tree** (RFC 6962
  / Certificate-Transparency structure: a Merkle tree over a sequence of leaves,
  with inclusion proofs and consistency proofs between two tree sizes). Each
  **leaf** is a map announcement: `(epoch, H, input-manifest-hash)`. The log's
  state is summarised by its **signed tree head** — here, a **root hash** at a
  tree size. The log proves two things cryptographically: a given `H` **is
  included** (inclusion proof) and the log **only ever grew, never rewrote
  history** (consistency proof). It proves nothing about whether `H` is a *good*
  map — reproduction (ID-5a) does that.
- **ID-7 (who may append — permissionless, so it is not an authority).
  [normative]** **Anyone** MAY append a leaf announcing a map they built; there
  is no privileged appender, no allow-list, no signer set whose signature makes a
  map official. The log is therefore **not** the thing that is trusted — it is a
  **witnessed, tamper-evident bulletin board**. Its only power is to make
  equivocation *detectable*; it has **no power to choose the map**, which is what
  keeps it clear of the I-3 prohibition. A log that gated appends behind a signer
  set WOULD be the directory authority I-3 forbids, and such a design is
  non-conforming (ID-1).
- **ID-7a (equivocation detection via gossiped roots). [normative]** The defense
  against a split view is **not** trusting the log operator; it is **gossiping the
  log's signed tree heads over the existing GR gossip channel** (GR-6) and
  demanding **consistency proofs** between any two roots a client sees. If a log
  ever presents two tree heads that are not consistent extensions of one another
  — the signature of equivocation — any client that observes both (directly or
  via a gossiped root from a peer) has **cryptographic proof** the log lied, and
  MUST treat that log as hostile (ID-10). Because roots are gossiped widely (GR-6
  mixes sources, GR-8), a log cannot show client A root X and client B root Y for
  long without some client holding both and catching it.
- **ID-7b (multiple logs, no canonical one). [normative]** There is **no single
  log.** Clients MUST support **several independent logs** and treat a map as
  log-corroborated only if it appears, with consistent gossiped roots, in a
  configurable quorum of the logs the client watches (strawman: **≥2 of the logs
  in its set (s)**). This removes the last single point: no one log operator is
  load-bearing, and a client's log set — like its relay sample — is diverse and
  replaceable (GR-8 rationale applied to logs). A log that goes dark is routed
  around, exactly as a relay that goes dark is.
- **ID-7c (the log stores commitments, not the map).** Leaves carry `(epoch, H,
  manifest-hash)` — tens of bytes — never the artifact. The map itself is fetched
  content-addressed by `H` from any mirror or peer (ID-8); the log only attests
  *which* `H` values were announced and *when*, so log storage stays trivial and
  no log becomes the distribution bottleneck.

## 7. The bootstrap paradox, stated honestly

A fresh client has no relay sample it can evaluate and no prior map; it must fetch
its **first** map over paths whose disjointness it **cannot yet verify** (that
verification needs the very map it is fetching). This is a genuine circular
dependency, and this part does not pretend to break it.

- **ID-8 (bootstrap is trust-on-first-use, declared). [normative]** The first map
  a fresh client obtains is a **TOFU** decision. The client MUST obtain it over as
  many **independent** channels as it has (strawman: the out-of-band bridge line
  of GR-10, plus two or more public mirrors reached over distinct networks (s)),
  MUST require the **same `H`** from all of them before provisionally accepting,
  and MUST record the map as **unverified-TOFU** until either (a) it rebuilds from
  inputs (ID-5a) or (b) it accumulates consistent gossiped roots and peer `H`
  agreement (ID-7a, ID-9) above a confidence threshold. The client MUST surface
  this state: *you are trusting your first map; it has not yet been corroborated.*
- **ID-8a (bound on what a bad first map buys the adversary). [normative]** An
  adversary who controls a fresh client's entire first fetch can hand it a map
  that mislabels ASes so that co-located relays look disjoint. The bound on the
  damage is three-fold and MUST be preserved by the design:
  1. **Content stays floored.** Even a fully adversarial map cannot lower the I-2
     content floor: it can only make the client *misjudge disjointness*, which
     (per PS-11 and the simulator, §10) erodes **linkage far faster than
     content** — a content break still needs the adversary on ≥`k` circuits at
     once. A bad map is a metadata attack, not a content attack. This asymmetry
     is the single most important reason the bootstrap paradox is survivable.
  2. **It is temporary and detectable, not permanent.** The moment the client
     gossips its root/`H` (ID-9) or rebuilds (ID-5a), a map that no honest peer or
     public input corroborates stands out. The adversary must keep the client
     eclipsed **forever** to keep the bad map unexposed — which is the OP-2
     eclipse problem, not a new weakness this part introduces.
  3. **It cannot forge reproduction.** The adversary can ship a bad `H`, but it
     cannot make the public inputs rebuild to that `H` (ID-5a). A client that ever
     rebuilds, or ever meets one peer who did, converges to the real map.
- **ID-8b (detect, do not claim to prevent). [normative]** This part provides
  **detection of a bad bootstrap after the fact**, not prevention of it. A
  conforming client MUST NOT present a TOFU map as verified, MUST re-evaluate it
  as gossip and (optionally) rebuild accumulate, and MUST warn if corroboration
  fails to arrive within a configurable window (strawman: a few epochs (s)). "We
  cannot prevent a bad first map; we make keeping it undetected expensive and
  eventually impossible" is the honest claim, and it is the claim the UI states.

## 8. Living with it: refresh and divergence handling

- **ID-9 (map freshness and gossip).** Clients MUST refresh toward the current
  epoch's map (ID-4 cadence) and MUST gossip their current `(epoch, H)` and the
  log roots they hold over GR-6 batches, subject to GR-8 source mixing so that no
  single class of peer can dominate a client's view of which map is current (the
  same eclipse defense, reused). A client MUST NOT weight a map by how many peers
  report it *before* applying GR-8/PS-10's "count only independently verified
  sources" rule — a sybil cannot vote a bad map into consensus by sheer numbers
  (ties to OP-2).
- **ID-9a (divergence is shown, not hidden).** When a client's `H` differs from a
  corroborated quorum (ID-7b) for the same epoch, it MUST treat its own map as
  suspect, attempt rebuild or re-fetch, and report the divergence to the user in
  Part 3's existing honesty surface (PS-9): *your view of the network's geography
  disagrees with your peers'; disjointness judgements may be wrong.* Silence here
  would let a geography-eclipse run unseen.
- **ID-10 (anomaly gossip). [normative]** Three events are **anomalies** every
  client MUST gossip when it detects them, because they are the observable
  signatures of the attacks this part cannot prevent, only surface: (a) an `H`
  that fails reproduction from its manifest (ID-5b); (b) a log that presents
  inconsistent roots, i.e. proven equivocation (ID-7a); (c) a persistent `H`
  divergence against a corroborated quorum (ID-9a). Anomaly gossip is the
  network's immune signal; a client MUST NOT suppress it to appear healthy.

## 9. The merge seam with update governance (OP-8 / item 4.1)

The map's root-publishers and the software-release signers look like they might be
one mechanism. **Position: keep them separate in trust, even if they share
tooling.** The reasoning is that they have **opposite trust shapes**:

- **ID-11 (map trust is reproduction, not signature). [normative]** The map is
  trusted because it **rebuilds from public inputs** (ID-5a); its correctness does
  **not** rest on *who* published it. A release binary, by contrast, is trusted
  because it **rebuilds from public source** (reproducible builds, roadmap 4.1/
  4.2) — also reproduction, also not signature. So the *trust anchor* is the same
  — **reproducibility, never author identity** — and the project MUST route both
  through it. But the **signer/appender sets MUST remain distinct**: binding the
  map log's appenders to the release signers would create a single roster whose
  compromise poisons *both* geography inference *and* software, i.e. exactly the
  concentrated coercion target item 4.1 is built to avoid. The map log is
  permissionless (ID-7); the release process may have a named (pseudonymous)
  signer set that only *locates* a build it cannot forge. Merging them trades the
  map's permissionlessness for the release process's roster — the wrong
  direction.
- **ID-11a (shared tooling is fine; shared authority is not).** Both MAY reuse the
  same transparency-log construction (ID-6) and the same gossip channel (GR-6) —
  sharing *mechanism* costs nothing. What they MUST NOT share is a set of parties
  whose signature is load-bearing for both, because that set would be the kill
  switch I-3 forbids, now able to flip both the map and the code.

## 10. What this part does not solve (the declared residual)

This part makes two honest clients provably agree or provably detect that they
differ. It does **not** make the map *true*. The gap between "the map every honest
client agrees on" and "where the relays physically are" is the residual, and it is
real:

- **Co-location behind disjoint prefixes is undetectable here.** An adversary who
  runs relays in one data center while announcing address space that the public
  BGP/RIR data attributes to **different** ASes will be labelled disjoint by the
  **correct** map. No reproducible build of public data can see through a
  truthful-looking BGP advertisement to the rack behind it. This is stated in the
  roadmap's deepest honest point and it stands: **from the overlay you verify
  consistency against a bounded-trust dataset, not true disjointness.** The job
  is to bound what this adversary gains (ID-8a: content stays floored; the attack
  is metadata/linkage), not to pretend it away.
- **BGP is genuinely ambiguous in places.** MOAS prefixes (one prefix legitimately
  originated by several ASes), **sibling ASes** under one operator (distinct ASNs,
  one controlling party — the map sees two ASes where disjointness-reality is
  one), and **anycast** (one prefix, many physical sites) are not dataset bugs;
  they are the territory. The map handles them conservatively (ID-3a, ID-4b:
  MOAS → set, registry conflict → `unknown`), which costs availability (more
  `unknown` ⇒ more fallback, PS-11) rather than safety. Sibling-AS detection is
  explicitly **out of scope** of a pure BGP/RIR build and is left as a declared
  blind spot: two sibling ASes are counted as disjoint when they are not.
- **Jurisdiction is coarse by decision.** Country-level RIR-derived labels are the
  floor of resolution this part commits to. Finer jurisdictional reasoning (legal
  cooperation blocs, mutual-legal-assistance reality) is deliberately **not**
  encoded — it would be a judgement call no reproducible build can make without
  importing a trusted opinion, which ID-1 forbids.

The honest summary: **the dataset's error rate is a declared, non-zero residual,
not a defect to be fixed to zero.** It is the price of refusing an authority. The
correct response is not to hide it but to feed it to the simulator and show the
user the achieved level (PS-9, PS-11).

## 11. The error rate feeds the simulator (not hand-waved)

The residual of §10 is not rhetorical; it is the exact quantity the simulator
already consumes. `poc/network_sim.py` exposes **`infer_error`** — the probability
that a client's inferred AS for a relay is **wrong** (half the time a wrong AS,
half the time `unknown`), modelling a dataset that both mis-maps and has gaps
(network_sim.py, `Network.random`). The map specified here **is** that dataset,
and its measured residual **is** that knob:

- **ID-12 (the map declares a measured error rate). [normative]** A conforming map
  release MUST ship with a **measured error estimate** — its disagreement rate
  against independent public ground-truth samples and its `unknown` fraction —
  derived reproducibly from public data, so that the number itself has no
  authority behind it. That measured pair (mis-map rate, `unknown` rate) is the
  value a client feeds to the Part 3 confidence machinery (roadmap 2.2) and the
  value the simulator sweeps as `infer_error`.
- **ID-12a (the zero-error case is the best case, never the expected one).** Per
  PS-11, the simulator's zero-error, full-view numbers are the **best** case; a
  conforming client MUST present the achieved disjointness level (PS-9) using its
  **real** map's declared error, and the UI MUST NOT quote a content-break figure
  as if it also bounded linkage (PS-11) — the asymmetry that makes a bad map
  survivable (ID-8a) is the same asymmetry the UI must not misreport as safety.

## 12. Requirements introduced here

- **ID-1** — no map authority: trust only reproduction and hashing.
- **ID-2 / ID-2a** — artifact shape (prefix→AS, AS→coarse jurisdiction),
  content-addressed by `H`; lookups total, `unknown` is first-class.
- **ID-3 / ID-3a** — public pinned inputs only (RouteViews + RIPE RIS BGP, five
  RIR delegation files); multi-vantage origin resolution, MOAS kept as a set.
- **ID-4 / ID-4a–d** — determinism: UTC epoch pins dump timing, fixed total
  order, specified tie-breaking, no floating inputs, canonical container + a map
  test vector.
- **ID-5 / ID-5a / ID-5b** — agreement is hash equality; rebuild from inputs is
  the authority-free arbiter; reject the unreproducible.
- **ID-6 / ID-7 / ID-7a–c** — permissionless append-only Merkle transparency log
  of `(epoch, H, manifest-hash)`; equivocation caught by gossiped roots +
  consistency proofs; multiple logs, no canonical one; log holds commitments, not
  the map.
- **ID-8 / ID-8a / ID-8b** — bootstrap is declared TOFU; the damage of a bad first
  map is bounded (content stays floored, it is detectable, reproduction cannot be
  forged); detect, do not claim to prevent.
- **ID-9 / ID-9a / ID-10** — refresh and gossip of `(epoch, H)` and roots under
  GR-8; divergence shown via PS-9; mandatory anomaly gossip for the three attack
  signatures.
- **ID-11 / ID-11a** — merge seam: same trust anchor (reproducibility) as release
  governance, but **separate** signer/appender sets; shared tooling yes, shared
  authority no.
- **ID-12 / ID-12a** — the map ships a measured, reproducible error estimate that
  feeds the simulator's `infer_error` knob and Part 3's confidence; the zero-error
  case is the best case, never the expected one.

ID-1, ID-5a, and ID-8a are the load-bearing three: no authority, reproduction is
the arbiter, and a bad map cannot lower the content floor. Break any of them —
find a step that needs a trusted party, a map that cannot be rebuilt from its
inputs, or a way a bad map reaches content and not merely linkage — and you have
broken this part. That is the invitation. `poc/network_sim.py`'s `infer_error`
sweep is the executable strawman behind §11; attack the model, then this text.
