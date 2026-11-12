# ScrambNet Specification — Part 11: Update Governance

**Status: DRAFT.** This part decides how a client comes to run a **newer**
ScrambNet binary *without trusting whoever released it*, under I-3 — no authority
— and under two project-owner-bound constraints: **no authoritative signer set**,
and **no push of any kind**. It is the adoption layer Part 10 §10.9 names as out
of its own scope. Part 10 decides *is this binary the build of that source*; this
part decides *which build to run, and when*. Strawman values are marked `(s)`.

Read §1 and §10 first. Between them they say what this part buys (reproduction
and freshness, not signature, as the arbiter of adoption) and what it concedes up
front: refusing both an authority and a push buys **patch-latency** as its central
residual — a vulnerable client may never be patched, and in the worst case
(a client already compromised by the very bug a patch would fix) it provably may
never even hear of the patch (§10.1). The project accepts that cost deliberately,
because the alternative — a party or a channel that can push a release to everyone
at once — is the exact concentrated kill switch the whole project exists to deny.

This part reuses rather than reinvents: Part 10's freshness index (RB-8a), release
log (RB-13), gossip (RB-14), count-only-verified discipline (RB-10/RB-10a) and
non-rebuilding-client state (RB-7b); Part 8's permissionless transparency log
(ID-6/ID-7), gossiped-root equivocation defense (ID-7a), multiple-logs rule
(ID-7b), and declared TOFU (ID-8); Part 2's source-mixing (GR-8); Part 3's honesty
surface (PS-9). The seam with Part 10 is cited, not re-decided (RB-2, Part 10 §9).

## 1. The decision, in two sentences

- **There is no release authority, and there is no push.** A newer release is a
  reproducible, content-addressed artifact announced by a permissionless log
  append (UG-2); a client *learns* it may exist only by pulling and gossiping on
  its own schedule (UG-3), *decides* to adopt it by a manual, local, opt-in act
  (UG-4), and binds that decision to reproduction (RB-7) and freshness (RB-9a),
  **never** to who announced or signed it (UG-1a, RB-2).
- **Adoption trust flows through reproduction and freshness; revocation can only
  inform, never force; and the price — an unpatched or compromised client that
  never adopts — is a declared residual, not a solved problem.** No signature
  gates adoption (UG-2a); no mechanism removes a bad binary from a running client
  (UG-8a); the known-bad signal is a permissionless, forceless, ignorable report,
  never an authority (UG-8).

So the honest outcome: **adoption is as authority-free as reproduction makes it,
and as reliable as a user who chooses to act and is not eclipsed — no more.** §10
is the residual that no construction here removes.

## 2. Announcing a release without a signer

- **UG-1 (no release authority; adoption is a client-local act). [normative]** No
  step of *learning of*, *validating*, or *adopting* a newer release MUST require
  trusting that a particular party released, announced, signed, or blessed it. The
  only trusted operations are those Part 10 defines — recompute `BLAKE2s`,
  rebuild-and-compare (RB-1) — plus comparing monotonic release indices on a line
  (RB-8a, UG-2c). Any element not replaceable by an untrusted substitute performing
  those is a defect under I-3 and MUST be removed or declared in §10 (the ID-1 /
  RB-1 rule, for update adoption).
- **UG-1a (adoption binds to reproduction, never to publication). [normative]**
  *Which* build to run is decided by the Part 10 trust anchor — does it reproduce
  (RB-7), is it fresh (RB-9a) — and by nothing about *who* announced it. A client
  MUST NOT adopt a build *because* it was announced by any party, key, channel, or
  roster. This restates RB-2 (signatures locate, never authorize) at the adoption
  boundary RB-2 defers to this part.
- **UG-2 (announcement is a permissionless log append, no privileged appender).
  [normative]** A release is announced by appending its Part 10 tuple
  `(triple, H_build, manifest-hash, release-index, committer-date)` (RB-8/RB-8a) to
  the permissionless append-only transparency log(s) of RB-13 / ID-6 — the same
  *construction* as the map log, reused as tooling (RB-2a / ID-11a), never as a
  shared authority. **Anyone MAY append**; there is no allow-list and no signer set
  whose append makes a release official (ID-7). A log that gated release appends
  behind a roster would be the directory authority I-3 forbids and is
  non-conforming (ID-7, RB-2a).
- **UG-2a (no authoritative signature; default is none). [normative]** A conforming
  release carries **no authoritative signature**. If a pseudonymous signature
  appears at all it is a pure RB-2 locator — it attributes a build to a continuing
  pseudonymous hand for gossip convenience — and a client MUST treat a signed and
  an unsigned announcement of the same `(triple, H_build, release-index)` as
  carrying **identical adoption weight** once reproduction corroborates them
  (RB-10). A design in which an announcement's acceptance depends on a signer's
  identity is non-conforming (RB-1, RB-12).
- **UG-2b (the release line is owned by no party). [normative]** The index of
  RB-8a is monotonic *within a release line*. A line MUST be defined so that no
  party owns the right to extend it; otherwise "append a higher index" becomes an
  authority to declare the next release (the directory authority I-3 forbids,
  wearing a version number). UG-2c gives the construction.
- **UG-2c (line identity is a reproduction-verifiable manifest chain from a
  genesis). [normative]** A line is identified by `line_id = BLAKE2s` of its
  **genesis manifest** (the first release's canonical manifest, RB-8a). A release
  **extends** `line_id` iff its manifest carries the previous release's
  manifest-hash as an explicit predecessor field **and** its tagged source
  reproduces forward (RB-7) from a source lineage whose prior tag is the
  predecessor's — so "extending the line" is a **permissionless, reproduction-
  checkable act**: anyone who can produce a reproducing successor manifest may
  append a higher index, and no repository, committer, or key owns the line. A
  **fork** is any manifest that does not chain to `line_id`; it necessarily carries
  a different `line_id` and is therefore **visible as a distinct line**, never a
  silent higher index injected into the tracked one (the ID-2 "the hash is the only
  name" rule, for release lineage). `line_id` is stable across honest releases
  (the genesis hash does not change) yet owned by no one (the chain is public and
  reproduction-checked) — the two properties UG-2b requires.

## 3. Discovery without a push

- **UG-3 (discovery is pull/gossip only; no push path exists). [normative]** A
  client learns a newer release *may* exist **only** by (a) pulling the freshness
  index (RB-8a) and the line's log tuples (RB-13) on its own schedule, and (b)
  gossiping `(line_id, triple, H_build, release-index)` over GR-6 under GR-8
  source-mixing (RB-14). No mechanism in this part — and none a conforming
  deployment MAY add — pushes a release, a notification, or a prompt to a client.
  The weaker "notify-of-availability" path is **explicitly not adopted**: freshness
  is pulled and gossiped, never delivered (the owner's binding constraint, stated
  normatively so an implementer cannot re-add a push and remain conforming).
- **UG-3a (no single source gates freshness). [normative]** A client MUST NOT treat
  the highest release-index it has seen as current on the word of any single peer,
  log, or mirror before applying GR-8 / PS-10 "count only independently verified
  sources" (RB-14, ID-9). Its view of *what is current* is a source-mixed
  observation under the same eclipse defense as its map and relay-sample views.
- **UG-3b (discovery cadence is client-local and privacy-bounded). [normative]**
  The pull cadence is a client-local policy (strawman: opportunistic, folded into
  existing GR-6 gossip batches, never a distinguishing beacon (s)). Freshness-pull
  traffic MUST NOT become a fingerprint; it rides the gossip channel the client
  already uses (the GR-8 / Part 6 metadata discipline, applied to update
  discovery).
- **UG-3c (a client pulls on its own clock, never in reaction to a peer signal).
  [normative]** A client MAY initiate a fetch **only** on its own privacy-bounded
  cadence (UG-3b) or on an explicit user action. It MUST NOT initiate a fetch *in
  response to* a peer-reported divergence, known-bad, or equivocation signal: that
  reactive trigger is the ID-9a re-fetch downgrade (Part 8 §10 flags "treat your
  map as suspect, re-fetch" as an under-defended direction an adversary drives), and
  for updates it is **push-in-disguise** (UG-5a). Anomalies are surfaced and
  gossiped (UG-7), never acted on by fetching. This is the boundary between "my
  scheduled pull noticed a higher index" (allowed) and "a peer made me go look"
  (forbidden).

## 4. Deciding to adopt (manual opt-in, no signature gate)

- **UG-4 (adoption is a manual, local, opt-in act). [normative]** Replacing the
  running binary with a discovered newer one is a decision the **user** makes
  locally; no conforming client adopts a release automatically, on a timer, or on
  reaching any corroboration threshold. The threshold governs *what the client may
  offer or surface*, never *what it installs*. "Corroborated" is a precondition the
  client checks; "adopt" is an act the user takes (the ID-8b "detect, do not claim
  to prevent" stance, moved from detection to adoption).
- **UG-4a (the adoption checklist — no signature gate). [normative]** Before
  surfacing a discovered release as *adoptable*, a client MUST have, for its own
  target triple and tracked `line_id`:
  1. **reproduction corroboration** — `H_build` matches the manifest, by the
     client's own rebuild (RB-7) **or**, for the non-rebuilding modal client
     (RB-7b), a count of **independently verified** reproducers under RB-10 (never
     a raw attestation tally);
  2. **freshness** — a release-index ≥ the highest the client has witnessed on that
     line, ordered in the log (RB-9a, RB-8a, UG-2c);
  3. **log corroboration** — appearance with consistent gossiped roots in a
     configured quorum of the logs it watches (ID-7b, strawman ≥2 (s));
  4. **no equivocation** — no outstanding UG-6 split-view anomaly against that line.

  There is **no signature-gate step**, by construction (UG-2a). A client MUST NOT
  present any of these as "verified" when it has only corroboration-by-count; it
  carries the Part 10 `reproduced-by-others-unverified` state through to the UI
  (RB-7b).
- **UG-4b (adoption policy is declared, client-local, conservative by default).
  [normative]** The policy that turns the UG-4a checks into an *offer* is
  client-local and MUST be declared to the user (strawman default: offer only a
  release fresher by index, reproduction-corroborated above the client's threshold,
  log-corroborated in quorum, and free of equivocation; never offer across a
  `line_id` change (UG-2c) without an explicit user step (s)). A client MAY expose a
  stricter policy (e.g. "offer only what I myself rebuilt"); it MUST NOT expose one
  weaker than "fresher index + quorum-corroborated + no equivocation," because
  weaker reduces to adopting on a single source's say-so (UG-3a). **An unrebutted
  vulnerability-class known-bad report (UG-8) MUST NOT by itself lower a release
  below this offer threshold** (UG-8, H-defamation defense).
- **UG-4c (offer and install are mechanically distinct). [normative]** **OFFER** is
  the surfacing to the user of an availability-and-corroboration state; it MUST NOT
  fetch the artifact body in response to a divergence or known-bad trigger (UG-3c),
  and any pre-fetch MUST ride the UG-3b cadence so it adds no distinguishing beacon.
  **INSTALL** is a user-initiated act that replaces the running binary. No automatic
  transition from OFFER to INSTALL may exist (UG-10). An implementation that
  pre-stages a binary one tap from running, or fetches on a peer signal, has built a
  push and is non-conforming even if it calls the step "offer."

## 5. The reproducible-downgrade defense, client-side

- **UG-5 (never silently accept a lower index; surface it). [normative]** A client
  MUST NOT adopt, nor silently treat as current, any release whose index is
  **lower** than the highest it has witnessed for that `line_id` (RB-9a). A
  presented-lower index is the single-vantage signature of a **reproducible-
  downgrade attack** — an old, perfectly-reproducing, known-vulnerable tag fed to
  the client (RB-9a) — and MUST be surfaced to the user and gossiped as a downgrade
  anomaly (UG-7d), never consumed as an ordinary "latest." Because the index is
  bound to the derived committer date and the manifest chain (RB-8a, UG-2c) and
  ordered in the log (RB-13), "lower index" is a checkable property, not a
  judgement.
- **UG-5a (staleness is surfaced, not acted on). [normative]** When a client's own
  running index falls below a corroborated quorum's current index for its line, it
  MUST surface the staleness to the user (PS-9's honesty surface, reused) — *you are
  running an older release than your corroborated peers; a newer one exists.* It
  MUST NOT act on that surfacing by pulling, prompting-as-push, or adopting (UG-3c);
  it informs, and the user decides (UG-4). The honest asymmetry with ID-9a is
  deliberate: the map's machinery *re-fetches* on divergence; update adoption must
  **not**, because a forced re-fetch would be a push in disguise. Staleness stops at
  the honesty surface.

## 6. Split-view and equivocation on releases

- **UG-6 (two different "latest" to two clients is caught by gossiped roots).
  [normative]** An adversary serving release X to Alice and release Y to Bob — same
  triple, same `line_id` — is a split-view attack on *freshness*, the ID-7a attack
  wearing an update mask. The defense is **not** trusting the log operator; it is
  gossiping the logs' signed tree heads over GR-6 (GR-8 source-mixed) and demanding
  **consistency proofs** between any two roots a client sees (ID-7a, RB-14). A client
  holding both roots has cryptographic proof the log equivocated and MUST treat it
  as hostile (ID-10, UG-7b).
- **UG-6a (index-equivocation is the cross-vantage signature; disambiguated from
  downgrade). [normative]** **Downgrade** (UG-5 / UG-7d) is the *single-vantage*
  signature: *my own* witnessed max on a line regressed. **Index-equivocation**
  (UG-7b) is the *cross-vantage* signature: the same `line_id` presented with a
  different highest index to different source-mixed vantages **and** the logs' roots
  fail a consistency proof — two different indices alone are not equivocation (one
  vantage may simply be behind); the **consistency-proof failure** is what proves it.
  A single underlying event may raise both signatures (the victim pinned at a stale
  index sees a downgrade when it later hears the higher one; a party holding both
  roots sees equivocation); it MUST be deduplicated by `(line_id, conflicting roots)`
  (the RB-10a dedup discipline, reused) so it is counted once. Index-equivocation is
  gossiped so a partially-eclipsed client catches it off non-eclipsed peers.

## 7. Release anomalies are gossiped, not suppressed

- **UG-7 (mandatory anomaly gossip). [normative]** Five events are release
  anomalies every client MUST gossip on detection, comparing only like-triple,
  like-`line_id` data, and deduplicated per RB-10a: (a) an `H_build` that fails
  reproduction from its manifest (RB-7a / RB-15a); (b) a log presenting inconsistent
  roots over release announcements — proven equivocation (RB-15b, UG-6/UG-6a); (c) a
  persistent same-triple `H_build` divergence against independent reproducers
  (RB-15c); (d) a **release-index regression** on a line — the downgrade signature
  (UG-5 / RB-15d); (e) a **known-bad report** (UG-8). A client MUST NOT suppress an
  anomaly to make a release look healthy (ID-10, for releases).

## 8. The revocation problem (the hard one)

- **UG-8 (known-bad is a permissionless, corroborated, forceless REPORT — never an
  authoritative revocation). [normative]** "Release X is known-bad" cannot be an
  authoritative statement: *any* party trusted to pronounce a release bad is a kill
  switch (it can **censor** an honest release by declaring it bad — the I-3 authority
  inverted), so no such party exists. Instead this part provides a **known-bad
  report**: a claim `(line_id, triple, H_build, reason-class, evidence-locator)`
  that **anyone MAY publish and anyone MAY ignore**. Reports cross the wire and feed
  a count, so they MUST reuse **RB-10a verbatim**: canonical CBOR, dedup by
  `(reporter reproduction-identity, line_id, triple, H_build, reason-class)`, and
  weight **per-independent-reproducer, never per-report-bytes** — without which the
  channel is a format-stuffing / defamation lever (H-defamation). Evidence splits
  into two kinds:
  - **reproducible evidence (the report self-verifies; no trust needed)** —
    *non-reproduction* (rebuild from the manifest and see RB-7a fail), *index-
    regression / downgrade* (the log order shows it, UG-5), *log equivocation* (the
    consistency proof fails, UG-6). For a client that **can rebuild / reach an
    honest reproducer**, "known-bad" here reduces to a Part 10 check it runs itself;
    the report merely *locates* the defect, it does not *authorize* the verdict.
  - **non-reproducible evidence (reduces to social consensus)** — *"this reproducing
    build contains a vulnerability / backdoor."* No cryptographic check decides this
    — it is the Part 10 §10.1 / OP-10 source-honesty residual. Here "known-bad" is a
    claim weighted by public review (I-1), corroboration count, and reproducibility-
    of-the-evidence-where-it-exists (a PoC that rebuilds), and it reduces to **OP-2
    and the project's social layer**. An **unrebutted vulnerability-class report MUST
    NOT by itself gate an offer** (UG-4b): it MAY only *annotate* the offer ("N
    independently-verified parties allege a vulnerability; evidence at …"), never
    lower the release below the UG-4a threshold — precisely because this class is
    sybil-votable (GR-19a) and gating on it would let an adversary censor an honest
    security patch into staleness.

  **The modal phone (RB-7b) does not enjoy the reproducible classes.** A client that
  cannot rebuild cannot self-verify a non-reproduction report, and an eclipsed
  client cannot hold the two roots a log-equivocation proof needs (ID-7a §10). For
  the non-rebuilding or eclipsed client, **all but the arithmetic index-regression
  check reduce to RB-10 corroboration, i.e. OP-2** (the Part 10 §10.5 reduction,
  inherited — see §10.2). A conforming client MUST NOT auto-act on a known-bad
  report (that would re-create the push and the authority at once); it surfaces the
  report with its corroboration level and evidence class, and the user decides
  whether to stop or move.
- **UG-8a (revocation can only inform; it cannot push, so it cannot force-patch).
  [normative]** Because no push exists (UG-3) and no authority exists (UG-1), a
  known-bad report reaches a client only when that client pulls/gossips, and changes
  nothing until the user acts. There is **no mechanism to remove a known-bad binary
  from a running client**, and this part does not pretend to one. The known-bad
  signal makes a bad release *detectable and avoidable by an attentive, non-eclipsed
  user*; it cannot make it *unrunnable* by fiat. This is the revocation residual
  (§10.2), stated, not smoothed.
- **UG-8b (self-verifying refuse-to-run — authority-free, opt-in, self-proof only).
  [normative]** A client that **itself** proves (RB-7, no external party) that its
  **own running binary** fails reproduction against its shipped manifest — or that
  its own embedded index is a regression it can check arithmetically against a
  non-eclipsed floor — MAY, **as a client-local opt-in, not a default**, refuse to
  continue running that binary and fall back to re-bootstrap (ID-8). This is
  **authority-free** (the proof is the client's own rebuild, and a false non-
  reproduction proof is *impossible* — the adversary cannot make honest public
  source reproduce to a bad `H`, ID-8a.3) and it is **not a push** (nothing is
  installed; the client declines to run code it proved is not the reproduction of
  its own stated source — the run-time analogue of RB-7a, which already *rejects* a
  non-reproducing release at adoption). Refuse-to-run MUST remain **forbidden** for
  any evidence the client cannot self-verify — the vulnerability class and anything
  resting on a corroboration count or a quorum floor (both OP-2 / eclipse-forgeable)
  — because there a *false* floor or report would be a denial of service against an
  honest client. This protects only the **rebuilding** client; the non-rebuilding
  modal phone (RB-7b) still reduces to OP-2 (§10.2), so UG-8b narrows the
  fleet-safety gap (§10.1) without closing it.

## 9. Bootstrap: the first update is TOFU

- **UG-9 (the first update inherits Part 10's first-binary TOFU and cannot verify
  itself). [normative]** A client's view of *what release is current* is mediated by
  the binary it is already running; a compromised first binary (Part 10 §10.8) owns
  the client's entire discovery, freshness, and gossip apparatus and can therefore
  **lie about freshness** — pin the user at a stale, vulnerable index, hide a
  known-bad report about itself, or suppress an equivocation it is party to. A
  client cannot honestly verify its *own* currency any more than its *own*
  reproduction (Part 10 §10.8). First-update trust rests on the same **out-of-band
  independent corroboration** the first binary does: a release-index and known-bad
  view reached from a machine or channel the user trusts more than the binary under
  test. This is declared TOFU (ID-8), not solved.
- **UG-9a (a fresh client's first release choice is TOFU over independent channels).
  [normative]** On first install a client MUST obtain its initial
  `(line_id, index, H_build)` over as many **independent** channels as it has (Part
  10 §10.8 / ID-8: the out-of-band bridge line GR-10 plus ≥2 mirrors over distinct
  networks (s)), require the **same** `(line_id, index, H_build)` from all before
  provisionally accepting, and record it as **unverified-TOFU** until it rebuilds
  (RB-7) or accumulates consistent gossiped corroboration. It MUST surface this
  state: *you are trusting your first client and your first notion of "latest";
  neither is yet corroborated.*

## 10. What this part does not solve (the declared residual)

This part moves update-adoption trust from *who shipped it* to *does it reproduce
and is it fresh*, and refuses both an authority and a push — the right choice for a
project whose every roster is a coercion target. It does **not** deliver a patched,
secure fleet. The gaps are real and declared, not smoothed:

- **§10.1 — The unpatched-fleet residual, and its worst case: no push means no
  forced patch, and the compromised client provably may never hear of the fix.
  [primary residual]** A client whose user never manually adopts — offline,
  inattentive, or abandoned — runs its current release, vulnerabilities and all,
  **indefinitely** (UG-4). No override exists, because an override is a push. Worse,
  the clauses compose against the fleet: in the one scenario that matters most — a
  client running an **actively-exploited RCE** — the running binary is **already
  attacker-controlled**, and that is exactly the binary UG-9 says can lie about
  freshness and suppress the known-bad about itself. So the mechanism that would
  route the patch (gossip + staleness surface, UG-3/UG-5a) runs **inside the
  compromised process** and can be silenced. The honest conclusion: for the
  compromised-RCE case the honesty surface and gossip path provide **no** guarantee
  of delivery; the residual is not "slower patching" but **"the compromised subset
  may never adopt,"** a terminal state until out-of-band re-bootstrap (ID-8),
  bounded only by the user noticing by some channel outside the compromised client.
  UG-8b narrows this for the *rebuilding* opt-in client (it can refuse to run a
  self-proven-bad binary), not for the modal phone. This is the deliberate price of
  refusing a push and an authority, and it is named first and at full strength.
- **§10.2 — Revocation-without-authority is unachievable for the vulnerability
  class, and reduces to OP-2 for the modal client across more than one class.**
  Non-reproduction, downgrade, and equivocation are revocable authority-free *only
  for a client that can rebuild or reach an honest reproducer* (UG-8). "This
  reproducing build is backdoored" is never authority-free — no check decides
  source-honesty (OP-10 / Part 10 §10.1) — so revocation of a reviewed-but-malicious
  release rests on public review (I-1), on corroboration whose independence is
  unverifiable (RB-10 / GR-19a), and on the user choosing to act: OP-2 plus the
  social layer. For the **non-rebuilding or eclipsed modal client**, the non-
  reproduction and log-equivocation classes **also** reduce to OP-2 (only the
  arithmetic index-regression check survives self-verification) — the Part 10 §10.5
  reduction, inherited. The design's contribution is to make the known-bad *claim*
  permissionless, corroborated, dedup-disciplined (RB-10a) and **forceless** so it is
  never an authority; it contributes **no** mechanism that removes a bad-but-
  reproducing release from a running fleet.
- **§10.3 — The eclipsed client never hears the update, and its freshness machinery
  is gameable.** An eclipsed client (OP-2) touches no honest root, so UG-6's
  equivocation detection **cannot fire** — the victim never holds two conflicting
  roots. Under eclipse an adversary can pin the victim at a **stale, known-vulnerable
  index** (a silent downgrade UG-5 cannot catch, because the victim never witnesses
  the higher index), **suppress** every known-bad report about the running build, and
  show a **sybil-corroborated** frozen past. Freshness is a *relative* guarantee —
  fresher than what you've witnessed — and an eclipsed client has witnessed only what
  the adversary allowed. For the non-rebuilding eclipsed client, "no authority,
  pull-only" means "trust the source-mixed quorum," and that holds **only as far as
  OP-2 does** — the reduction Parts 8 and 10 end on.
- **§10.4 — The never-adopting user is stuck by design.** UG-4's manual opt-in means
  a user who dismisses every offer stays on an old build; there is no override,
  because an override is a push. The design accepts a **non-zero steady-state
  fraction of the fleet on stale releases** as the declared cost of refusing a push,
  and surfaces staleness (UG-5a) rather than acting on it.
- **§10.5 — First-update TOFU inherits Part 10 §10.8 and is strictly worse for
  freshness.** A compromised first binary can lie about currency as easily as about
  reproduction — freezing the user at a stale index forever, undetectably from inside
  (UG-9). First-notion-of-latest is TOFU, corroborated only out-of-band.
- **§10.6 — Shared tooling, not shared authority, must be re-audited for the update
  log.** Reusing the map's / Part 10's log construction and gossip channel (RB-2a,
  ID-11a) is free *only* while no party's role is load-bearing for both the map/code
  and the update line. A conforming deployment MUST keep the release-line log's
  appenders a non-roster (UG-2) and SHOULD use a log set independent of the map's
  (ID-7b), so "convenience: reuse the same operators" does not silently re-create the
  cross-cutting kill switch ID-11 forbids. The fork-vs-escape case is a further
  residual: an honest hard fork (legitimate divergence) and an adversary opening a
  parallel line to escape a downgrade/known-bad on the tracked line are
  **indistinguishable at the protocol level** — both are a new `line_id` (UG-2c).
  UG-2c makes the *existence* of a second line visible; it does not decide *intent*,
  which is a social / OP-2 judgement, not a cryptographic one.

The honest summary: this part refuses both an authority and a push, and in exchange
is **silent** on forcing a patch (§10.1), **cannot cryptographically revoke a
reviewed-but-malicious release** (§10.2), **reduces to OP-2 under eclipse** (§10.3),
**leaves the never-adopting user stuck by design** (§10.4), and is **TOFU on the
first notion of "latest"** (§10.5). The correct response is to bound them — loud,
permissionless, dedup-disciplined known-bad gossip (UG-7/UG-8), a visible staleness
surface (UG-5a), out-of-band first-update corroboration (UG-9a), self-verifying
opt-in refuse-to-run for the rebuilder (UG-8b), aggressive source-mixing (UG-3a) —
and to **state** the patch-latency trade in the UI and the spec, not hide it behind
"no auto-update is safer."

## 11. Requirements introduced here

- **UG-1 / UG-1a** — no release authority; adoption binds to reproduction and
  freshness, never to publication (restates RB-2 at the adoption boundary).
- **UG-2 / UG-2a / UG-2b / UG-2c** — permissionless log-append announcement, no
  signer; signed and unsigned carry identical adoption weight; the release line is
  owned by no party — `line_id` is a reproduction-verifiable manifest chain from a
  genesis, a fork is a visibly distinct line.
- **UG-3 / UG-3a / UG-3b / UG-3c** — discovery is pull/gossip only, no push;
  source-mixed, privacy-bounded, client-clocked; never a fetch reactive to a peer
  signal (that is the ID-9a re-fetch downgrade).
- **UG-4 / UG-4a / UG-4b / UG-4c** — adoption is manual opt-in; a four-gate checklist
  with no signature gate; a declared conservative policy; offer and install are
  mechanically distinct with no automatic transition.
- **UG-5 / UG-5a** — never silently accept a lower index (reproducible-downgrade);
  staleness is surfaced on PS-9, not acted on (the deliberate asymmetry with ID-9a).
- **UG-6 / UG-6a** — split-view on freshness caught by gossiped roots + consistency
  proofs; index-equivocation is the cross-vantage signature, disambiguated from
  single-vantage downgrade and deduplicated.
- **UG-7** — five mandatory release anomalies, gossiped, deduplicated per RB-10a.
- **UG-8 / UG-8a / UG-8b** — known-bad is a permissionless, RB-10a-disciplined,
  forceless report, never an authority; a vulnerability-class report annotates but
  never gates an offer; revocation can only inform; self-verifying opt-in
  refuse-to-run is authority-free and permitted, external-evidence refuse-to-run is
  forbidden.
- **UG-9 / UG-9a** — the first update is declared TOFU over independent channels; a
  compromised first binary can lie about freshness, corroborated only out-of-band.

UG-1 and UG-4 are the load-bearing two: no authority, and adoption is a manual act
bound to reproduction. Both are bounded, not absolute — UG-1 reduces to OP-2 for the
non-rebuilding or eclipsed client (§10.2, §10.3), and UG-4's no-push buys the
unpatched-fleet residual (§10.1), whose worst case — a compromised client that
provably may never hear the patch — is named at full strength rather than softened.
Break this part by naming a push path a conforming client MAY add, a signer that
gates adoption, a way a known-bad report forces an action or censors an honest
release past UG-4b, a way to extend a release line without reproduction (an owner of
the line), or a way the non-rebuilding client is left trusting a majority that is not
OP-2. That is the invitation, in the Part 8 voice.
