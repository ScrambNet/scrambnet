# Design rationale — First-contact bootstrap (OP-7)

**Status: DESIGN RATIONALE, not specification.** This document maps the first-contact
bootstrap problem, records a candidate construction that was architected and attacked,
and states an honest verdict. It introduces **no normative requirement**: the central
result is that the construction *reduces* OP-7, it does not solve it, so nothing here
is ready to become a conformable `MUST`. It is kept in the same spirit as Part 4 §11
(an explored transport design, recorded with the reasons it did not ship) and the
first-contact-eclipse residual of Part 2 §7 — a design attacked and bounded is a
result, and writing down where the wall is stops the next contributor from re-deriving
it. The candidate requirements are labelled `BT-n` so a future Part could adopt the
pieces that survive; until then they are sketches, not a Part.

OP-7, as the threat model states it: **"Bootstrap with zero contacts."** A brand-new
client knows nobody and holds no network address, and must make first contact and
expand to full participation, against a censor, without violating the invariants.

## 1. The frame, stated once

Against a network-controlling censor, **something must cross an out-of-band channel
exactly once.** No overlay construction removes this — Tor does not, Snowflake does
not, decoy routing moves the out-of-band step to the politics of out-of-country ISP
deployment, which is a worse out-of-band channel, not none. So "zero-contact" is a
goal we inherit from the problem's name, not a reachable state. The real target, and
the one accepted as the starting point for this work, is:

> **Turn ONE out-of-band seed into full network access, with no censor-reusable single
> point (I-3), and no further out-of-band contact for expansion.**

The accepted seed channels are a site, a mirror, a QR code, or a person. The content
floor (I-2) is not in question here: by CT-16 the floor never rides the transport or
the bootstrap, so everything below concerns *reachability* at first contact, never
*confidentiality* of content.

## 2. The three adversaries, and the tension built into the problem

- **A — a national censor that actively enumerates.** It controls the country's
  network, can scan, can **pose as a brand-new user** to discover entry points and
  block them wholesale (enumeration is the first enemy of any bootstrap), and tolerates
  high collateral damage.
- **B — a censor that blocks but does not actively enumerate** (blacklist / DPI only).
- **C — a global passive observer** that does not block but observes everything to
  **deanonymize** the bootstrapping user, linking first contact to a real identity.

The requirement set for this pass was the hard one: **defeat all three at once, and
concede only where forced, by name.** The tension that makes that hard is structural
and worth stating before any mechanism: **A rewards a re-discoverable entry point**
(so access regrows after a block), while **C punishes any observable first contact**,
and **I-3 forbids the single point** that would make A easy. These three pull in three
directions. The rest of this document is where they fail to have a common solution, and
exactly what the minimal concession is.

## 3. The solution space

Each candidate: what it buys, where it meets an invariant, and which of A / B / C it
beats or loses to.

- **IP/port scanning.** The censor enumerates the same finite space **once** and
  blocks wholesale — defender-asymmetric in the *censor's* favour — and IPv6 makes the
  space too large for the *client* to scan too, so it dies for both sides. Dead as a
  primary mechanism; this is the enumeration asymmetry CT-7 names.
- **Hardcoded bootstrap nodes / `nodes.dat`** (eMule, BitTorrent
  `router.bittorrent.com`). Trivial first contact; the canonical single point; a
  standing kill switch. **Direct I-3 violation** — I-3 names "discovery … and
  bootstrap" explicitly. Rejected by invariant; this is the thing I-3 was written
  against.
- **Rationed bridge distribution** (Tor BridgeDB / moat / Lox: rationed email,
  HTTPS + CAPTCHA, Telegram, reputation levels). Raises the enumeration *rate* — an
  adversary posing as a user gets only a trickle per identity, and reputation makes
  blocked-bridge reporting cost something. But a patient A with many identities drains
  any public pool, and the distributor is itself an addressable, blockable
  quasi-single-point. **Keep the rate-limiting + social-graph idea; reject any single
  distributor.**
- **Domain fronting** (meek). Historically a strong "block me and you block the whole
  provider" deterrent. **Dead as a general technique**: major clouds disabled the
  host/SNI mismatch it relied on (2018), and it is a third-party-dependency mechanism —
  it works only while a specific large provider permits something they have every
  incentive to close, and a national censor has blocked the largest fronting/ECH
  provider (recorded in Part 4, CT-11). **Rejected as load-bearing**; usable only as
  one defeasible transport template, never the discovery anchor.
- **Snowflake + broker.** The proxies are ephemeral and numerous — enumerating them is
  bailing the sea. But it **moves the problem to the broker** that pairs client with
  proxy, a coordination point historically kept alive by the same domain fronting that
  is dying. The ephemeral-proxy idea is the reusable piece; the broker is the single
  point to dissolve.
- **Decoy routing / refraction networking** (Telex, TapDance, Conjure). The strongest
  property anyone has achieved for this problem: **no enumerable endpoint** — a
  complicit ISP router *outside* the censor's country watches for a cryptographic tag
  the client embeds in a connection to an innocuous allowed site, and deflects the
  tagged flow. The censor cannot block it without blocking the innocuous site and
  everything transiting that router. But it requires **out-of-country ISP/AS
  deployment**, an institutional dependency that has never scaled, and the privileged
  router is an I-3 single point of a *different* shape: it cannot be replaced by an
  *untrusted* substitute; it requires trusted, privileged substrate. **We take its goal
  (no enumerable endpoint) and refuse its mechanism** — a pseudonymous project with no
  roster and no funding has less institutional muscle than Tor, and decoy routing needs
  more, not less.
- **Public-infrastructure rendezvous** (a global DHT such as BitTorrent Mainline, or a
  public append-only log, as a rendezvous bulletin board the censor cannot selectively
  kill). Promising for I-3 — the substrate is untrusted and enormous, and exists for
  reasons unrelated to ScrambNet. But the public DHT is itself enumerable and
  poisonable; its keys are censor-derivable if formed from public constants (I-1 makes
  the scheme public); and — decisively — **the DHT's own join uses hardcoded
  well-known nodes**, a single point one layer down (§5, F-b). This is the backbone of
  the candidate construction, and also where most of its trouble lives.
- **Social / out-of-band / web-of-trust** (QR in person, a key read aloud). Maximal
  censor-resistance — a censor cannot block a conversation between two humans — and
  minimal scale. This *is* the accepted seed, not a full answer: it delivers first
  contact and nothing after.
- **Peer-exchange / gossip after entry.** Once the client holds **one honest peer**, it
  learns more peers from gossip without any authority (GR-6, GR-8). This is the
  expansion half, and ScrambNet already has it. It inherits the honesty of its first
  peer — a malicious first peer curates the entire view (the Part 2 §7 first-contact
  eclipse).

## 4. The candidate construction `BT-1 … BT-13` (as explored)

Shape: **one out-of-band seed → a non-enumerable read off public infrastructure to
expand → peer-exchange/gossip once inside.** Strawman values marked `(s)`. These are
recorded as explored, with the surviving strength of each stated in §5 — several are
weaker than first written.

- **BT-1 — the seed is a secret capability, not an address.** The one out-of-band seed
  is a high-entropy secret `S` (256 bits (s)), from which the client derives a
  rendezvous read key, an unblinding key, and a probe secret (CT-10a). The scheme is
  public (I-1); only `S` is secret. *Surviving strength: only over a replay-proof
  channel — see §5 F4.*
- **BT-2 — per-recipient seeds, social-graph budget.** A seed is minted per recipient
  and bound to a reputation budget so a captured seed is meant to drain only its own
  allowance before needing to be re-vouched. *Surviving strength: the enforced budget
  does not survive (§5 F1); the social-graph framing survives only after first
  admission.*
- **BT-3 — residual: seed compromise exposes the introducer edge.** Because trust is
  edge-bound (GR-20), a burned seed exposes the human who vouched — a non-rotatable
  identity at bootstrap (BL-18a, OP-6). *Survives, strengthened in §5 F8.*
- **BT-4 — rendezvous rides public, massively-shared infrastructure.** The expansion
  rendezvous is a read from infrastructure that exists for non-ScrambNet reasons (a
  global DHT (s)); the lookup is one ordinary operation among millions (I-4). *Surviving
  strength: dissolves the ScrambNet-specific single point, NOT the substrate's own join
  single point (§5 F3).*
- **BT-5 — the rendezvous key is per-seed secret.** `K_r = KDF(S, epoch, "rz")`, from
  the secret seed, so a censor who knows the whole scheme cannot compute `K_r` without
  `S`. *Surviving strength: the key is secret, but one reader per key per epoch is an
  access-pattern fingerprint (§5 F2).*
- **BT-6 — the rendezvous returns a probe-resistant endpoint.** The stored value is
  encrypted under the seed key and resolves to a CT-10-conforming endpoint that serves
  a real website to any prober and reveals the covert service only on proof of the seed
  secret. *Surviving strength: inherits the §11 / CT-10b operator residuals (§5 F9).*
- **BT-7 — re-seed from inside.** `K_r` rotates per epoch; the next epoch's rendezvous
  material is fetched over the overlay via gossip once the client holds one honest
  peer, so the out-of-band seed is used once. *Surviving strength: conditional on
  surviving one epoch boundary with an honest peer reached — which A can deny (§5 F2).*
- **BT-8 — first contact yields one quarantined provisional peer.** Treated as a single
  unverified source class capped at fraction `f` (1/2 (s)), quarantined until a second
  independent class is reached; until then the client runs the PS-8/PS-9 small-network
  fallback. *Surviving strength: the quarantine and fallback survive; the eclipse-bound
  claim does not at first contact (§5 F5).*
- **BT-9 — the economic bet is declared defeasible.** "A cannot block the public DHT
  without high collateral" is the same bet CT-13/CT-14 declares defeasible; an A that
  pays collateral, whitelists (CT-7b), or shuts down (CT-18a) defeats it. *Survives,
  sharpened in §5 F3: A blocks the DHT's bootstrap hosts, not only "the national DHT."*
- **BT-10 — unobservability is bounded to A/B; C is conceded.** First contact is made
  indistinguishable from ordinary public-infrastructure use for a local/national
  observer, but not for a global passive observer. *Surviving strength: C is conceded
  at GREATER salience than steady-state traffic (§5 F6).*
- **BT-11 — bootstrap bytes obey I-4.** Every observable byte is fixed-size and uniform,
  with no bootstrap-specific wire signature. *Survives — but it is about bytes, not flow
  shape (§5 F7).*
- **BT-12 — degrade to a fresh out-of-band seed, never a hardcoded point.** When the
  rendezvous is blocked and no honest peer is held, the client obtains a fresh seed over
  the out-of-band channel — never a hardcoded address, default broker, or fixed domain.
  *Survives, and is in fact the true base case the whole construction reduces to.*
- **BT-13 — bootstrap output carries no inherited trust.** Rendezvous-delivered peers
  and relays enter path selection as unverified (PS-10, PS-15 `c_j = 0`), subject to the
  PS-17 steering gate and PS-12 defences — exactly as suspect as a gossiped relay until
  the client's own probing corroborates them. *Survives as written.*

## 5. What the attack passes found — the findings that reshape the verdict

Each is stated with the invariant or prior result it turns on. The citations were
checked against the published spec.

- **F1 — BT-2's enforced rate budget cannot exist without an authority, and its
  social-graph half assumes the problem away.** A per-seed budget enforced across the
  population needs a party that counts redemptions and refuses the next — a central
  allocator, which I-3 forbids and which Part 2 §7 refuses by name ("the party that can
  publish the one trusted view is also the party that can be coerced, subpoenaed, or
  seized"). If the counter lives in the untrusted substrate, an A who captured the seed
  (whose only credential is possession of `S`) redeems the budget in parallel from
  sock-puppets. And "re-vouch along the social graph" presumes the user is *already* a
  node in the graph — but OP-7 is bootstrap with **zero** contacts, so there is no edge
  to re-vouch along. The anti-sybil wall (GR-20, "edges cannot be minted") is the same
  wall that keeps the honest graph-less user out. **The enforced meter is cut; the
  social-graph framing applies only after first admission.**
- **F2 — "A is beaten" rests on three assumptions that all fail, so A is NOT beaten.**
  (i) If A's enumeration cycle is shorter than one epoch, BT-7's re-seed-from-inside
  never fires and "one seed" collapses into "a fresh out-of-band seed every epoch." (ii)
  The rate-meter does not bound A without an authority (F1). (iii) BT-5's per-seed DHT
  key is a population-level access-pattern fingerprint — one reader per key per epoch is
  the same shape as the Part 4 §11 "selection distribution is itself the fingerprint"
  residual, one layer down, and A aggregates DHT lookups nationally. Any one failing
  means A wins. **A is reduced to the first-contact-eclipse residual (Part 2 §7, OP-2) —
  "detect, make permanent eclipse costly, do not prevent" — not beaten.**
- **F3 — two smuggled single points (I-3).** The public substrate's **own** join uses
  hardcoded well-known nodes (the Mainline DHT's `router.bittorrent.com` class); a new
  client with an empty routing table cannot do a single lookup without first contacting
  a hardcoded host, so a censor blocks a handful of IPs and every fresh-table client is
  dead *before* the rendezvous runs. **The substrate removes the ScrambNet-specific
  single point, not its own.** Separately, "rendezvous" already names a different Part 6
  primitive (RZ-n, deposit between parties who already share a contact card; RZ-1, "a
  recipient MUST NOT be discoverable through gossip") — the bootstrap primitive here is
  its opposite (a stranger discovering an endpoint), so the term must not be reused, and
  the primitive needs its own full derivation/format spec before it is anything but a
  sketch (I-1).
- **F4 — a secret capability is not distributable over a public mirror.** BT-1's
  security needs `S` secret, but a secret handed out by a mirror the censor can also
  download is not secret. So BT-1 is sound only over **replay-proof** channels
  (person-to-person, sealed private QR), and silently excludes the mirror/site channels
  the accepted seed model allowed. It also contradicts GR-10, which says the out-of-band
  line carries "one record plus one transport hint" — an address. The reconciliation:
  the public-mirror seed is the **address-bearing GR-10 floor** (blockable, enumerable);
  the private-channel secret-`S` is a **ceiling** that is not available over a mirror.
  The difference must be surfaced to the user, not hidden.
- **F5 — the eclipse bound does not hold at first contact.** GR-19's bound (full eclipse
  needs `a ≥ ⌈1/f⌉` independent classes) is derived for a client mixing across `m ≥ 3`
  independent source classes, and GR-19a says it collapses when one party owns more than
  one class, "and the overlay cannot tell 'two classes' from 'one party wearing' both."
  At first contact `m = 1` — the single provisional peer — so the bound BT-8 cited as
  protection does not apply in the regime BT-8 is about. The quarantine (`c_j = 0`) and
  the PS-8/PS-9 fallback survive; the eclipse-**bound** claim is downgraded to a
  residual declaration (the un-curvable first-contact eclipse, Part 2 §7).
- **F6 — C is conceded at *greater* salience than steady-state traffic.** Bootstrap is a
  one-time, first-ever event — the birth of a client's participation is a uniquely
  valuable correlation anchor — and BT-5 hands a global passive observer a per-client
  lookup to anchor on. So "no worse than fast mode" understates it: C learns *more* from
  the bootstrap flow than from ongoing traffic. Claiming equality would be the
  camouflage-grade overclaim CT-15a forbids.
- **F7 — B is not beaten; the choreography is a flow shape.** Each packet is I-4-uniform
  (BT-11), but the sequence lookup → fetch-blob → probe-endpoint → first-gossip is a
  fixed flow *shape*, and uniform bytes do not hide flow shape (CT-6, CT-12, and the
  §11 first residual: "crowd membership is a handshake property, never a flow
  property"). A DPI-only censor can key on the bootstrap choreography without probing.
  By CT-1 ("an undeclared capability is treated as conceded"), B's choreography
  classifier is conceded. B is cost-raised, not beaten.
- **F8 — the introducer-edge exposure has a tradeoff with no free point.** A
  per-recipient seed exposes exactly one edge on capture (good for the network, bad for
  that one human introducer — the BL-18a non-rotatable identity at the social layer); a
  per-cohort seed improves A's enumeration economics but exposes a whole cohort's
  introducer on one capture. Declared, not solved — the OP-6/OP-2 shape recurring at
  bootstrap.
- **F9 — BT-6 inherits the §11 / CT-10b operator residuals unchanged.** The
  probe-answering real endpoint shares one address, certificate, and endpoint between a
  public site and the covert channel, so covert-load congestion turns the public site
  into a timing oracle on the operator, and hosting real content carries an abuse /
  takedown exposure that the "carries packets, not opinions" posture (threat model,
  OPERATORS.md) does not cover. Inherited at bootstrap, declared here.

## 6. The honest verdict

This construction **does not solve OP-7, and it must not pretend to.** It does one
narrow, defensible thing: it *reduces* OP-7 from "how does a client contact a network
it knows nothing about" to the two residuals it cannot remove, and it turns the single
out-of-band seed the problem already requires into expansion without a
ScrambNet-specific single point in the common case. The scheme is public; only the seed
is secret (I-1); every byte is uniform (I-4); content never rides bootstrap (I-2).

What is unconditional: **the I-2 content floor never rode the bootstrap and is
untouched (CT-16).** That is the only unconditional win.

What is conceded, each by name — the correction the attack passes forced, against the
first draft's "A and B beaten, C conceded":

- **A is not beaten.** It is reduced to the first-contact-eclipse residual (Part 2 §7,
  OP-2): detect and make permanent eclipse costly, do not prevent. The three
  assumptions that "A beaten" rested on — epoch shorter than A's enumeration latency, a
  rate-meter without an authority, a DHT access pattern that does not fingerprint — all
  fail (§5 F1, F2), and if any fails A wins.
- **B is not beaten.** The bootstrap choreography is a flow-shape sequence a DPI censor
  can classify (§5 F7). B is cost-raised.
- **C is conceded, at greater salience than steady-state traffic** (§5 F6).
- **Two single points survive one layer down** (§5 F3): the public substrate's own join,
  and the social graph a zero-contact user is not yet in. Both reduce the zero-contact
  *core* back to the out-of-band human seed.

The minimal irreducible residual, reduced to a named open problem: **one secret must
cross an out-of-band channel once, and the flow that uses it is both correlatable by a
global passive observer and, at the very first contact, potentially eclipsed with no
honest vantage to detect it.** The first half is accepted and genuinely irreducible;
the second half is OP-2 (first-contact eclipse) and OP-7 (admitting a graph-less user),
both already declared open. **OP-7 remains open.** The true base case of the whole
construction is BT-12 — *ask a human for a fresh seed* — which is where the problem
honestly bottoms out. No victory is claimed.

## 7. What survives, for a future Part

If a future contributor builds a bootstrap Part, these are the pieces the attack passes
left standing as written: **BT-11** (bootstrap bytes obey I-4), **BT-13** (bootstrap
output carries no inherited trust, gated by PS-12/PS-17), and **BT-12** (degrade to a
fresh out-of-band seed, never a hardcoded point — the honest base case). Everything else
survives only with a weakened claim and a declared residual, as §5 records. The one
requirement that must be rebuilt rather than weakened is **BT-2**: the enforced rate
budget is cut (I-3), and its social-graph half must openly concede it does not address
the zero-contact first admission. This document is the record of why — so the rebuild
starts from the wall, not from the first draft.
