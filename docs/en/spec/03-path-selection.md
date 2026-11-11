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

## 6. What this part does not decide

The disjointness dataset's trustless distribution, and formal verification that
a chosen set is as disjoint as claimed (OP-1); honest viable-size thresholds
and whether `n = 2, k = 2` is worth running at all (OP-3); guard rotation
economics; path selection over the blackout mesh, where AS and jurisdiction
mean nothing (OP-6). `poc/network_sim.py` is the executable strawman behind
this part — attack its model, then this text.
