# ScrambNet Specification — Part 4: Chameleon Transports

**Status: DRAFT, and the part most likely to rot.** This part states a transport
threat model and an honest realism assessment. It commits no outward mechanism
and promises no victory in the censorship arms race. Read §1 and the realism
assessment (§8) first: between them they say the one narrow thing this part is
willing to claim, and the much larger thing it refuses to. Strawman values are
marked `(s)`.

Architecture layers L1 (chameleon) and L3 (ephemeral transports) live here; the
transport is the thing that carries a share's bytes past a censor. This part is
filed under OP-7 (reachability and bootstrap), and it depends on, rather than
solves, the zero-contact bootstrap problem (OP-7, GR-10).

## 1. The decision, in two sentences

- **This part does not claim ScrambNet wins or sustains the censorship arms
  race.** It claims the opposite about its own importance: the confidentiality
  and dispersal floor (I-2) does **not** depend on the transport layer at all. A
  transport buys *reachability* — the ability to get a share's bytes to a relay —
  and reachability is allowed to fail, down the architecture degradation ladder
  (L1→L2→L3→L4) and, at a total shutdown with no mesh neighbour, all the way to
  zero, **without the content floor ever moving** (CT-16).
- **The honest, defensible claim is therefore narrow and must not be widened:**
  *we do not make losing the transport race impossible; we make losing it
  non-catastrophic for confidentiality.* A censor can cut reachability to zero;
  a censor still cannot read content below `k` shares, because that protection
  never rode the transport (CT-16, CT-18, CT-18a).

Everything below is the threat model that justifies this narrow claim and the
realism assessment (§8) that is its spine — the part's most important section,
not an appendix.

## 2. The transport threat model (what the 2026 censor actually does)

- **CT-1 (declare what you resist; silence is a concession). [normative]** A
  conforming transport description MUST state which of the CT-2…CT-7a adversary
  capabilities it claims to resist and which it concedes. An undeclared capability
  is treated as conceded (the I-1 completeness rule, for transports) — a transport
  that does not name an attack has not defended against it.
- **CT-2 (passive DPI / protocol fingerprinting).** The censor classifies flows by
  byte and structure signatures without reading content; the chameleon's job is to
  present no distinguishing signature of its own (CT-8).
- **CT-3 (TLS-fingerprint matching). [normative]** The censor fingerprints the TLS
  ClientHello. The 2026 baseline is **JA4 / JA4+** (FoxIO), not the retired JA3:
  JA4 **sorts** cipher suites and extensions before hashing and ignores GREASE, so
  it is robust to the extension-order *randomization* mainstream browsers now do.
  A conforming mimic MUST therefore match the target's cipher-suite *set*,
  extension *set*, ALPN, supported-versions and GREASE *pattern* — not merely its
  order, which JA4 no longer distinguishes. (A mimic that only randomizes order is
  not thereby hidden.)
- **CT-4 (SNI / ECH inspection).** The censor reads the cleartext SNI to learn the
  destination name. ECH can hide it, but only conditionally (CT-11).
- **CT-5 (active probing / connect-back).** The censor connects to a suspected
  endpoint and checks whether it behaves like what it claims to be; survival
  requires CT-10.
- **CT-6 (passive statistical classification of flow shape). [normative,
  residual-declaring]** The censor classifies flows by *statistics*, not bytes:
  timing, volume, direction, burst structure, **and entropy** — and the feature
  set is open and adversary-chosen, including learned (ML) classifiers. In
  particular, **high-entropy "fully-encrypted-traffic" detection** blocks flows
  that look *too random* with no probe and no fingerprint match (observed on the
  GFW since late 2021). This has a counter-intuitive consequence the rest of the
  part depends on: **randomized or high-entropy cover is a *brighter* signal, not
  a dimmer one** — the safest cover resembles a very common real protocol, never
  noise. CT-6 cannot be closed by byte-level mimicry (CT-8); its honest answers are
  at other layers (CT-12, CT-15).
- **CT-6a (TLS-in-TLS / nested-encryption detection). [normative,
  residual-declaring]** A transport that tunnels ScrambNet's own already-encrypted,
  I-4-uniform share traffic *inside* a mimicked outer TLS flow leaves
  characteristic record-size and timing patterns — a TLS flow that is *carrying
  another TLS handshake* — which DPI can flag even when the outer handshake is
  byte-perfect (CT-3/CT-4 clean). This is the marquee attack on nested
  circumvention and MUST be declared: a mimic can be perfect at the handshake and
  still be caught at the flow structure. It is a residual byte-mimicry cannot
  close (it belongs with CT-12); naming it is required by CT-1.
- **CT-7 (endpoint enumeration — blocking what is known). [normative]** The censor
  discovers and blocks known endpoints/bridges wholesale. Dispersal (CT-15) and
  social-graph bridge distribution (architecture L2, Lox) raise the cost; mimicry
  does not address enumeration at all.
- **CT-7a (endpoint discovery — the bootstrap front line, declared open).** Distinct
  from CT-7: *how a censored user obtains an unblocked endpoint in the first place,
  faster than the censor enumerates it.* This is the bridge-distribution problem
  (Lox / social graph) and it reduces to **OP-7 (zero-contact bootstrap), which is
  open.** Part 4 does not solve it; it cross-references it (GR-10, OP-7), and any
  claim that endpoints are reliably discoverable is an unbacked promise this part
  refuses to make.
- **CT-7b (protocol whitelisting — the limit case).** The censor permits only an
  allow-list of protocols/destinations and drops the rest (observed: Iran's
  national-network whitelist, 2025–2026). Against this, mimicry of an *allowed*
  destination is the only move, and even it fails when the censor accepts the
  collateral cost (§8, CT-14) — up to a total shutdown, where no transport reaches
  anything (CT-18a).

## 3. Mimic discipline (the treadmill, made normative)

- **CT-8 (no static project signature; imitate as-deployed). [normative]** A
  chameleon transport MUST NOT present a static, project-specific wire signature,
  and MUST imitate a target protocol *as actually deployed*, not an idealized one.
  A hand-rolled or frozen stack is itself a fingerprint and is non-conforming.
- **CT-9 (the uTLS drift clause). [normative]** A uTLS-style mimic MUST track the
  target's *currently deployed* ClientHello and MUST declare the target version it
  mimics (CT-20). Against JA4 (CT-3) the distinguisher is divergence in the cipher
  and extension *sets*, ALPN, supported-versions and GREASE pattern — these drift
  with each browser release, so a mimic frozen at version N becomes a distinguisher
  once the real population moves to N+1. This is a **maintenance treadmill with no
  terminal state**: there is no version at which the work is done (§8). The floor
  MUST NOT depend on keeping pace with it (CT-16).
- **CT-9a (prefer a high-population target — for anonymity-set reasons, not
  economic ones). [normative]** A conforming deployment SHOULD mimic a
  high-population, fast-moving target (a mainstream browser's TLS) rather than a
  niche one, for two *mechanical* reasons: the large herd is a better anonymity set
  (more real flows to hide among), and a fast-patching target shortens the CT-9
  staleness window. This clause makes **no** economic claim that the herd is "too
  expensive to block" — that bet is CT-13, declared defeasible, and the 2026 record
  (a national censor blocked the largest ECH herd, §8) shows it can be lost.

## 4. Active-probe survival

- **CT-10 (survive a connect-back probe; silence is itself a fingerprint).
  [normative]** A chameleon endpoint MUST survive an active probe: it MUST complete
  a *real*, valid handshake of the protocol it imitates and serve plausible cover
  behaviour to an unauthenticated prober (e.g. real TLS termination proxying to
  real-looking content), revealing the covert service only to a client proving a
  pre-shared secret. The modern model is terminate-real-TLS-and-proxy-to-a-real-
  site, **not** the older stay-silent model: *staying silent to an unauthenticated
  prober is itself a detectable behaviour* (characteristic timeouts, byte-acceptance
  thresholds, replay handling) and is non-conforming.
- **CT-10a (the pre-shared secret is a bridge line — its distribution is open).
  [normative]** The secret that distinguishes a real client from a prober in CT-10
  is a **bridge line**, and **its distribution is OP-7 / GR-10, declared open.**
  CT-10 assumes a secret already delivered; it does **not** solve delivery. Probe
  resistance and bootstrap are separate problems, and conflating them (assuming the
  secret is somehow already everywhere) is the error CT-7a forbids.
- **CT-10b (the cost thins the operator pool).** Real cover content, real
  certificates and real termination are a standing per-endpoint operational burden.
  Raising that bar is exactly what shrinks the volunteer-operator pool — which is
  the sustained-maintenance problem (§8) wearing an operational hat.

## 5. ECH posture (no overclaim)

- **CT-11 (ECH is opportunistic and availability-bounded, never a floor).
  [normative]** A conforming description MUST NOT present ECH (Encrypted Client
  Hello) as a solved SNI defense. It states: (a) ECH hides the SNI only where the
  fronting provider deploys it, the client supports it, **and the encrypted-DNS
  lookup that carries the ECH config succeeds** — block or downgrade that DNS and
  ECH silently does not engage, which is the actual 2026 failure mode; (b) 2026
  server-side deployment is a *minority-but-growing* slice, concentrated at a few
  large fronting providers, not the long tail, so "the SNI is hidden" is false for
  most destinations most of the time; (c) **"block ECH entirely" is an observed
  censor response** (a national censor blocking ECH connections to a major provider
  from late 2024), which ECH by construction cannot counter. ECH is an opportunistic
  improvement, not a guarantee. *(The ECH specification is the IETF TLS working
  group's ESNI/ECH work; this part does not pin a published RFC number, which was
  not yet confirmed at drafting — cite the current document, not a number that may
  be wrong.)*
- **CT-11a (degrade, don't leak). [normative]** Where ECH is unavailable or blocked,
  a conforming transport MUST degrade to the next rung of the ladder (L2 ephemeral
  bridges) rather than fall back to a distinguishable cleartext-SNI flow. The
  degradation path, not ECH, is the guarantee.

## 6. The flow-correlation residual

- **CT-12 (mimicry cannot defeat flow shape; say so). [normative,
  residual-declaring]** Byte-level mimicry MUST NOT be claimed to defeat flow-shape
  correlation (CT-6), nested-TLS detection (CT-6a), or a global passive observer
  correlating entry and exit. Timing, volume, direction, burst structure and
  nesting leak through a perfect mimic. These are residuals mimicry *cannot* close
  and MUST be declared, not hidden. The only honest answers are at other layers —
  dispersal spreads one message's shape across covers (CT-15, an *availability*
  property, not a shape-hiding one) and paranoid-mode mixing (architecture L2)
  trades latency for shape resistance — never the mimic itself. Website-oracle and
  entry-side confirmation attacks reduce to this same correlation residual and the
  global-passive-adversary row the threat model already declares out of fast-mode
  scope.

## 7. Share-dispersal across diverse covers (the normative verdict)

- **CT-15 (the verdict: diversity helps availability, hurts unobservability; buy
  the first, pay and declare the second). [normative]** Carrying the `n` shares of
  one message over *different cover types* (one in TLS, one in WebRTC, one on mesh)
  is a two-sided decision, resolved as follows:
  (a) it MUST NOT be assumed to improve **unobservability** — `n` covers are `n`
  fingerprints to get right (CT-3), `n` treadmills (CT-9), and a genuinely new
  harm: a **cross-cover correlation surface**. An adversary who sees a TLS flow, a
  WebRTC flow and a mesh burst that are timing/volume-correlated (CT-6) can link
  them as one message's shares *without breaking any single mimic* — diversity does
  not dim that signal, it can brighten it;
  (b) it is permitted and valued **strictly as an availability measure**: no single
  cover block kills delivery (`k < n` already buys this), and endpoint enumeration
  (CT-7) must now succeed against covers *individually* — which raises the censor's
  cost against a censor that blocks covers *one at a time*, and provides **no**
  benefit against a protocol whitelist (CT-7b) or a total shutdown (CT-18a), which
  block all covers in a single act.
- **CT-15a (sell it as reachability, never as camouflage). [normative]** A
  conforming client MUST NOT present multi-cover dispersal to the user as *stronger
  camouflage*; it MAY present it as *stronger reachability*. Conflating the two is
  the same linkage-vs-content category error ID-12a forbids for the map, restated
  for transports: multi-cover improves an availability property and does not improve
  a mimicry property.
- **CT-15b (minimum cover set left open; claims bounded by what is actually run).
  [normative]** Part 4 does **not** mandate a minimum cover set — mandating `n`
  covers mandates `n` maintenance treadmills the project may not be able to staff
  (§8). A client with an open/unspecified cover set MUST NOT claim any
  *quantitative* availability property (no "resists enumeration across N covers"
  without a stated, actually-run N); it MAY claim only the *qualitative* "no single
  cover block kills delivery," and only when it actually runs ≥2 independent covers
  with `k < n`. Whether to require ≥2 covers for the dispersed-delivery default is
  an owner decision (§8).

## 8. The honest realism assessment (the spine)

*(This section is the part, not an appendix. It is written in the §residual voice
of Parts 8 and 11.)*

**This part commits no outward mechanism and must not pretend to.** It is a verdict
about where the project is fragile, stated at full strength: **the transport layer
is the project's weakest and most-likely-to-rot layer, and the honest posture is to
say so and to design so the floor never depends on it.**

**The uTLS drift treadmill (CT-9).** A mimic frozen at a browser version becomes a
distinguisher the moment the real population moves on — a smaller, staler herd is a
*brighter* signal, not a dimmer one. There is no version at which the work is done.
Against JA4 the order no longer matters, but the cipher/extension *sets* still drift
with every release, so the treadmill is slower than it was against JA3 but does not
stop. The project does not get to win this; it gets to run on it or step off it, and
CT-16 is the decision to make stepping off survivable.

**ECH's 2026 reality (CT-11).** ECH hides the SNI only where provider, client *and
the encrypted-DNS lookup* all succeed, and in 2026 that is a minority of
destinations. "Block ECH entirely" has already been used by a national censor
against the largest fronting provider, which ECH cannot counter. ECH is an
opportunistic improvement bounded by deployment; the floor is the degradation path,
never ECH.

**The economic argument and its counter-examples (CT-13/CT-14).** "Blocking me costs
more than it earns" is a real deterrent and a false guarantee. The 2026 record has
repeated counter-examples of censors paying large collateral costs rather than permit
circumvention: a national regulator blocking ECH to a major provider (from late
2024); a national-network **protocol whitelist** permitting only a short allow-list
(Iran, 2025–2026); and **total internet shutdowns** during unrest (Iran, mid-2025 and
again in early 2026). Each is a censor choosing control over commerce. The economic
bet is probabilistic: it works against a censor who values the collateral and fails
against one who has shown they will not. We state this rather than hand-wave the
economics as settled. *(These are cited as categories of observed behaviour; a
conforming write-up should attach dates and jurisdictions and MUST drop any
counter-example it cannot stand behind — a wrong counter-example is worse than none,
CT-14.)*

**The uncomfortable question, answered (the central declared residual).** *Does a
pseudonymous volunteer project have the sustained-maintenance capacity a transport
arms race demands?* Tor has paid staff, a funded pluggable-transport ecosystem and
years of institutional memory, and it *still* loses rounds against determined
censors. A pseudonymous, no-roster project — one that by design (I-3, and the
governance of Parts 10/11) refuses the central coordination that would let it push a
transport update to everyone at once — has **less** of that capacity, not more. The
honest answer is therefore **no, not reliably.** The transport arms race rewards
exactly the funded, coordinated, identity-bound maintenance the project has renounced
for principled reasons. We should expect the mimicry layer to fall behind.

**And that is why nothing load-bearing sits on it.** The maintenance capacity to win
a transport arms race is exactly what we do not have and exactly what the floor does
not require. We expect the mimicry layer to fall behind; the architecture is a bet
that it may — the same bet the architecture already makes for the onion belt ("if all
of this computational layer someday falls, the network does not become readable — it
becomes less convenient") and that Parts 10/11 make for updates (refuse the push, pay
the latency, state it). This is honest pessimism about a capacity we lack, converted
into the design rationale that makes the shortfall non-catastrophic — not defeatism.

**The bottom of the ladder, conceded (CT-18a).** The degradation ladder L1→L2→L3→L4
has a bottom, and the bottom has a bottom. At a **total shutdown with no physical
mesh neighbour in reach**, no transport reaches anything and **no message is
delivered — full stop.** We do not make *that* survivable. The I-2 content floor
still holds (nothing is *revealed*; what cannot be sent cannot be read), but
reachability is zero, and the floor at that point is *intact and useless*: perfect
confidentiality of a message that cannot leave the device. The honest claim is not
"communication always gets through" — it is "confidentiality never depends on the
transport, and when the transport dies the secret dies with it undelivered, not
exposed." A mesh node in a hot blackout is itself a physically locatable act (Part 5,
OP-6), so even the last rung is an explicit, dangerous opt-in, not a guarantee.

## 9. The invariant guard

- **CT-16 (the floor does not depend on winning the race; confidentiality ≠
  availability). [normative]** No confidentiality or dispersal guarantee (I-2) MUST
  depend on any chameleon transport succeeding, on a mimic staying current (CT-9),
  on ECH being available (CT-11), or on the economic argument holding (CT-14).
  Transports buy **reachability only**. I-2 guarantees **confidentiality**
  (content below `k` is unreadable), a *delivered-vs-undelivered* property that is
  silent on whether anything is delivered — **not** a readable-vs-unreadable
  guarantee of delivery. Transport failure MUST degrade down the ladder
  (L1→L2→L3→L4), and at the bottom to zero reachability (CT-18a), **never**
  compromising content below `k`. A design in which losing the transport race loses
  the floor is non-conforming.
- **CT-17 (minimize reliance; do not promise to win). [normative]** A conforming
  posture MUST minimize the floor's dependence on mimicry rather than promise to
  sustain it. Where mimicry and degradation both answer a threat, the part MUST
  prefer the degradation path as the guarantee and treat the mimic as the
  convenience (the architecture's own maxim: everything that can expire is a
  convenience).
- **CT-18 (the declared ceiling: no arms-race-victory claim). [normative]** Part 4
  MUST NOT claim ScrambNet wins or sustains the censorship arms race. The only claim
  it makes is CT-16's: the transport layer is *allowed to lose* without the floor
  losing. Any text, UI or README asserting transport-level invincibility, a
  "sustainable" arms-race victory, or ECH-as-solved is non-conforming and MUST be
  corrected — including the threat-model national-censor row, which this part
  revises to split *reachability* (contested, may reach zero) from *content*
  (protected unconditionally, independent of transport).
- **CT-18a (the terminal case is stated, not hidden). [normative]** A conforming
  write-up MUST state the terminal case of CT-18 explicitly: at a total shutdown
  with no mesh reach, reachability is zero and no message is delivered; the content
  floor holds but is useless for that undelivered message. "We make losing the
  transport race survivable *for confidentiality*, not for delivery" is the exact
  claim, and nothing may be worded to imply delivery is guaranteed.

## 10. Operational honesty surface

- **CT-19 (surface the transport posture honestly). [normative]** A conforming
  client MUST surface its current transport posture on the existing honesty surface
  (PS-9): which cover it is using, whether ECH is *actually* in effect (not merely
  attempted), and that transport reachability — unlike the I-2 floor — carries **no**
  guarantee and may fail to zero. The message the UI states: *your content floor
  holds; your ability to reach the network does not.*
- **CT-20 (declare mimic staleness). [normative]** A conforming deployment SHOULD
  declare how current its mimic target is (CT-9), the transport analogue of the
  map's measured error rate (ID-12), so the user and the simulator can treat an
  out-of-date mimic as the fingerprint it is rather than silently trust it.

## 11. Requirements introduced here

- **CT-1 / CT-2 / CT-3 / CT-4 / CT-5** — declare-what-you-resist; passive DPI; JA4
  TLS fingerprinting (sets + GREASE, not order); SNI/ECH inspection; active probing.
- **CT-6 / CT-6a** — passive statistical/entropy/ML flow classification (randomness
  is a brighter signal); TLS-in-TLS nested detection — both residuals mimicry cannot
  close.
- **CT-7 / CT-7a / CT-7b** — endpoint enumeration vs endpoint *discovery* (the
  OP-7 bootstrap front line, declared open); protocol whitelisting.
- **CT-8 / CT-9 / CT-9a** — no static signature; the uTLS drift treadmill; prefer a
  high-population target for anonymity-set reasons, not an economic promise.
- **CT-10 / CT-10a / CT-10b** — survive a probe with real cover (silence is a
  fingerprint); the pre-shared secret is a bridge line whose distribution is OP-7;
  the cost thins the operator pool.
- **CT-11 / CT-11a** — ECH is opportunistic, DNS-dependent, block-ECH-observed, not a
  floor; degrade rather than leak cleartext SNI.
- **CT-12** — mimicry cannot defeat flow-shape/nested/correlation; the answers are at
  other layers, never the mimic.
- **CT-15 / CT-15a / CT-15b** — multi-cover dispersal helps availability, hurts
  unobservability, adds a cross-cover correlation surface; sell it as reachability
  not camouflage; claims bounded by covers actually run.
- **CT-16 / CT-17 / CT-18 / CT-18a** — the floor never depends on the transport;
  confidentiality ≠ availability; no arms-race-victory claim; the zero-reachability
  terminal case stated, not hidden.
- **CT-19 / CT-20** — honest transport posture on PS-9; declared mimic staleness.

CT-16 and CT-18 are the load-bearing two: the floor does not depend on winning the
transport race, and the part makes no claim that the race is won. The transport layer
is the one the project expects to lose rounds on, and it is architected so that
losing them costs *reachability*, never *confidentiality* — down to the terminal case
where reachability is zero and the undelivered secret is still a secret (CT-18a).
Break this part by naming a censor capability CT-2…CT-7b misses, a clause that
promises to win or sustain the arms race past CT-18, a place the I-2 floor is made to
depend on a transport succeeding, or a way multi-cover dispersal is sold as
camouflage past CT-15a. That is the invitation, in the house voice.
