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
  (a) the error erodes **linkage far faster than content** — a content break
  still needs the adversary on `≥ k` circuits at once, so the floor holds while
  metadata degrades first; the UI MUST NOT present a low content-break number
  as if it also bounded linkage;
  (b) a thinner **gossip sample** (PS-10, I-3) forces fallback sooner: a client
  that knows too few relays cannot build AS-disjoint circuits at all and drops
  to `none`, where the break rate jumps (§2). The viable-size estimate (PS-10)
  MUST therefore account for the *reachable* sample, not the whole network.
  The zero-error, full-view numbers are the best case; a conforming client MUST
  present the achieved level (PS-9) from its real, noisy, partial view.

## 6. What this part does not decide

The disjointness dataset's trustless distribution, and formal verification that
a chosen set is as disjoint as claimed (OP-1); honest viable-size thresholds
and whether `n = 2, k = 2` is worth running at all (OP-3); guard rotation
economics; path selection over the blackout mesh, where AS and jurisdiction
mean nothing (OP-6). `poc/network_sim.py` is the executable strawman behind
this part — attack its model, then this text.
