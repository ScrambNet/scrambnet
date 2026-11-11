# ScrambNet Specification — Part 3: Circuit Construction and Path Selection

**Status: DRAFT, and the least settled part of the spec.** This is the
load-bearing wall of the *operational* security (the I-2 content floor stands
without it, but linkage protection and the whole k-path story live here).
Strawman values marked `(s)`. The disjointness-verification problem is OP-1 and
openly unsolved; this part states the target and a first mechanism to attack.

## 1. Scope and why this is hard

Dispersal (Part 1) makes content unconditionally safe below `k` captured
shares. That guarantee is only *operationally* real if the `n` share-circuits
are genuinely disjoint — otherwise one adversary vantage point sees `k` shares
and the floor, though mathematically intact, is never reached. This part
decides how a client, holding only its own verifiable gossip sample (Part 2)
and no trusted map, selects `n` circuits that an adversary cannot cheaply sit
across. Everything here must hold against relays that lie about everything
except what their signatures bind (GR-2).

## 2. Disjointness targets

- **PS-1.** The `n` circuits of one message MUST be *node-disjoint*: no relay
  appears on two of them. This is the floor, always enforceable if the sample
  is large enough.
- **PS-2.** The client SHOULD additionally seek, in decreasing order of value
  and increasing order of difficulty: **AS-disjoint** (no two circuits share
  an autonomous system at guard or exit), then **jurisdiction-disjoint** (no
  two share a legal jurisdiction). Each level it cannot meet MUST be reported
  to the user, not silently skipped (PS-9).
- **PS-3.** Within one circuit, the guard, middle, and exit MUST be node-
  distinct, and SHOULD be AS-distinct. A circuit whose guard and exit share an
  AS is an end-to-end correlation gift and MUST NOT be used when any
  alternative exists.

## 3. Inference without self-declaration

- **PS-4.** GR-3 forbids relays from declaring location, so the client infers
  the AS and jurisdiction of each relay from its `addrs` using *its own*
  dataset (e.g. a periodically refreshed IP-to-AS map), never from anything
  the relay says. The dataset's distribution MUST itself obey I-3: no single
  authoritative source. That dataset is specified in [Part 8](08-inference-dataset.md)
  (a reproducible, content-addressed map; no authority; declared error rate).
- **PS-5.** Inference is uncertain, and the client MUST treat it so: when the
  AS or jurisdiction of a relay is unknown, it counts as *potentially shared*
  with every other unknown — the conservative assumption, never the optimistic
  one.

## 4. Guards

- **PS-6.** Each client maintains a small set of **guard relays** (strawman: a
  primary guard per circuit position, rotated on a schedule of months, not
  minutes), following Tor's guard rationale: rotating entry points fast
  multiplies the chance of eventually drawing a hostile one. Guards MUST be
  chosen AS-disjoint from each other so that the `n` circuits do not funnel
  through one AS at entry.
- **PS-7.** Guard selection is weighted by *verified* bandwidth (GR-7), never
  claimed; a relay with an unverifiable claim is treated as low-bandwidth, not
  high.

## 5. Small networks: degrade, and say so

- **PS-8.** When the client's verified sample cannot supply `n` AS-disjoint
  circuits, it MUST fall back in a fixed order — AS-disjoint → node-disjoint →
  independent draws — and MUST NOT silently proceed as if the stronger
  property held. Parameters MAY be reduced (small-network mode: `n = 2, k = 2`
  with best-effort disjointness) when the estimated viable size is not met.
- **PS-9.** The client MUST expose the disjointness level actually achieved for
  a message, in terms a non-expert reads correctly: the crowd is small today;
  this is what you are buying. The content floor (I-2) and the linkage level
  are separate statements and MUST be shown separately.
- **PS-10 (sybil-resistant size estimate).** The viable-size estimate MUST
  count only independently verified relays and observed AS diversity, never
  raw record count, so that an adversary cannot inflate the network with sybils
  to trick clients into full parameters whose diversity is fake (ties to OP-2).
- **PS-11 (believed disjointness is not real disjointness).** The protection a
  client builds is only as good as its inference dataset, and the client MUST
  treat the dataset's error rate as a first-class security parameter, not an
  implementation detail. The simulator (`poc/network_sim.py`, §1) separates
  *ground truth* — which the adversary exploits — from the client's *belief*,
  and sweeps the inference-error rate: as error rises, AS-disjoint selection
  becomes partly illusory and both the content-break rate and the linkage leak
  rise monotonically. Two consequences are normative:
  (a) for **random** inference error (noise, a merely inaccurate map), the error
  erodes **linkage far faster than content** — a content break still needs the
  adversary on `≥ k` circuits at once, so the floor holds while metadata
  degrades first; the UI MUST NOT present a low content-break number as if it
  also bounded linkage. This asymmetry holds **only for random error**; an
  *adversarially chosen* map is not noise (see PS-12);
  (b) a thinner **gossip sample** (PS-10, I-3) forces fallback sooner: a client
  that knows too few relays cannot build AS-disjoint circuits at all and drops
  to `none`, where the break rate jumps (§2). The viable-size estimate (PS-10)
  MUST therefore account for the *reachable* sample, not the whole network.
  The zero-error, full-view numbers are the best case; a conforming client MUST
  present the achieved level (PS-9) from its real, noisy, partial view.
- **PS-12 (a hostile map must not steer selection onto the adversary).**
  `[claim-critical]` An *adversarially chosen* map is not random error, and the
  PS-11(a) asymmetry does **not** protect against it. A map the adversary
  controls has two levers over AS-disjoint selection: give the adversary's own
  co-located relays *distinct* fake ASes (so they never exclude each other), and
  give *honest* relays *colliding* fake ASes (so that once circuit 1 picks one
  honest relay, every other honest relay looks AS-shared and is filtered out).
  The honest candidate pool then collapses after the first draw and the client
  selects circuits 2…`n` almost entirely from adversary relays — landing the
  adversary on guard **and** exit of `≥ k` circuits **deterministically**, a
  *content* break, while the client still believes it achieved AS-disjointness
  and raises no fallback warning. Demonstrated against `poc/network_sim.py`: a
  steering map drives the content-break rate from ~0% to **100% at ~15%**
  adversary ownership (vs a low single-digit rate for an honest map at 35%). So
  **a bad map CAN reach content, not only linkage** (this corrects an earlier
  overstatement; Part 8 ID-8a is corrected to match). The defenses a conforming
  client MUST apply:
  1. **Do not let the map alone collapse the honest pool.** A client MUST NOT
     build a circuit set in which more than a bounded fraction of the circuits
     depend, for their claimed mutual disjointness, on relays the client cannot
     *independently* corroborate as distinct (GR-8 source mixing, PS-10 "count
     only independently verified"). If believed-disjoint selection would draw
     circuits 2…`n` from a pool the map has made suspiciously small, the client
     MUST treat that as a fallback/anomaly condition (PS-8, PS-9), not a success.
  2. **A map that implies an implausible AS structure is itself an anomaly.** A
     map under which the client's *reachable honest sample* collapses to one or a
     few ASes while the adversary-shaped remainder is maximally diverse is a
     signature of steering; the client SHOULD gossip it as a map anomaly
     (Part 8 ID-10) and fall back.
  3. **Rebuild is the real defense.** A steering map is not reproducible from
     public inputs (Part 8 ID-5a); a client that rebuilds, or agrees with one
     honest peer who did, rejects it. Until then the client MUST treat an
     unverified map's disjointness claims as unverified, not as achieved (PS-9).
  The honest residual remains: within the eclipse window of a client that has
  accepted an unverified steering map and cannot yet rebuild, the content floor
  can fall. This is bounded by `k`/`n` margin and by the defenses above, not by
  a claim that it cannot happen. The attack and defense 2 are **executable** in
  `poc/network_sim.py` (`make_steering_map`, `detect_steering`,
  `select_paths_ps12`): the undefended selector breaks content on 100% of
  messages at 20% ownership, and the PS-12 detector turns that into a
  fallback/anomaly on 100% of them with **zero** false positives on honest maps
  (tests in `test_network_sim.py`). A conforming client's detector MUST have a
  false-positive rate low enough not to deny service on honest maps — a defense
  that cries wolf is its own availability attack.

## 6. The verification procedure (PS-13…PS-19)

### 6.1 The procedure and its certificate

- **PS-13 (the procedure is a pure function of three declared inputs).**
  `[claim-critical]` Circuit construction MUST be expressible as a deterministic
  function
  ```
      verify(sample, map, corroboration, n, k)  ->  (circuits, certificate)
  ```
  of exactly three client-side inputs, and nothing else:
  - **`sample`** — the client's verified gossip sample of relays (Part 2, counted
    under PS-10: *only independently verified relays*);
  - **`map`** — the Part 8 inference map, named by its hash `H` and carrying its
    own measured error rate `e` (ID-12);
  - **`corroboration`** — a per-relay number `c_j ∈ [0,1]` stating how
    independently the relay's inferred AS/jurisdiction is corroborated (PS-15).
  The output is `n` circuits **and** a **disjointness certificate** (PS-14). No
  step may read the relay's self-declared location (GR-3, PS-4), a trusted
  directory (I-3), or ground truth (there is none to read — that is the whole
  problem). A conforming implementation that cannot express its selection as this
  pure function cannot emit a checkable certificate and is non-conforming: an
  implementer with this spec and the same three inputs MUST be able to rebuild the
  same circuits-and-certificate decision (I-1).

- **PS-14 (what the certificate contains — and how it is machine-checkable).**
  `[claim-critical]` The certificate is a canonical-CBOR record (Part 0 encoding)
  carrying **exactly** the fields a second party needs to **recompute and confirm**
  it, and no field that asks to be trusted:
  1. **`map_hash`** — the `H` the certificate was computed against (ID-2). The
     certificate is meaningless without it: *"AS-disjoint"* is never a free-standing
     claim, only *"AS-disjoint under map `H`"*.
  2. **`map_error`** — the pair `(mismap_rate, unknown_rate)` the map shipped
     (ID-12), copied verbatim so the verifier need not re-measure it. Their sum is
     the per-lookup error `e` used below.
  3. **`circuits`** — for each of the `n` circuits, the relay IDs (GR-2 key
     fingerprints) at guard/middle/exit, and for the **pivots** (guard and exit —
     the two positions an AS-level adversary correlates, PS-3) the **believed**
     `(AS, jurisdiction)` the map assigned, or `unknown`.
  4. **`corroboration`** — the per-pivot `c_j` used (PS-15), so the verifier
     recomputes with the same reductions.
  5. **`class`** — the achieved disjointness class, one of `as` / `node` / `none`
     (PS-2 order), i.e. the *strongest* property the set actually satisfies under
     the map, not the one requested.
  6. **`confidence`** — a number in `[0,1]` (PS-16), the conservative lower bound
     on the probability the `class` claim holds given the map's error bars and the
     corroboration.
  7. **`steering_flag`** — the PS-12 detector's verdict on the client's **full
     reachable sample** (PS-17), and the pool-survival ratio behind it.
  A verifier **holding the same map `H`** MUST be able to: (a) re-look-up every
  pivot's `(AS, jurisdiction)` in `H` and confirm it matches field 3; (b)
  recompute `class` from those lookups by the PS-2 disjointness test; (c) recompute
  `confidence` from fields 2, 4, 5 and 7 by the PS-16 formula **as declared**; and
  (d) confirm the record is internally consistent. If any recomputation disagrees,
  the certificate is **invalid** and MUST be rejected (it was computed against a
  different map, or forged). The certificate binds no signature: like the map
  itself (ID-11), **reproduction, not signature, is the arbiter.**

  **What the verifier can and cannot re-derive — stated honestly (a hostile
  review's finding).** Two fields are *inputs the originating client measured*,
  not quantities a remote verifier can recompute from `H` alone:
  `steering_flag`/`pool_survival` are functions of **that client's full reachable
  gossip sample** (PS-17), which is not a certificate field; and each `c_j` is
  that client's **corroboration measurement** (PS-15), also not re-derivable from
  `H`. So the certificate is checkable **relative to its declared inputs** — a
  verifier confirms the confidence follows from the stated `map_error`,
  `corroboration` and `steering_flag` by the PS-16 formula — but it is **not** an
  unconditional proof: a client that **lies** about its own `c_j` upward, or omits
  a steering flag its sample would have raised, produces a certificate that
  recomputes *consistently* and is still wrong. The defenses against that are not
  in the certificate but in the network: an independent client over the same `H`
  and an overlapping sample derives a **different** certificate, and the
  divergence is gossiped as an anomaly (PS-19, ID-10) exactly as a map divergence
  is. The certificate removes the *silent* "AS-disjoint: yes"; it does not make a
  lying client's confidence self-proving. This is a declared limit (§6.6), not a
  hidden one.

### 6.2 Corroboration: the per-relay confidence input

- **PS-15 (per-relay corroboration is independent agreement, counted like PS-10).**
  The input `c_j` for a relay is **not** a trust score and MUST NOT be sourced from
  the relay or from any single party. It is the degree to which the relay's
  inferred AS is **independently corroborated** — the same "count only independently
  verified" discipline PS-10 applies to size estimates and GR-8 applies to gossip:
  - `c_j = 0` — the relay's AS comes from the map `H` **and nothing else**; the
    client has no second vantage. This is the default and the conservative floor.
  - `c_j` rises toward `1` as **independent, source-mixed** vantages (GR-8) agree
    on the same inferred AS for that relay: a second reproducibly-built map from a
    disjoint collector set (ID-3a), an out-of-band observation of the relay's
    announced prefix, a peer's gossiped certificate pivot that matches. Strawman
    (s): `c_j = 1 − 2^(−v)` for `v` independent corroborating vantages (one
    vantage ⇒ 0.5, two ⇒ 0.75, …), capped below `1` because no finite number of
    overlay vantages sees the rack (§6.6).
  A relay the map labels `unknown` has `c_j = 0` **and** contributes an
  already-conservative `unknown` believed-AS (PS-5): it collides with everything,
  so it rarely survives into a pivot position, and when it does the confidence
  formula already treats it as fully uncertain (PS-16). Corroboration MUST NOT be
  inferred from how *many* peers report a value before GR-8/PS-10 source-mixing is
  applied — a sybil cannot vote a relay's AS into high corroboration by sheer
  numbers (ties to OP-2, exactly as ID-9).

### 6.3 The confidence formula

- **PS-16 (confidence is a conservative independent-mislabel lower bound).**
  `[claim-critical]` Let the **pivots** of a circuit set be the distinct relays at
  guard or exit across the `n` circuits (at most `2n`, fewer after dedup). The
  claimed disjointness holds **only if no pivot is mislabelled** in a way that turns
  a believed-distinct pair into a truly-colliding one. The map ships per-lookup
  error `e = mismap_rate + unknown_rate` (ID-12); corroboration reduces a pivot's
  **effective** mislabel probability to
  ```
      p_j = e · (1 − c_j).
  ```
  Treating per-pivot mislabels as **independent**, the certificate's `confidence`
  for `class = as` is the product
  ```
      confidence  =  Π_j ( 1 − e · (1 − c_j) )       over pivots j,
  ```
  floored to `0` by the PS-17 steering gate. For `class = node`, disjointness does
  not depend on the map at all (node identity is GR-2-bound, not inferred), so
  `confidence = 1 − (PS-17 gate)`. For `class = none`, `confidence = 0` by
  definition: no disjointness is claimed, so none is attested.

  **The independence assumption, named and justified as conservative.** Real pivot
  mislabels are **not** independent: one wrong BGP prefix in the map mislabels every
  relay under it at once (positive correlation). We assume independence anyway, and
  it is **conservative in the direction that matters** for a *lower bound*: the
  product `Π(1 − p_j)` under-counts the *correlated* case where several pivots share
  one mislabel cause — when mislabels are correlated, the probability that *at least
  one* pivot is wrong is **lower** than the independent product implies, so the true
  "all pivots correct" probability is **higher** than our bound. The product is thus
  a floor on confidence, i.e. it never over-states safety. Where independence would
  make us *over*-confident is a shared *honest* cause (one giant correct AS), which
  does not threaten disjointness; the adversarial shared cause — one map collapsing
  the pool — is not handled by this product at all but by the PS-17 gate, which
  floors confidence to 0 regardless of the product. So the two failure shapes are
  split cleanly: **random/correlated map error → the product (conservative);
  adversarial map structure → the gate (hard floor).**

  Grounding (not hand-waved). Against `poc/network_sim.py`, with no corroboration
  (`c_j = 0`, so `p_j = e`), `1 − confidence` upper-bounds the **observed** real-AS
  collision rate of the pivots at every error level — e.g. at `e = 0.2`,
  `1 − confidence ≈ 0.83` against an observed real-disjointness failure of `≈ 0.18`:
  pessimistic, which is the correct direction for a security floor, never optimistic.
  Corroboration recovers it monotonically (at `e = 0.2`, mean confidence rises
  `0.17 → 0.43 → 0.84 → 0.99` as uniform `c_j` goes `0 → 0.5 → 0.9 → 1.0`). A
  conforming client SHOULD present this honest pessimism rather than tighten the
  bound with a model that assumes more than the three declared inputs justify — a
  defensible floor beats false precision (PS-11).

### 6.4 Robustness to PS-12, by construction

- **PS-17 (the steering gate floors confidence — on the right signal, over the
  FULL reachable sample).** `[claim-critical]` Before the product of PS-16 is
  reported, the procedure MUST apply the PS-12 defense-2 detector
  (`detect_steering`) to the client's **entire reachable gossip sample**, not to the
  `2n` chosen pivots — the structure lives in the *population* and is gone from the
  pivots by the time they are drawn (checking the pivots alone catches a steering
  map on only ~half of messages). **The signal must be the one the adversary cannot
  avoid.** A first version of this detector keyed on "one giant believed-AS holding
  the collapsed honest pool, surrounded by singletons", and a hostile review
  **evaded it** by collapsing the honest pool into a *few* fake ASes instead of one
  giant — no giant AS, detector silent, content broken on ~30% of messages. The
  correct, load-bearing signal is the **anomalous singleton fraction**: to make its
  co-located relays look AS-disjoint the adversary MUST give each a distinct fake
  AS, i.e. make them singletons, and a real network has very few singleton ASes.
  The detector MUST therefore fire when singleton relays exceed a small fraction of
  the sample **and** the non-singleton relays sit in too few crowded ASes to build
  `n` disjoint circuits (the second clause keeps inference *noise*, which also
  makes singletons, from tripping it). Measured against `poc/network_sim.py`
  (`make_steering_map(honest_groups=g)` / the fixed `detect_steering`): this catches
  the **effective** steering regime (`g = 1…5`, a 10–100% content break) at ~100%
  with **0%** false positives on honest maps even at inference error up to 0.4.
  Therefore:
  - If the detector fires on the reachable sample, the certificate MUST set
    `steering_flag = true`, `class = none`, and `confidence = 0`, and the client
    MUST treat the result as the PS-12 fallback/anomaly condition (gossip it,
    ID-10; degrade and say so, PS-8/PS-9) — it MUST NOT emit an `as` certificate.
  - **Declared residual:** a *marginal* steering map that spreads the honest pool
    across enough fake ASes (`g ≥ 8`) to build genuinely disjoint circuits escapes
    the detector — but there its content break is only ~5%, indistinguishable from
    a small legitimate network, and bounded by the `k`/`n` margin and the PS-16
    confidence, not by a claim that it cannot happen (§6.6).

- **PS-18 (pool-collapse precondition — PS-12 defense 1, folded in as a confidence
  input).** `[claim-critical]` Independently of the structural detector, the
  procedure MUST compute the **honest-pool survival ratio**: the fraction of the
  reachable, independently-corroborated sample (PS-10, PS-15 with `c_j > 0`) that
  remains a *believed-distinct-AS* candidate **after** the first circuit is drawn.
  A certificate MUST NOT claim `class = as` when circuits `2…n` were drawn from a
  pool the map collapsed below a bounded fraction (strawman (s): survival `< 1/n` of
  the corroborated honest sample), because then the set's claimed mutual
  disjointness rests on relays the client cannot *independently* corroborate as
  distinct — exactly PS-12 defense 1. In that case the procedure MUST either lower
  `class` to `node` (dropping the map-dependent claim entirely) or set the anomaly
  condition as in PS-17. **The confidence is LOW exactly when PS-12 says the client
  is being steered:** the gate zeroes it on the structural signature, and the
  survival precondition strips the `as` claim when the pool is suspiciously thin —
  so a steering map cannot earn a high-confidence `as` certificate by either lever
  (distinct-fake adversary ASes or colliding-fake honest ASes). This is the
  non-negotiable property, and it is verified, not asserted: the same gate that the
  PS-12 tests show turns a 100% content break into a 100% fallback drives the
  certificate confidence to 0 on 100% of steering maps.

### 6.5 A worked certificate

Inputs: `n = 4`, `k = 3`; a healthy sample; map `H = 0x9f2c…a17b` shipping
`map_error = (0.04, 0.03)` so `e = 0.07`; the 8 pivots (4 guards + 4 exits) — 6
corroborated by one extra independent vantage (`c_j = 0.5`), 2 resting on the map
alone (`c_j = 0.0`); the steering detector does **not** fire on the reachable
sample. Then `p_j = 0.035` for the six and `0.07` for the two, and
`confidence = (1−0.035)^6 · (1−0.07)^2 = 0.698`.

```
disjointness-certificate (canonical CBOR; shown as a record):
  map_hash      : 0x9f2c3e...a17b
  map_error     : { mismap: 0.04, unknown: 0.03 }         # e = 0.07 (ID-12)
  class         : "as"                                     # strongest met, PS-2
  confidence    : 0.698                                    # PS-16 product, gate=1
  steering_flag : false                                    # PS-17, full-view check
  pool_survival : 0.61                                     # PS-18, > 1/n = 0.25 OK
  circuits:
    - { guard: 4a1f.., mid: 7c02.., exit: e9d3..,
        pivots:[{as:3356, jur:"US", c:0.5},{as:1299, jur:"SE", c:0.5}] }
    - { guard: b17c.., mid: 02aa.., exit: 55f1..,
        pivots:[{as:3320, jur:"DE", c:0.5},{as:9002, jur:"GB", c:0.0}] }
    - { guard: cc90.., mid: 1d44.., exit: a7e8..,
        pivots:[{as:6830, jur:"NL", c:0.5},{as:2914, jur:"JP", c:0.5}] }
    - { guard: 3e5b.., mid: f108.., exit: 9b22..,
        pivots:[{as:174,  jur:"US", c:0.0},{as:8075, jur:"IE", c:0.5}] }
```
Read correctly (PS-9): *"These 4 circuits are AS-disjoint **under map `H`**, which
admits a 7% error rate; given how independently each relay's AS is corroborated,
there is at least a **70% chance** the AS-disjointness is real and not an artifact
of a mislabel. It is not a guarantee, and it says nothing about a data center the
map cannot see (§6.6)."* Had the steering detector fired, every number above would
be replaced by `class: none, confidence: 0, steering_flag: true` and a fallback
warning — there is no high-confidence certificate for a steered client.

```
  THE PRODUCE-CIRCUITS-AND-CERTIFICATE FLOW

   sample (PS-10)      map H + e (ID-12)      corroboration c_j (PS-15)
        │                   │                        │
        └─────────┬─────────┴───────────┬────────────┘
                  ▼                      ▼
        ┌───────────────────┐   ┌─────────────────────────────┐
        │ detect_steering    │   │ believed-AS disjoint select │
        │ on FULL sample     │   │ (PS-2 order: as→node→none)  │
        │ (PS-17, defense 2) │   │  + pool-survival (PS-18,    │
        └─────────┬─────────┘   │     defense 1)              │
                  │             └──────────────┬──────────────┘
          fires?  │                            │ n circuits + pivots
         ┌────────┴────────┐                   ▼
       yes               no        ┌────────────────────────────┐
         │                 └──────▶ │ confidence = Π(1−e(1−c_j))  │ PS-16
         ▼                         │ class = strongest met       │
  class=none, conf=0               └──────────────┬─────────────┘
  steering_flag=true                              ▼
  → fallback + gossip        ┌─────────────────────────────────────┐
    (PS-8/9, ID-10)          │ CERTIFICATE {map_hash, map_error,    │
                             │  circuits, corroboration, class,     │
                             │  confidence, steering_flag}          │
                             └──────────────┬──────────────────────┘
                                            ▼
                     a verifier with the SAME H recomputes and confirms
                     (reproduction is the arbiter — no signature, ID-11)
```

- **PS-19 (the certificate is for the user and the peer, both).** The `confidence`
  and `class` MUST drive the PS-9 honesty surface the user reads (*the crowd is this
  disjoint today, with this much certainty*), and the certificate MUST be gossipable
  so a peer holding the same `H` can re-derive it (PS-14) and so that a divergence —
  two clients, same `H` and sample, different certificate — is caught and gossiped
  as an anomaly (ID-10), the same immune signal Part 8 uses for map divergence. The
  UI MUST NOT quote `confidence` as if it bounded linkage: it bounds the **content**
  disjointness claim; metadata degrades faster (PS-11(a)), and a high confidence in
  `class = as` does not mean low linkage leak.

### 6.6 What this does not solve

The certificate attests **consistency against a bounded-trust dataset, not true
disjointness** (Part 8 §10), and the honesty of this whole procedure is in saying
so on every record. An adversary who co-locates relays in one rack while announcing
address space that the public BGP/RIR data **truthfully** attributes to different
ASes is labelled disjoint by the **correct** map — so the lookups match `H`, the
steering detector does not fire (the structure is not a steering signature, it is
the genuine public routing table), the pool does not collapse, and the pivots are
well-corroborated **because every honest vantage agrees with the map**. The
procedure therefore issues a **high-confidence `as` certificate that is
nonetheless wrong**: `confidence` measures the chance the set is disjoint *under the
map*, and here the map is right and the overlay still cannot see the rack. This is
the Part 8 §10 co-location residual, and it is the one limitation the certificate
**cannot** remove — no amount of corroboration closes it, because corroboration
only confirms agreement *with public data*, and the public data itself is what the
adversary satisfied. Its magnitude is exactly the simulator's gap between believed
and true AS at `infer_error = 0`: the certificate reads 1.0, reality can still
collide, and only raising `k`/`n` margin — not any certificate field — bounds the
loss. The certificate's gift is that it never **hides** this: it states its own
error bars, floors itself to zero under steering (PS-17/18), and is checkable by
anyone with the map (PS-14). It turns "AS-disjoint: yes" — a lie — into
"AS-disjoint under map `H` with error `e`, confidence `c`" — a true statement whose
one remaining blind spot is named here and nowhere hidden.

Three further limits a hostile review surfaced, declared here rather than papered
over:

- **Marginal steering escapes the detector.** A steering map that spreads the
  honest pool across enough fake ASes (`g ≥ 8`) builds genuinely disjoint circuits
  and so does not trip the singleton-fraction detector (PS-17) — but its content
  break is then only ~5%, the level of a small legitimate network, bounded by the
  `k`/`n` margin and the PS-16 confidence. The detector catches the *effective*
  steering regime (10–100% break), not every map.
- **A lying client's confidence is not self-proving.** `confidence` is only as
  honest as the `c_j` and `steering_flag` the originating client measured and put
  in the certificate; a client that overstates its own corroboration, or omits a
  flag, emits a certificate that recomputes consistently and is still wrong
  (PS-14). The catch is social, not arithmetic: an independent client over the
  same `H` derives a different certificate, and the divergence is gossiped as an
  anomaly (PS-19). The certificate removes the *silent* lie, not a *detectable*
  one.
- **The confidence product bounds pivot-pair collisions, not every collision.**
  PS-16 measures the chance a believed-disjoint pivot *pair* is truly colliding.
  A mislabel that collides a pivot with a *middle* hop, or confuses jurisdiction
  for AS, is outside the product and must be caught by the PS-2 disjointness test
  on the full circuit, not read off the confidence number.


## 7. What this part does not decide

The disjointness dataset's trustless distribution, and formal verification that
a chosen set is as disjoint as claimed (OP-1); honest viable-size thresholds
and whether `n = 2, k = 2` is worth running at all (OP-3); guard rotation
economics; path selection over the blackout mesh, where AS and jurisdiction
mean nothing (OP-6). `poc/network_sim.py` is the executable strawman behind
this part — attack its model, then this text.
