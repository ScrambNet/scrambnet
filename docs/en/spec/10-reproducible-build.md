# ScrambNet Specification — Part 10: Reproducible Build and Supply Chain

**Status: DRAFT.** This part decides how a party obtains a ScrambNet **binary**
it can trust *without trusting whoever built it*, under I-3 — no authority —
against a project whose contributors are **pseudonymous** and therefore carry no
identity a user could verify. It is the software analogue of Part 8: there, a
*map* is trusted because it rebuilds from public inputs; here, a *binary* is
trusted because it rebuilds from public source. Strawman values are marked `(s)`.

Part 9 says *what the node's code must do*; this part says *how that code becomes
a binary you can verify you are running*. Read §1 and §10 first: between them they
say what this part buys (reproduction, not signature, as the arbiter) and what it
admits it cannot buy (a backdoor in faithfully-reproduced source; a
reproducibly-miscompiling compiler; and, for the user who cannot rebuild, a
reduction to OP-2 — the same reduction Part 8 ends on).

This part decides reproducibility as the trust **anchor**. It does **not** decide
*who signs a release or how signers are chosen and replaced* — that is item 4.1
(OP-8), a separate part. The seam between them is §9, and it mirrors Part 8's
ID-11/ID-11a by citation.

## 1. The decision, in two sentences

- **There is no release authority.** A ScrambNet binary is a **reproducible,
  content-addressed artifact** that any party rebuilds byte-for-byte from tagged
  public source and pinned public inputs; two parties agree a binary is honest
  not because a trusted party signed it but because they computed the **same
  `BLAKE2s`** (RB-1, RB-9). A binary blessed by a fixed signer set would be a
  release authority under another name, and I-3 forbids it.
- **Agreement is by reproduction; signatures only *locate* a build, they never
  *authorize* it; trust in a build the user cannot itself reproduce reduces to
  corroboration-by-count, which is OP-2.** This is the honest shape and it is
  stated up front, not buried: for the party with a build machine, reproduction
  carries the whole trust; for the phone that cannot rebuild — the modal user —
  trust rests on a count of independent reproducers, exactly as Part 8's
  non-rebuilding client rests on a gossiped quorum (RB-7b, §10).

So the honest outcome is the same one Part 8 reached for the map: **reproduce it
yourself and the trust is authority-free; cannot reproduce it, and you are back to
a corroboration quorum subject to OP-2.** Everything below makes "reproduce it
yourself, and detect anyone who lied" concrete, and §10 is the residual that no
amount of construction removes.

## 2. Scope and the trap this part is avoiding

A pseudonymous project cannot ask the user to trust its authors — there is no
author to trust. The naive "trustless" design is a binary signed by the project's
maintainers; that re-imports precisely the authority I-3 denies. The trap: a
signer who can quietly ship a malicious binary under a trusted key is the kill
switch item 4.1 exists to avoid. So trust must not flow through *who signed*; it
flows through *does it rebuild*.

- **RB-1 (no release authority; reproduction is the arbiter). [normative]** No
  step of obtaining or validating a build MUST require trusting that a particular
  party compiled, signed, or blessed it. The only trusted operations are (a)
  recomputing `BLAKE2s`, and (b) rebuilding the artifact from tagged source and
  pinned inputs and comparing. Any design element that cannot be replaced by an
  untrusted substitute performing (a) or (b) is a defect under I-3 and MUST be
  removed or declared in §10. (Operation (b), rebuild-and-compare, is trusted
  **modulo** the toolchain residual: running the build executes the pinned
  compiler, which RB-3b declares a trusting-trust residual — rebuild reduces trust
  to the compiler, it does not eliminate it. RB-1 is the two-operation claim, read
  with that cross-reference, not without it.)
- **RB-2 (reproducibility authorizes; signatures only locate). [normative]** This
  part decides nothing about *who signs a release or how signers are chosen and
  replaced* — that is item 4.1. A signature over a build, if one exists at all,
  MUST be treated as a **locator** ("a build with this `H_build` was announced
  here, then, by this pseudonymous hand"), never as an **authorization** ("this is
  the build to run"). A conforming client MUST NOT adopt a build *because* it was
  signed; *which* build to adopt is item 4.1's concern and is client-local and
  opt-in. Binding build-honesty to a signer set re-imports the authority I-3
  forbids (the ID-11a rule, for software).
- **RB-2a (shared tooling, not shared authority).** This part MAY reuse Part 8's
  transparency-log construction (ID-6) and the GR-6 gossip channel to publish and
  gossip build hashes (RB-14) — sharing *mechanism* costs nothing (ID-11a). It
  MUST NOT share with the map a set of parties — **signer or log-appender roster**
  — whose role is load-bearing for both the map and the code, because that set
  would be the kill switch I-3 forbids, now able to flip both geography inference
  and software. The shared log introduces no authority **because** both parts
  route trust through reproduction, not the log, and the log stays permissionless
  (ID-7).

## 3. The toolchain, pinned by content

- **RB-3 (the toolchain is pinned by content, not by channel name). [normative]**
  The build MUST pin an *exact* toolchain — a specific stable release (strawman:
  `rust 1.xx.y` in `rust-toolchain.toml` with `channel = "1.xx.y"`, never
  `stable`/`latest`/`beta`/`nightly`) — **and** pin that toolchain's binary
  artifacts by `BLAKE2s` in the build manifest (RB-8). "The toolchain" is a set of
  hashed bytes, not a name a mirror can resolve differently. A rebuilder fetches
  the toolchain from **any** mirror and verifies the hashes (I-3: the distributor
  is replaceable; the bytes are pinned — the ID-3 pattern applied to the
  compiler).
- **RB-3a (pin the whole compile surface).** The pin MUST cover every tool whose
  output reaches the artifact: `rustc`, `cargo`, the `std`/`core` prebuilt
  libraries actually linked, the linker (strawman: a pinned `lld`/`mold` (s), not
  the host's ambient `ld`), the libc/sysroot, and any tool a `build.rs` invokes. A
  tool left to the host is an unpinned input and a determinism hazard (RB-6, RB-18).
- **RB-3b (the compiler is a fetched binary — trusting-trust is a declared
  residual). [normative]** The pinned `rustc` is a *fetched binary*, not something
  this pipeline builds from source. Trusting it is a **declared residual** (§10,
  trusting-trust): RB-3 pins *which* compiler bytes everyone uses, so all
  rebuilders share the *same* residual and any *substitution* is detectable by
  divergence; it does **not** make the compiler honest. Pinning proves
  **provenance**, not **honesty** (see RB-18). A bootstrap-from-source or
  diverse-double-compilation path, if ever adopted, is named as future work, not
  required here.

## 4. The hermetic build

The build is a **pure function of the manifest to a byte-identical artifact**.
Determinism is the whole game: if two honest builders can diverge, hash equality
(RB-9) stops meaning "same binary" and honest builders get flagged as an attack
(RB-7, RB-15) — the Part 8 lesson (ID-4 preamble), un-learned here would be fatal.

```
  THE BUILD IS A PURE FUNCTION OF THE MANIFEST (RB-8)

  ┌──────────────────────── manifest (RB-8) ────────────────────────┐
  │  source commit/tag · toolchain hashes (RB-3) · every dependency  │
  │  content hash (RB-5) · fixed environment (RB-4b) · target triple │
  │  · SOURCE_DATE_EPOCH (derived, RB-4b) · expected H_build         │
  └────────────────────────────┬────────────────────────────────────┘
                               ▼
            ┌─────────────────────────────────────────┐
            │  HERMETIC BUILD (pure fn, RB-4)          │
            │  no network (RB-4a), no ambient host     │
            │  state, fixed env (RB-4b), nondeterminism │
            │  eliminated per the pinned hazard set    │
            │  (RB-6, versioned by toolchain)          │
            └───────────────────┬─────────────────────┘
                               ▼
                    artifact (for ONE target triple)
                               │
                               ▼
              H_build = BLAKE2s(artifact)   ← the build's ONLY name (RB-6a)
                                              defined per (source, manifest,
                                              target triple) — RB-6b

  Alice ─ same manifest, same triple ─▶ H_A     Two honest builders agree by
  Bob   ─ same manifest, same triple ─▶ H_B     equal H_build. Reproduction is
                                                 the arbiter (RB-7), not a signer.
```

- **RB-4 (hermetic, offline, ambient-free build). [normative]** The build MUST run
  with **no network access** and **no ambient host state**: no reading of `$HOME`,
  host environment variables (beyond an explicit allow-list, RB-4b), the system
  clock for any embedded value, user/group names, hostname, CPU-count where it
  would affect output, or any path outside the sandbox. Conforming substrates: a
  Nix/`crane`-style pure derivation, **or** a container/`bwrap` sandbox with the
  network namespace removed and a fixed minimal environment. This part specifies
  the **properties** and mandates neither substrate (I-1: a hostile implementer
  builds a conforming builder from the properties); Nix and a sandboxed container
  are named as the two reference-conforming substrates. A party that adopts a
  substrate MUST pin *it* too (a Nix toolchain is itself an RB-3 pin).
- **RB-4a (no build-time network fetch, ever). [normative]** The build MUST NOT
  fetch anything — no registry access, no git dependency resolution, no `build.rs`
  download, no toolchain pull. Every fetch happens *before* the hermetic step,
  pinned by hash, and is handed in through the manifest. A build that *can* reach
  the network is non-conforming even if it happens not to use it, because its
  determinism then depends on a server (the ID-4c floating-inputs prohibition, for
  software).
- **RB-4b (fixed, declared, derived environment). [normative]** The build
  environment MUST be fixed in, and only in, the manifest: locale `C`/`C.UTF-8`,
  `TZ=UTC`, umask, the env allow-list, and `SOURCE_DATE_EPOCH`. `SOURCE_DATE_EPOCH`
  MUST be **derived deterministically from the tagged commit** (the committer date
  of the pinned tag), so it is a function of a pinned input, not a free-floating
  manifest assertion a builder could set at will. A forged committer date is not a
  silent win: it changes `H_build` and is therefore caught by divergence (RB-7),
  exactly as any other input change is.

## 5. The dependency tree

- **RB-5 (minimal, audited, vendored, content-pinned dependency tree).
  [normative]** Dependencies MUST be (a) *minimized* — each one justified against
  not having it, because every crate is an untrusted author in the trust chain
  (RB-16, OP-10); (b) *vendored* — the exact source of every transitive dependency
  pinned into the build inputs, not resolved live (RB-4a); and (c) *pinned by
  content* — `Cargo.lock` committed, **and** every crate additionally pinned by
  `BLAKE2s` of its source in the manifest (RB-8), not trusted to the registry's own
  checksum alone. A registry that can change bytes under a name is an authority;
  the content hash removes it and makes the registry a replaceable CDN.
- **RB-5a (the lockfile is necessary, not sufficient).** `Cargo.lock` pins
  versions and registry checksums; it does not by itself make the *build*
  reproducible (feature unification, `cfg`, host differences still bite — RB-6)
  nor remove trust in the registry. RB-5's content-pin and RB-4's hermeticity close
  that gap. A build that pins only the lockfile is non-conforming.
- **RB-5b (build scripts and proc-macros are trusted compute, not inert data).
  [normative]** `build.rs` scripts and procedural macros execute arbitrary code
  *at build time*; they MUST run inside the RB-4 sandbox under the same
  no-network/no-ambient rules, and they are in scope for the RB-16 audit exactly as
  runtime code is. A proc-macro that reads the clock or the network is a
  determinism hazard and a supply-chain surface in one.

## 6. Determinism hazards and how the build pins them

Each hazard below is a place two honest builders could produce different bytes.
The build MUST eliminate each; a build that does not is non-conforming because it
cannot support RB-9, and its divergence is mis-read by RB-7 as an attack.

- **RB-6 (the hazard set is normative, versioned by toolchain). [normative]** The
  build MUST eliminate every hazard in the **pinned hazard set** for the toolchain
  version in use. This set is normative-as-of-a-pinned-toolchain, not forever
  (residual §10.7: determinism is a moving target against toolchain churn), and the
  manifest MUST reference the hazard-set version it was built against. The set at
  minimum MUST pin:
  - **timestamps** — `SOURCE_DATE_EPOCH` from the tagged commit (RB-4b); no mtimes
    in any emitted archive;
  - **build paths** — `--remap-path-prefix` to a fixed `/build` root, so no
    absolute path, `$HOME`, or user name is embedded in debug info or panic
    strings;
  - **parallelism and ordering** — codegen-unit ordering, link order, symbol-table
    order, archive-member order, and any hash-map iteration order that reaches
    output MUST be made deterministic (fixed or sorted);
  - **`-C metadata` / `-C extra-filename` derivation** — derived deterministically
    from pinned inputs, never from a host-varying value;
  - **locale/encoding** — `LC_ALL=C`;
  - **debug-info and symbols** — deterministic, or stripped; if kept, deterministic;
  - **randomized layout and seeds** — `-Z randomize-layout` off; any RNG-seeded
    codegen pinned;
  - **the archive/package framing** — a fixed codec at a fixed level, with no
    filenames, timestamps, or uid/gid in container metadata (the ID-4d canonical-
    container rule, for software packaging).

  The analogue of Part 8's un-pinned decode hazard (ID-4d §10 note) applies here
  and is named, not hidden: **LLVM-version-dependent codegen and host-dependent
  `cfg`/feature unification** (admitted in RB-5a) are reproducible only *as of the
  pinned toolchain and the pinned feature resolution*; each toolchain bump is a
  fresh determinism-audit obligation (§10.7), not a free ride.
- **RB-6a (the artifact is content-addressed; `H_build` is its only name).
  [normative]** The release artifact is addressed by `H_build = BLAKE2s(artifact)`
  (the suite hash, Part 0). `H_build` is the build's only authoritative name; a
  human-readable version string (`v1.2.3`) is a convenience label and MUST NOT be
  trusted in place of `H_build` (the ID-2 "hash is the only name" rule). Freshness —
  *which* version a client should run — is a separate property, carried by RB-8a,
  not by the version string.
- **RB-6b (`H_build` is per-target; agreement is defined within a triple).
  [normative]** A release reproduces to *different* bytes per target
  (`aarch64-linux-android`, `x86_64-unknown-linux-gnu`, `armv7-…`, …) from the
  *same* source, so `H_build` is a function of **(tagged source, manifest, target
  triple)**. The manifest MUST pin the target triple; agreement (RB-9) is defined
  **only within a fixed triple**; and RB-7/RB-15 MUST compare only like-triple
  `H_build`. A client comparing its own-triple hash to a different-triple published
  hash MUST NOT raise a build-divergence anomaly — that is a category error, not an
  attack. The part also pins exactly which bytes `H_build` covers for each shipped
  artifact (the node binary, and separately any installer or library), so two
  rebuilders hash the same object.

## 7. How two parties agree they hold the same binary

- **RB-7 (a stranger's rebuild-and-compare procedure). [normative]** The procedure
  a party with *no relationship to any contributor* runs to obtain a bit-identical
  artifact and verify it:
  1. fetch the tagged source and the manifest (RB-8) from **any** mirror;
  2. verify every input against its manifest `BLAKE2s` (RB-3, RB-5);
  3. run the hermetic build (RB-4) for the target triple (RB-6b);
  4. compute `H_build`;
  5. compare by `BLAKE2s` equality to the published hash (RB-14) and to any peer's
     same-triple hash.

  Equal `H_build` is proof of the same binary; unequal is proof they differ and
  MUST be surfaced as a **build divergence** (RB-15), never silently reconciled. The
  dispute is resolvable by anyone with no appeal to authority: rebuild and see what
  the public source produces (the ID-5a arbiter, for software). This is the 4.2
  "done" criterion: two parties on different machines produce hash-identical
  artifacts from the tagged source via a procedure naming no trusted singleton.
- **RB-7a (a non-reproducing release is rejected, not patched over). [normative]**
  A released artifact whose `H_build` cannot be reproduced from its stated manifest
  is, by definition, not the build of that source: a conforming verifier that *can*
  rebuild MUST reject it and SHOULD gossip the discrepancy as a build anomaly
  (RB-15). "It builds on the maintainer's machine but nowhere else" is a
  reproducibility failure — a defect — not an acceptable state (the ID-5b rule, for
  software).
- **RB-7b (the client that cannot rebuild — the modal user). [normative]** Almost
  every real user runs the client on a phone with no toolchain, no disk, and no
  bandwidth to compile the dependency tree; it *cannot* perform operation (b) of
  RB-1. Such a client MUST track every binary it runs as
  **`reproduced-by-others-unverified`** until it (or a peer whose `H_build` it then
  matches) rebuilds, MUST treat corroboration as a count of **independently
  verified** reproducers under the RB-10 rule (never a raw attestation tally), and
  the part states plainly: **for the non-rebuilding client, build-trust does not
  flow from reproduction — it reduces to corroboration-by-count, which is OP-2**,
  exactly as Part 8's map-trust reduces to OP-2 for the non-rebuilding map client
  (§10, ID-5b/§10). The client MUST surface this state; it MUST NOT present an
  unrebuilt binary as if the user had verified it.

## 8. The manifest, agreement, and freshness

- **RB-8 (the manifest is the reproduction recipe). [normative]** Every release
  MUST ship a **manifest**: the source commit/tag, the pinned toolchain hashes
  (RB-3), every dependency's content hash (RB-5), the fixed environment (RB-4b),
  the target triple (RB-6b), `SOURCE_DATE_EPOCH` (derived, RB-4b), the hazard-set
  version (RB-6), and the expected `H_build`. The manifest — not a server, not a
  person — defines the build (the ID-3 manifest, for software).
- **RB-8a (the manifest is canonical and content-addressed; freshness is a
  checkable field). [normative]** The manifest MUST have a **canonical
  serialization** (reuse the Part 2 canonical-CBOR profile, GR-21..GR-30) and is
  itself content-addressed by `manifest-hash = BLAKE2s(canonical manifest)`;
  otherwise two honest parties produce different manifest-hashes for the same
  recipe and log corroboration (RB-14) splits on a formatting difference — the
  GR-21 lesson un-learned. The manifest MUST carry a **monotonic release index**
  bound together with the derived committer date, and the transparency-log leaf
  (RB-13) MUST preserve that ordering, so that *recency* is a checkable property of
  the artifact. This closes the seam gap with 4.1 that 4.1 cannot close later (the
  manifest schema is a 4.2 artifact): see RB-9a.
- **RB-9 (agreement is hash equality, nothing more). [normative]** Two parties hold
  the same binary **if and only if** their same-triple `H_build` are equal (RB-6b).
  Comparison is a 32-byte check; it needs no signer, no quorum, no authority (the
  ID-5 rule, for software).
- **RB-9a (reproducibility proves binary-matches-source, not source-is-current —
  the freshness residual). [normative]** `H_build` authenticates *that the bytes
  match the source*; it says nothing about *which source is the one to run*. A
  **reproducible-downgrade attack** — feeding a client an old tag with a known
  vulnerability, which reproduces perfectly and passes every RB check above — is
  defeated **only** by a freshness rule. This part provides the checkable input for
  that rule (the monotonic release index + derived date of RB-8a, ordered in the
  log, RB-13); the *adoption policy* that uses it (reject a lower index than one
  already seen; warn on staleness) is item 4.1 and is client-local. The residual:
  reproducibility alone does not defeat downgrade; the manifest field this part
  mandates is what makes defeating it *possible* for 4.1 (the ID-4 epoch, for
  releases).

## 9. The merge seam with update governance (OP-8 / item 4.1)

The release signers and the map's root-publishers look like one mechanism.
**Position, mirroring Part 8's §9: keep them separate in trust, even if they share
tooling.**

- **RB-10 (an attestation is a reproduction claim, weighted by independent
  re-reproduction, not by who issued it). [normative]** A build **attestation** is
  a statement *"I rebuilt manifest M for triple T and got `H_build`"* — a
  **reproduction report**, not an authorization. Its weight comes from being
  **independently checkable** (anyone re-runs RB-7 and confirms or refutes it), not
  from the attester's identity: a pseudonym-signed attestation and an unsigned one
  carry the **same** weight once a third party has reproduced the claim; the
  signature only *locates* the claim (RB-2). Corroboration MUST follow the Part 2
  discipline exactly: **count only independently verified reproductions, never a
  raw attestation count** (the GR-20 / PS-10 "count only verified, never raw"
  rule). And the part concedes what GR-19a already proves: **reproducer
  independence is not verifiable from attestations alone** — you cannot tell 10 000
  reproducers from one party wearing 10 000 masks — so a reproducer count is a
  *weak* signal that reduces to OP-2, and the *strong* signal is the client's own
  rebuild (RB-7). A design in which an attestation's acceptance depends on the
  attester's identity, or in which a raw count of unverified attestations
  corroborates a build, is non-conforming (RB-1, and it is the sybil-votable
  majority authority RB-10 exists to forbid).
- **RB-10a (canonical attestation format, dedup by reproducer). [normative]**
  Attestations cross the wire (RB-14) and feed a count (RB-10), so they MUST have a
  canonical encoding (reuse canonical CBOR, GR-21..GR-30) or two honest attesters
  produce non-matching bytes and counting breaks. Attestations MUST be deduplicated
  by `(reproduction identity, M, triple, H_build)`, and weight is
  **per-independent-reproducer, never per-attestation-byte-string**, so an
  adversary cannot inflate corroboration by minting byte-distinct variants of one
  claim (format-stuffing).
- **RB-11 (the toolchain must build deterministically-usably; a cross-host test
  vector exists). [normative]** Because the pinned toolchain can itself embed
  nondeterminism (parallel codegen, `OUT_DIR`, host triple in metadata), the part
  MUST pin the flags and modes that make it produce identical output across hosts
  (RB-6), and a **cross-host build test vector** (manifest → expected `H_build` for
  a fixed triple) MUST exist so a second machine proves it reproduces the identical
  artifact (the ID-4d map-test-vector rule; ties to roadmap 3.2's conformance
  harness). This is the RB analogue of Part 9's RI-1b: *a passing functional test
  proves the binary runs, not that it is bit-identical* — reproducibility is
  checked by rebuild-and-compare, never assumed from "it compiled."
- **RB-12 (contributors are pseudonymous; trust flows only through reproducibility).
  [normative]** ScrambNet has **no identity-bound signing keys** and no trusted
  author identity. Trust in a binary MUST derive **entirely** from (a) the source
  being public and reviewable (I-1) and (b) the binary reproducing from that source
  (RB-7) — **never** from *who* wrote, committed, tagged, or signed it. A step that
  requires a trusted author, maintainer, or signer identity to accept a build is
  non-conforming under both RB-1 and the project's pseudonymity rule. This is the
  resolution of this part's central tension: *the author is untrusted by
  construction; the binary is trusted by reproduction.*
- **RB-12a (what pseudonym keys are for — and the precondition they rest on).** A
  contributor key, if used at all, authenticates *continuity of a pseudonym* and
  *locates* work (this commit, this attestation, came from the same pseudonymous
  hand) — a convenience for gossip and for 4.1's locator role (RB-2), never a root
  of build-trust. Losing, rotating, or replacing such a key MUST NOT invalidate any
  binary that still reproduces. A holder of a compromised key cannot ship a
  malicious-but-reproducing binary that **survives one honest reviewer plus one
  honest reproducer** — but that protection is *their existence*, not the key:
  absent an honest reviewer of the source (I-1) and an honest reproducer the client
  can reach (RB-7/RB-10), the compromised key *can* ship a malicious binary to a
  client that neither reviews nor rebuilds (RB-7b). So the protection reduces to
  I-1 (review) and OP-2 (honest-reproducer reachability); it is not an unconditional
  property of the key. (This states the precondition explicitly, so the claim is
  not circular.)
- **RB-12b (reproducibility proves binary-matches-source, says nothing about
  source-honesty).** Reproducibility and review are **orthogonal axes**.
  Reproducibility proves the binary matches the source; it says nothing about
  whether the source is honest. Pseudonymity (RB-12) removes "a trusted author
  vouched for the source," so source-honesty rests on **public review (I-1)** and
  nothing else. The part states this plainly so no reader mistakes "reproducible"
  for "safe" or "reviewed": a faithfully-reproduced build of backdoored source is a
  faithful reproduction of a backdoor (§10, OP-10).
- **RB-13 (hashes and manifests are published to a permissionless log, ordered by
  release index).** Release `(triple, H_build, manifest-hash, release-index,
  committer-date)` tuples SHOULD be announced to the same permissionless
  append-only transparency log(s) used for maps (ID-6/ID-7), preserving the RB-8a
  ordering, so build announcements are timestamped and equivocation-detectable with
  **no privileged appender** (ID-7). The log does not *bless* a build — reproduction
  does (RB-7) — it makes "different binary shown to different people" detectable and
  gives freshness (RB-9a) a witnessed order. Per RB-2a the log *construction* is
  shared with the map; the *instances/sets* SHOULD stay independent (ID-7b
  "multiple logs, none canonical") so the two availability domains do not collapse
  into one load-bearing operator.
- **RB-14 (gossip the build tuple; detect split-view). [normative]** Clients and
  rebuilders SHOULD gossip `(triple, H_build, manifest-hash, release-index)` over
  GR-6 under GR-8 source-mixing, and demand transparency-log consistency proofs, so
  an adversary serving binary X to Alice and binary Y to Bob (same triple, same or
  conflicting index) is caught by any party holding both (the ID-7a equivocation
  defense, for builds). A log gating build appends behind a signer set is
  non-conforming (RB-2a/ID-7).
- **RB-15 (build anomalies are gossiped, not suppressed). [normative]** Four events
  are build anomalies every verifier MUST gossip on detection, comparing only
  like-triple hashes (RB-6b): (a) an `H_build` that fails reproduction from its
  manifest (RB-7a); (b) a transparency log presenting inconsistent roots over build
  announcements (proven equivocation); (c) a persistent same-triple `H_build`
  divergence against independent reproducers; (d) a **release-index regression** —
  a tag presented with a lower index than one already witnessed for that release
  line (the downgrade signature, RB-9a). A verifier MUST NOT suppress an anomaly to
  make a release look healthy (the ID-10 immune-signal rule, for builds).

## 10. What this part does not solve (the declared residual)

This part makes two parties who *both rebuild* provably agree or provably detect
that they differ, and it moves trust from *who built it* to *does it rebuild* — a
real and large reduction, the right one for a pseudonymous project. It does
**not** make the binary *safe*. The gaps are real and are declared, not smoothed:

- **§10.1 — A backdoor in a pinned dependency is reproduced faithfully, not
  caught.** If a vendored crate contains hostile code, every rebuilder gets the
  identical malicious binary and RB-7 *confirms* the match — reproduction is
  working exactly as designed and is blind to the malice. The binary honestly
  reflects source that is honestly backdoored. The only defenses are **public
  review (I-1), audit (RB-16), and minimizing the dependency surface
  (RB-5/RB-17)** — human processes that *bound* the surface, none an authority-free
  cryptographic check. **This is the primary residual, it has no untrusted
  substitute, and it is the project's recurring problem wearing a fourth mask —
  OP-10.** The value proposition is honest precisely here: reproducibility does
  **not** defend against the most likely real-world attack, and was never meant to —
  but it changes *what kind* of attack is required. Without it, an attacker poisons
  **one binary for one target**, invisibly and unattributably. With it, a malicious
  binary must trace to **public source** that **everyone can review** and that
  **reproduces identically for everyone** — forcing the attack from "poison the
  binary" (invisible, per-target) to "poison the public source or a public
  dependency" (reviewable, universal, maximally exposed to the one honest
  reviewer). That transformation is the worth of the part; catching the poisoned
  source is OP-10 and I-1, not reproducibility.
- **§10.2 — A compromised toolchain that reproducibly miscompiles.** A backdoored
  `rustc`/LLVM can insert behavior absent from the source, deterministically, so
  every rebuilder reproduces the identical bad binary and `H_build` equality holds.
  Pinning (RB-3) makes everyone share one compiler and makes *swapping* it
  detectable; it does not make the pinned compiler honest. **No untrusted
  substitute** short of bootstrap-from-source or diverse-double-compilation, which
  this part names as future work (RB-3b), not a current requirement.
- **§10.3 — Trusting-trust (Thompson).** The general case of §10.2: a compiler that
  backdoors *and* propagates the backdoor into compilers it builds. Pinning the
  compiler bytes does not break the loop; it guarantees everyone is inside the
  *same* loop. Declared, not solved. (This is why RB-18 says "every output byte
  traces to a *pinned* input" — provenance — and explicitly **not** "to an honest
  input": a hashed, pinned, backdoored compiler satisfies traceability and is still
  malicious.)
- **§10.4 — Reproducible ≠ safe; reproducible ≠ reviewed.** A perfectly
  reproducible build of honest-looking-but-subtly-wrong source is perfectly
  reproducible. Pseudonymity (RB-12) means no trusted author vouches for the source,
  so source-honesty rests entirely on public review (I-1); reproducibility and
  review are orthogonal (RB-12b).
- **§10.5 — Corroboration-by-count reduces to OP-2; the non-rebuilding client is
  the modal user.** "N independent rebuilders got `H_build`" is only as strong as
  the *independence* of the N (RB-10, GR-19a). A single honest re-reproduction
  refutes a false claim with certainty (stronger than the map case, since source is
  deterministic), but a client that **cannot rebuild** (RB-7b — the phone, i.e.
  almost every user) leans on the attestation count, which is a sybil-votable
  quorum: an adversary mints pseudonymous attestations for a bad `H_build`, and an
  **eclipsed** client sees only adversary attestations and never meets an honest
  reproducer. So for the non-rebuilding or eclipsed client, "no authority" means
  "trust the verified-reproducer quorum," and that holds only as far as **OP-2**
  does. This part **reduces** build-authority to OP-2 for the non-rebuilder; it does
  not dissolve it — the identical reduction Part 8 ends on (ID-1 → OP-2).
- **§10.6 — The arbiter is liveness-bounded; escrow must be replicated or it is a
  singleton.** Rebuild-and-compare is the authority-free arbiter **only while the
  pinned inputs are still fetchable**. The toolchain binaries and the full crate
  tree are large and perishable: a **yanked crate** or a **de-published toolchain
  release** makes `rebuild(manifest)` unexecutable, and then the one trusted
  operation is gone — worst for exactly the forensic disputes ("was v1.2
  backdoored?") that need it most. A conforming deployment SHOULD escrow the pinned
  input bytes in a content-addressed store **replicated across the same
  permissionless mirror set** as the builds; a single-replica escrow is
  content-addressed (so it cannot *lie*) but it is a **liveness singleton** (it can
  *vanish*), and I-3 covers liveness. Absent replication, RB-7 is declared
  **liveness-bounded**, not unconditional (the ID-5a liveness residual, for builds).
- **§10.7 — Determinism is a moving target against toolchain churn.** New
  `rustc`/LLVM versions introduce new nondeterminism sources (new parallel passes,
  new metadata, new `cfg` behavior). RB-6's hazard set is **current**, not closed; a
  pinned toolchain is reproducible *as pinned*, but each toolchain bump is a fresh
  determinism-audit obligation, and the manifest records which hazard-set version it
  was built against (RB-6, RB-8). "Reproducible once" does not mean "reproducible
  forever."
- **§10.8 — First-build TOFU: a malicious first binary lies about reproducing
  itself.** A fresh user's *first* client binary cannot be reproduced before it is
  used to bootstrap (you need a working client to fetch the source, the toolchain,
  and reach the logs and peers). The first binary is adopted on trust-on-first-use
  exactly as Part 8's first map is (ID-8) — and worse: a compromised first binary
  owns the user's entire reproduction and gossip apparatus thereafter, so it can
  **lie about its own reproduction** ("I rebuilt myself; `H_build` matches"). A
  client therefore cannot honestly verify *its own* reproduction; first-binary trust
  rests on an **out-of-band independent reproducer** — a different machine/toolchain
  the user trusts more than the binary under test. This is the trusting-trust /
  compromised-host boundary (§10.9); it is a declared residual, stated here rather
  than swallowed silently by "out of scope."
- **§10.9 — What this part does not even attempt.** Runtime compromise of the
  user's machine; a malicious *build of honest source by the user themselves* on a
  compromised host (reproduction confirms the match; the host still owns the
  process); and everything above the artifact boundary — install, and update
  *adoption* (which build to run and when), which is item 4.1. The part is
  bit-identical-artifact only; it names these as out of scope, not as solved.

The honest summary: reproducible builds move trust from *who built it* to *does it
rebuild* — real and large. But they are **silent** on whether the source is honest
(§10.1, §10.4), **blind** to a reproducible compiler/dependency backdoor (§10.1,
§10.2, §10.3), **liveness-bounded** as an arbiter (§10.6), **reduced to OP-2** for
the non-rebuilding or eclipsed client (§10.5) — the modal user (RB-7b) — and
**TOFU** on the first binary (§10.8). These are the price of refusing a release
authority. The correct response is to bound them — minimize and audit the trusted
compute base, replicate the escrow, encourage independent rebuilds, carry the
freshness index — and to state them, not hide them.

## 11. Supply-chain hygiene that bounds the residual

- **RB-16 (dependency and toolchain audit is mandatory and in-scope).** Because
  reproduction cannot see a backdoor that every rebuilder faithfully reproduces
  (§10.1), the part MUST require a committed, reviewable audit trail for the
  dependency set and the toolchain (`cargo-vet`/`cargo-audit`-style records, pinned
  by content), treated as **review evidence (I-1), not as authority**. The audit
  reduces the §10.1 attack surface; it does not remove it, and the part says so.
- **RB-17 (minimize the trusted compute base).** The part SHOULD require actively
  shrinking what must be trusted-and-audited: fewer dependencies (RB-5), fewer
  `build.rs`/proc-macros (RB-5b), a smaller toolchain surface (RB-3a),
  `#![forbid(unsafe_code)]` where feasible — because every element of the trusted
  compute base is a §10.1 residual the audit must cover and reproduction cannot.
  Honest note: "minimal" is not "small" — a real async + crypto node (an async
  runtime, a Sphinx/X25519 stack, CBOR, …) drags *hundreds* of transitive crates,
  many with build scripts, so the §10.1 dependency-backdoor residual is not a corner
  case but the **expected** attack surface. That is the honest framing of OP-10.
- **RB-18 (the whole chain is pinned or it is not pinned — and pinned means
  provenance, not honesty). [normative]** A single unpinned input anywhere — an
  un-hashed toolchain component, a floating dependency, a `build.rs` that reads the
  host, a container base image fetched by tag — voids the reproducibility claim for
  the whole artifact, because that one input reintroduces a server or a host as a
  trusted party (RB-1). The manifest MUST be **complete**: if a byte of output
  cannot be traced to a *pinned* input, the build is non-conforming (the ID-4c rule,
  for software). **This is a determinism/provenance claim, not a trust claim:** a
  pinned input can be malicious (§10.1, §10.2, §10.3); pinning makes the malice
  identical for everyone and any *divergence from an honest input* detectable — it
  does **not** make the input honest. "Pinned" never means "safe."

## 12. Requirements introduced here

- **RB-1 / RB-2 / RB-2a** — no release authority, reproduction is the arbiter;
  signatures only locate, never authorize; shared tooling with the map, never
  shared authority.
- **RB-3 / RB-3a / RB-3b** — toolchain pinned by content across the whole compile
  surface; the pinned compiler is a declared trusting-trust residual (provenance,
  not honesty).
- **RB-4 / RB-4a / RB-4b** — hermetic, offline, ambient-free build; no build-time
  fetch; a fixed environment with `SOURCE_DATE_EPOCH` **derived** from the tagged
  commit.
- **RB-5 / RB-5a / RB-5b** — minimal, vendored, content-pinned dependency tree;
  lockfile necessary-not-sufficient; build scripts and proc-macros are sandboxed
  trusted compute.
- **RB-6 / RB-6a / RB-6b** — normative, toolchain-versioned nondeterminism hazard
  set; `H_build` is the only name; `H_build` is per-(source, manifest, target
  triple) and agreement is within a triple.
- **RB-7 / RB-7a / RB-7b** — the stranger's rebuild-and-compare; reject the
  unreproducible; the non-rebuilding modal user tracks `reproduced-by-others-
  unverified` and reduces to OP-2.
- **RB-8 / RB-8a / RB-9 / RB-9a** — the manifest is the recipe, canonical and
  content-addressed, carrying a monotonic release index; agreement is like-triple
  hash equality; the freshness residual (reproducible-downgrade) with the manifest
  field 4.1 needs.
- **RB-10 / RB-10a** — an attestation is a reproduction claim weighted by
  independent re-reproduction (count only verified, never raw; independence is
  OP-2); canonical format, dedup per reproducer.
- **RB-11 / RB-12 / RB-12a / RB-12b** — cross-host build test vector; trust flows
  only through reproducibility; pseudonym keys locate, never root trust (with the
  precondition made explicit, non-circular); reproducibility ⊥ review.
- **RB-13 / RB-14 / RB-15** — permissionless log of build tuples ordered by release
  index; gossip + split-view detection; four mandatory anomalies including the
  downgrade signature.
- **RB-16 / RB-17 / RB-18** — mandatory audit as review evidence; minimize the TCB
  (which is still large); the whole chain pinned, where pinned is provenance, not
  honesty.

RB-1 and RB-7 are the load-bearing two: no authority, and reproduction is the
arbiter. Both are bounded, not absolute — RB-1 reduces to OP-2 for the client that
does not rebuild (§10.5, the modal user), and RB-7 is liveness-bounded (§10.6).
The sharpest residual, stated and not hidden, is §10.1: **reproducibility does not
catch a backdoored dependency, which is the most likely real attack — it forces the
attack into public, reviewable, universal source, which is the point, and catching
it there is OP-10, not this part.** Break this part by naming a build step that
needs a trusted party, a released artifact that cannot be rebuilt from its
manifest, a determinism hazard RB-6 misses, a way a signature smuggles back
authorization past RB-2, or a way the non-rebuilding client is left trusting a
majority that is not OP-2. That is the invitation, in the Part 8 voice.
