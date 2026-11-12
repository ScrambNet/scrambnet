# ScrambNet Specification — Part 5: Blackout and Mixed-Mesh Link Diversity

**Status: DRAFT, and a declared research risk.** This is the largest unwritten
design in the project, and this part returns — as the roadmap permits — a
*partial* result: a solid mixed-network model and one genuinely load-bearing
idea (independent-gateway dispersal, as an *availability* property), wrapped
around residuals it names at full strength and does not claim to close. It
commits **no concrete mesh stack** and makes **no anonymity claim for the radio
layer**; it is a posture-and-model part, exactly as Part 4 is. Strawman values
are marked `(s)`.

Read §3 (the realism assessment) first — it is the spine, and it says the much
larger thing this part refuses to claim. The one load-bearing positive claim is
narrow: *dispersal across independent gateways extends I-3 to the physical
neighbourhood exit as an availability property, and nothing in the mesh is
permitted to move the I-2 content floor* (BL-16) — the mesh is as independent of
the floor as Part 4 keeps the transport (CT-16). This part is the L4 rung that
Part 4's CT-18a hands off to, and it stays consistent with that concession
(BL-17): when there is no neighbour, nothing is delivered.

## 1. The mixed-network model and the roles

- **BL-1 (the mesh is a layer, not a mode). [normative]** A conforming node MUST
  treat local radio links and internet links as link types coexisting *at all
  times*, not as a "blackout mode" entered on infrastructure loss. Losing the
  uplink MUST be a change of *route* (one more hop to a gateway), never a change
  of protocol, identity, or security posture. A design with a distinct "mesh
  mode" the user toggles is non-conforming to this framing (OP-6).
- **BL-2 (roles, by hardware reality). [normative]** A node MUST self-classify,
  from its actual radio capability, as exactly one of: **leaf** (a phone: STA+AP
  or Wi-Fi Aware concurrency, battery-bound, no root), **backbone** (a dual-radio
  PC/SBC running true 802.11s, continuous store-and-forward), or **gateway** (a
  backbone or leaf currently holding an uplink and announcing it). Roles are
  capability-derived and time-varying — a gateway that loses its uplink becomes
  backbone or leaf — never a fixed tier.
- **BL-3 (opt-in is a precondition of any radio link). [normative]** A node MUST
  NOT originate, relay, or gateway any traffic over a local radio link without a
  prior, explicit, informed opt-in *specific to mesh participation* and distinct
  from any relay opt-in, because mesh visibility is physical (BL-18) and carries a
  radio-layer identity the overlay cannot rotate (BL-18a). Silence, or inheriting
  the relay opt-in, is non-conforming.
- **BL-4 (honest battery and storage budget). [normative]** A leaf node MUST
  surface, before opt-in, the battery and storage cost it will actually incur
  (strawman: a bounded store-and-forward quota and a duty-cycled radio schedule),
  and MUST NOT promise continuous backbone-grade availability it cannot sustain on
  battery. The concrete budget is OP-6 open and MUST be declared, not guessed
  (BL-20).

## 2. Independent-gateway dispersal, addressing, carriage, and mixing

### 2.1 Independent-gateway dispersal (the load-bearing idea, as availability)

- **BL-5 (shares SHOULD leave through independent gateways). [normative]** When a
  message's `n` shares (SP-2) traverse the local mesh to an uplink, a conforming
  client SHOULD route them so they leave through *different* gateways, extending
  I-3 (no single point) to the physical neighbourhood exit. One gateway carrying
  `k` of the `n` shares is a single point and MUST be avoided where ≥2
  independent-*estimated* gateways (BL-6) are reachable. In a deep blackout the
  independence estimate may be empty (BL-6); BL-5 then degrades to BL-7 **by
  default**, not as an edge case. The benefit claimed here is **availability**, not
  unobservability (§3): no single gateway's failure, blockage, or sybil-capture
  kills delivery — this is the CT-15 verdict for transports, in mesh space.
- **BL-6 (what "independent" can mean at the radio layer — stated, not solved).
  [normative, residual-declaring]** A conforming client MUST NOT treat gateways as
  independent on *self-declaration* (GR-3, in radio space). "Independent" can be
  estimated only from *observable, non-self-declared* signals — distinct uplink
  ASes *where an AS map (Part 8) is reachable*, distinct radio next-hops, distinct
  physical direction — each of which is weak, spoofable, or **unavailable inside a
  blackout** (the AS map, the strongest signal, is often the first thing gone).
  The honest meaning of "independent gateway" is therefore a **bounded-trust
  estimate**, not a verified fact (§4b); a client MUST present it as such and MUST
  NOT claim verified gateway independence. See BL-21 — this is the recurring
  independence problem in radio space.
- **BL-7 (too few — or zero — independent gateways degrades, never fails open).
  [normative]** Where fewer than two independent-estimated gateways are reachable,
  a client MUST NOT silently push `k` shares through one as if dispersal held; it
  MUST hold shares for a later independent exit (bounded by the BL-12 TTL), spread
  them over time, or surface that the physical exit is a single point for this
  message (BL-19). The floor (I-2) is unaffected either way (BL-16).

### 2.2 Addressing without global reachability

- **BL-8 (names survive; global routes do not). [normative]** The relay/recipient
  Ed25519 `id` (Part 2) and the `box_id`/rendezvous of Part 6 MUST remain the
  stable names inside a blackout; what breaks is global *reachability*, not naming.
  A node MUST NOT depend on a reachable DHT or any global route for next-hop
  selection on the mesh.
- **BL-9 (next-hop without a DHT — the menu and its costs).** Absent a global
  route, a mesh next-hop is chosen by a bounded-cost local method: epidemic
  flooding toward any uplink (cheap, no destination knowledge, high radio cost); a
  reachability *gradient* where neighbours advertise reachability *toward a
  gateway* — never toward the named recipient, which would be a selector
  (I-4/SP-7); or physical carry (store-and-forward until a gateway comes in range).
  This clause names the menu; the choice is a strawman (BL-20), and every option
  MUST preserve SP-7 (no cross-path linkability on the bytes) and I-4 (BL-15).
- **BL-10 (delivery still runs through Part 6 drops, never to a named device).
  [normative]** The mesh's job ends at the *uplink*: once shares reach the
  internet they re-enter the overlay and are delivered to dispersed dead drops
  (Part 6) exactly as before. The mesh MUST NOT attempt to deliver to a named
  recipient *device* directly — that would make delivery target a person,
  violating the Part 6 contract (RZ-1). The genuinely-all-local case (sender, drop
  and recipient all in-mesh, no uplink) is served by the recipient's **drop** also
  being mesh-reachable — deposit and poll both run over the mesh *to a drop*, never
  to the recipient device — which is the open item Part 6 §9 lists as "polling over
  the mesh during blackout (OP-6)." Routing to a named recipient device stays
  forbidden as a selector.

### 2.3 Store-and-forward and the framing verdict

- **BL-11 (Sphinx validity, not bytes, is the constraint on long carry).
  [normative, residual-declaring]** The 2048-byte Sphinx packet (SP-3) is
  self-contained in *bytes* but not in *validity*: its hop security binds to a
  relay's ≤7-day `onion` epoch (CH-5) and to the per-epoch replay cache (SP-5,
  SP-7b). A packet carried hours-to-days across intermittent links MAY outlive the
  epoch its first hop assumed, or arrive after replay state has rotated or been
  lost across restarts. A conforming design MUST state this and MUST NOT assume a
  Sphinx packet is indefinitely carriable unchanged.
- **BL-12 (the verdict: blackout needs its own store-and-forward envelope).
  [normative]** Because of BL-11, and because store-and-forward needs fields the
  fixed 2048-byte packet has no room for (a bounded time-to-live, fragmentation and
  reassembly for intermittent links, per-hop custody signalling), the verdict for
  this draft is that **blackout carriage needs its own outer framing** — a DTN-style
  bundle (prior art: RFC 4838/5050) that *wraps* the unchanged inner Sphinx packet,
  is itself fixed-length-padded, and whose metadata is AEAD-protected, never
  cleartext. The inner packet is untouched; the envelope is new and lives only on
  blackout links. This is a strawman verdict (BL-20), overturned only by an argument
  that closes BL-11, which this draft does not have.
- **BL-13 (the envelope must not become a selector — and inherits CT-6a's nesting
  residual). [normative, residual-declaring]** The envelope's TTL, fragment index,
  and custody fields are exactly the cleartext metadata I-4 forbids; they MUST live
  inside an AEAD-protected, fixed-size, uniform-looking frame (SP-4 discipline), and
  MUST NOT let a radio observer link two fragments of one message, or two shares of
  one message, any better than SP-7 already allows on the overlay. **Honest
  residual, inherited from Part 4:** wrapping an I-4-uniform inner packet inside an
  outer bundle re-creates the **CT-6a nested-structure surface** in radio space — a
  fixed-size outer frame whose size/timing/fragmentation can betray that it carries
  a *second* fixed unit, and per-layer uniformity does **not** make the nesting
  undetectable to an RF observer. This is a declared residual, not closed by the
  framing. It is survivable only in the sense everything here is: the blackout RF
  adversary is *local*, so nesting detection costs *observability-of-participation*
  — which BL-18 already concedes is lost — and does **not** touch the I-2 content
  floor.

### 2.4 Radio-layer mixing vs the sybil gateway

- **BL-14 (the sybil gateway is a physical eclipse; the answer is partial).
  [normative, residual-declaring]** A node announcing "I have uplink" attracts the
  neighbourhood's traffic, and a sybil gateway (or coalition) is a *physical
  eclipse* — the radio-layer instance of the Part 2 eclipse residual (OP-2). The
  partial answer is (i) radio-layer source mixing (BL-15) so a gateway cannot
  trivially attribute a share to its originating neighbour *at the frame layer*,
  composed with (ii) independent-gateway dispersal (BL-5) so no single gateway sees
  `k`. A conforming description MUST declare this answer **partial**: it raises the
  sybil's cost, it does not remove the eclipse, and it reduces to OP-1/OP-2
  recurring at the radio layer (BL-6, BL-21).
- **BL-15 (radio-layer source mixing is an availability/anti-eclipse measure, not
  origin-hiding). [normative]** Traffic on a local radio link MUST satisfy I-4 to a
  radio observer on the bytes (fixed-size uniform frames, BL-13) and SHOULD apply
  source mixing so the immediate frame-level sender of a share is not, by the frame,
  marked as its originator. This is **not** the GR-8 directory-sampling defense
  (GR-8 mixes a client's *stored sample* across source classes against map eclipse
  — a different mechanism against a different adversary) and MUST NOT borrow its
  name or its assurances. And it MUST NOT be presented as hiding the *physical*
  originator: a local adversary with direction-finding knows the physical emitter
  of a transmission regardless of frame contents (BL-18), so radio source-mixing
  buys *anti-eclipse cost against a sybil gateway*, never origin anonymity — the
  same linkage-vs-availability discipline CT-15a enforces for transports.

## 3. The honest realism assessment (the spine)

*(Written in the §residual voice of Parts 4, 8 and 11. This is the part, not an
appendix.)*

**What is genuinely designable, and real.** Three things. First, the *mixed-network
model* (BL-1): treating radio and internet as coexisting link types so that losing
an uplink is one more hop, not a different world, is clean, buildable, and
prior-art-backed (Briar, Reticulum, Yggdrasil/cjdns, Freifunk demonstrate pieces).
Second — the idea that earns the paradigm its keep — *independent-gateway dispersal*
(BL-5): the classic fatal weakness of every gateway mesh is that the gateway sees
everything, and ScrambNet answers it with the mechanism that defines the whole
network, spreading the `n` shares across gateways so no single physical exit sees
`k`. Third, the *invariant guard* (BL-16): keeping the I-2 floor wholly independent
of whether the mesh forms is not merely designable, it is forced, and it is the same
discipline Part 4 applies to transports. These three are solid.

**But the good idea is an *availability* idea, and must be sold as nothing more.**
Independent-gateway dispersal does little for *who* or *where* in the hot-blackout
threat model, because two residuals and one identity leak undercut it as an anonymity
mechanism: you cannot verify gateway independence in a blackout (BL-6), the emitter
is physically locatable (BL-18), and the radio layer carries an identity the overlay
cannot rotate (BL-18a). What dispersal *does* deliver, and delivers genuinely, is
availability: no single gateway's failure, blockage, or sybil-capture kills delivery,
and that holds even when every anonymity property has collapsed. This is exactly the
CT-15 verdict for multi-cover transports — availability yes, camouflage no — and the
part pins it there (BL-16). Sold as anonymity it would be an overclaim; sold as
availability it is a real, non-vacuous property.

**What is only partial.** The sybil-gateway / physical-eclipse problem (BL-14).
Radio-layer source mixing plus independent-gateway dispersal raises the cost of a
sybil eclipse; it does not remove it. A gateway coalition controlling `k` of the
reachable exits in a small neighbourhood mesh eclipses a sender exactly as a relay
coalition does on the overlay — OP-1 and OP-2 recurring in radio space, not a new
defence. "Partial" is the correct word.

**What is not solved — declared at full strength, three residuals.**

*First, gateway-independence verification (BL-6, BL-21).* You cannot verify from
anything a gateway self-declares that two gateways are independent, and inside a
blackout it is worse than on the overlay: the AS map (Part 8) that would let a client
*infer* independence from non-self-declared data is itself often unreachable — the one
tool gone exactly when it is needed, so the estimate can be near-empty in a deep
blackout (BL-5 degrades to BL-7 by default). This is not a Part 5 orphan: the threat
model names it as one face of the project's deepest recurring problem — verifying a
party's independence without trusting its self-declaration — shared with relays
(OP-1), release signers (OP-8), and dependency authors (OP-2/RB). The honest answer is
the same as there: a *bounded, declared residual* feeding a trust *estimate* with an
attached error (ID-12 style), not a cryptographic check. Part 5 does not get to be
where this is finally solved.

*Second, and irreducibly, physical locatability (BL-18).* A mesh node in a hot
blackout is a radio transmitter in a physical place, and **no overlay hides a radio
emitter from an adversary with a direction-finder.** This is categorically harder than
anything else in the specification, because every other threat in ScrambNet is a
*remote* adversary reasoning about bytes, and this is a *local* adversary with an
antenna — present precisely because they imposed the blackout. The whole cryptographic
edifice operates on *what the bytes reveal*; locatability is not about the bytes at
all, it is the electromagnetic fact of transmission. The part must not promise the
mesh preserves anonymity, and it does not.

*Third — the leak the overlay works hardest to prevent and the radio undoes (BL-18a).*
Locatability is *where you are*; identity is *who you are*, and the radio layer leaks
both. A Wi-Fi/802.11s radio emits persistent layer-2 identifiers the ScrambNet overlay
never touches — a MAC address (and 802.11s peering may require a stable one), Wi-Fi
Direct/Aware service and device IDs, probe-request fingerprints, and, against a capable
adversary, a *hardware RF fingerprint* (oscillator imperfections) that survives MAC
randomization entirely. So the entire overlay story — rotating `id`, per-epoch
`box_id`, per-relationship cards (RZ-2), SP-7 share unlinkability — sits *above* a
layer-2 pseudonym a local sniffer reads directly, and overlay rotation cannot rotate
it. And the mesh *topology itself* is an observable RF map: who relays to whom is
visible on the air even under uniform frames. This is the single residual the first
draft of this part omitted; it is named here at full strength because it is arguably
worse than locatability — you are not only findable while transmitting, you carry a
stable radio pseudonym every time you join.

**Can the mesh preserve the invariants it inherits? Partially, and here is the honest
ledger.** **I-2 (content floor):** preserved cleanly — the floor never rode the mesh
any more than it rode the transport (BL-16); this is the strongest and truest
statement the part makes. **I-4 (wire uniformity) and SP-7 (share unlinkability):**
preserved **at the byte layer only** — a uniform frame is still a detectable emission
(BL-18), and two shares of one message emitted from the *same physical device in the
same window* are correlated by direction-finding and timing (the radio re-links what
the overlay unlinks); the part MUST NOT claim inherited byte-unlinkability survives to
the RF layer. **I-3 (no single point):** *extended*, as a best-effort availability
property, through independent-gateway dispersal (BL-5) — but only to the degree BL-6's
estimate is trustworthy, which is the unsolved residual. So: I-2 preserved, I-4/SP-7
preserved-on-the-bytes-only, I-3 extended-but-estimated. That is the ledger, and it is
anti-triumphal on purpose.

**Consistency with CT-18a.** Part 4 conceded that at a total shutdown with no mesh
neighbour, delivery is zero and the floor is intact-and-useless. Part 5 is the rung
*below* that concession — what you do *when there is* a neighbour — and it does not
walk it back. It extends reachability one layer lower; it does not make delivery
guaranteed (BL-17). The honest claim is not "communication always gets through on the
mesh" — it is: *when a mesh neighbour and a gateway exist, a message can cross the city
at the speed of a bus; when none exists, the secret stays home, undelivered and
unexposed; and in either case, transmitting on the mesh is a physically locatable,
radio-identifiable act the overlay cannot hide.*

This is an XL / research-risk item, and it returns, as the roadmap permits, a *partial*
result: a solid mixed-network model and a genuine availability idea, around residuals
(gateway-independence, physical locatability, radio identity) named at full strength
and not claimed closed.

## 4. The two reasoned verdicts

**(a) Does the 2048-byte Sphinx packet survive hours-long store-and-forward, or does
blackout need its own framing? → It needs its own framing (BL-11, BL-12).** The packet
is fine in *bytes* but fails in *validity and function* on three independent counts:
(1) its hop security binds to a ≤7-day `onion` epoch (CH-5), which a days-long carry
can outlive, arriving at a rotated, zeroized key; (2) SP-5/SP-7b require per-epoch
replay state surviving restarts, and intermittent radio nodes lose power and caches
exactly across the hours-long horizon; (3) the fixed 2048-byte layout (SP-3) has no
spare field for the TTL, fragmentation, and custody signalling intermittent links need,
and may not grow one in cleartext (I-4). The clean resolution is a DTN-style outer
bundle wrapping the unchanged inner packet (BL-12/BL-13), with the declared CT-6a
nesting residual. This is a strawman verdict, overturned only by closing BL-11.

**(b) Can gateway independence be verified at the radio layer? → No; it is a declared
residual feeding a bounded-trust estimate (BL-6, BL-21).** "Independent" would have to
be established without trusting what the gateway says (GR-3, in radio space), and every
available signal is weak or gone: distinct uplink ASes need the Part 8 map, *unreachable
inside the very blackout where independence matters most*; distinct physical direction
is spoofable and coarse; distinct radio next-hop proves topology, not exit independence.
There is no cryptographic check that two gateways have independent uplinks — the same
wall OP-1 hits for relay disjointness and OP-8 for signer jurisdiction. So the honest
architecture is identical to the AS-map one (ID-12): do not claim verification, produce
a bounded-trust estimate from non-self-declared observables (which may be near-empty in
a deep blackout), attach the uncertainty, surface it (BL-19), and let dispersal (BL-5)
and over-time spreading (BL-7) bound — not remove — the harm when the estimate is wrong.

## 5. The invariant and honesty guards

- **BL-16 (the floor is independent of the mesh succeeding — the CT-16 analogue).
  [normative]** No confidentiality or dispersal guarantee (I-2) MUST depend on the
  mesh forming, on a gateway being reachable, on gateways being genuinely independent
  (BL-6), or on the blackout envelope being delivered. The mesh buys **reachability
  only** — the same word Part 4 uses for transports. A design in which losing the mesh
  loses the floor is non-conforming.
- **BL-17 (consistency with CT-18a: the bottom is still a bottom, three states).
  [normative]** Part 5 extends reachability one rung below CT-18a and MUST NOT be worded
  to contradict it. The three states, all explicit: (1) **no neighbour in range** →
  CT-18a, zero delivery, floor intact-and-useless; (2) **neighbour(s) in range but no
  gateway reachable anywhere in the mesh** → *also* zero delivery, reached via the mesh
  rather than directly — store-and-forward MAY hold shares against a *future* gateway
  within the BL-12 TTL, but this MUST NOT be presented as delivery; (3) **≥1 gateway
  reachable** → BL-5/BL-7 dispersal or degrade. State (2) collapses to the same outcome
  as (1); only the path differs. Part 5 makes delivery *possible* one layer lower,
  never *likely* and never *guaranteed*.
- **BL-18 (physical-locatability residual — stated at full strength, never solved).
  [normative, residual-declaring]** A mesh node transmitting in a hot blackout is a
  **physically locatable act**: a radio emitter in a place, at exactly the moment the
  local adversary who imposed the blackout is most aggressive and most willing to use
  direction-finding and IMSI-catcher-style tactics. **No overlay, mixing, dispersal, or
  framing in this specification hides this, and this part MUST NOT claim or imply that
  it does.** It is the reason mesh participation MUST be an explicit, informed,
  per-context opt-in (BL-3), and the reason the honest claim of this part is narrow (§3).
- **BL-18a (radio-layer identity residual — declared, not solved). [normative,
  residual-declaring]** Mesh participation exposes persistent layer-2 identifiers the
  overlay cannot rotate: a MAC address (802.11s peering may require a stable one), Wi-Fi
  Direct/Aware device and service IDs, probe-request fingerprints, and — against a
  capable adversary — a *hardware RF fingerprint* that survives MAC randomization. Each
  is a stable pseudonym for the *device*, independent of every overlay rotation
  (`id`, `box_id`, RZ-2 cards, SP-7). MAC randomization helps against the first class
  and nothing against RF fingerprinting. The mesh *topology* is likewise an observable
  RF map — who relays to whom is visible on the air even under uniform frames. The part
  MUST NOT imply overlay unlinkability extends to the radio emitter. This is the second
  face, alongside gateway-independence (BL-21), of the recurring identity/independence
  problem in radio space, declared and not closed.
- **BL-19 (surface the mesh posture honestly — the CT-19 analogue). [normative]** A
  conforming client MUST surface, on the existing honesty surface (PS-9/CT-19): that a
  radio link is in use; that this link is *physically locatable* (BL-18) **and
  radio-identifiable** (BL-18a); whether its gateway exit is single or
  plural-and-independent-*estimated* (BL-6/BL-7); and that mesh reachability — unlike
  the I-2 floor — carries **no** guarantee and may be zero. The message the UI states:
  *your content floor holds; on the mesh you can be located and your device recognized
  on the air where you are standing.*
- **BL-20 (concrete stack left open; claims bounded by what is run). [normative]** Part 5
  does **not** mandate a specific radio stack, routing method (BL-9), TTL/fragment sizing
  (BL-12), or battery budget (BL-4); these are strawmen and owner decisions. A client
  with an unspecified mesh stack MUST NOT claim any *quantitative* mesh-availability
  property; it MAY claim only the *qualitative* "a node that loses uplink can take one
  more hop to a neighbour gateway, and shares SHOULD leave through independent-estimated
  gateways," and only where it actually runs ≥2 independent-estimated gateways with
  `k < n`.
- **BL-21 (the recurring independence problem is declared, not closed). [normative,
  residual-declaring]** Verifying gateway independence without a reachable map and with
  location self-declared (BL-6) is the **same problem that appears for relays (OP-1),
  release signers (OP-8), and dependency authors (OP-2/RB)** — verifying a party's
  independence without trusting its self-declaration — now wearing its radio-layer mask
  inside a blackout, where the AS map (Part 8) is itself unreachable. Part 5 does **not**
  solve it; it reduces it to that declared recurring residual and feeds a bounded-trust
  estimate, exactly as the map feeds one with a declared error rate (ID-12).

## 6. Requirements introduced here

- **BL-1 / BL-2 / BL-3 / BL-4** — the mesh is a layer not a mode; capability-derived
  time-varying roles; explicit per-context opt-in before any radio link; an honest
  battery/storage budget.
- **BL-5 / BL-6 / BL-7** — independent-gateway dispersal as availability; "independent"
  is a bounded-trust estimate, never self-declared and near-empty in a deep blackout;
  too-few/zero gateways degrade, never fail open.
- **BL-8 / BL-9 / BL-10** — names survive, routes don't; next-hop without a DHT and its
  costs; delivery still runs through Part 6 drops, never to a named device, and the
  all-local case is served by a mesh-reachable drop.
- **BL-11 / BL-12 / BL-13** — Sphinx validity (not bytes) bounds long carry; blackout
  needs its own DTN-style envelope; the envelope must not be a selector and inherits
  CT-6a's nesting residual.
- **BL-14 / BL-15** — the sybil gateway is a physical eclipse, answered only partially;
  radio source mixing is an availability/anti-eclipse measure, **not** GR-8 and **not**
  origin-hiding.
- **BL-16 / BL-17** — the floor is independent of the mesh; consistency with CT-18a, the
  three delivery states, the bottom is still a bottom.
- **BL-18 / BL-18a / BL-19** — physical locatability and radio identity, both declared
  at full strength and never solved; honest mesh posture on PS-9.
- **BL-20 / BL-21** — concrete stack left open; the recurring independence problem
  declared, not closed.

BL-16 and BL-18/BL-18a are the load-bearing three: the floor does not depend on the
mesh, and the mesh cannot hide that you are transmitting or that your device is
recognizable on the air. The honest claim is narrow and availability-shaped: *the mesh
extends reachability one rung below a shutdown and keeps the content floor it inherits,
but it does not hide the emitter, the device, or the topology, and it does not
guarantee delivery.* Break this part by naming a mesh-layer anonymity the clauses
promise past BL-18/BL-18a, a place the I-2 floor is made to depend on the mesh
succeeding past BL-16, a way BL-17 is read as upgrading "possible" to "likely," or a
radio-layer leak BL-18/BL-18a miss. That is the invitation, in the house voice — and on
this part especially, the honest answer to "does it solve the blackout?" is "partly,
and here is exactly where it does not."
