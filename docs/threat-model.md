# ScrambNet — Threat Model

> A network that promises total protection is lying, and the people who run real risks
> deserve to know exactly where the umbrella ends. This document is the contract.

## Adversaries and outcomes

| Adversary | Capability | Network response | Outcome |
|---|---|---|---|
| Local observer (your ISP, an office Wi-Fi) | Watch your traffic | Sees an ordinary TLS flow to an ordinary address | **Protected** |
| National censor | Block IPs, match DPI fingerprints, enumerate bridges | Chameleon transports; bridges distributed along the social graph with Lox-style trust levels | **Protected** (an arms race, but a sustainable one) |
| Malicious relay on a path | Observe what crosses it | Sees one hop of one share; Sphinx packets are identical everywhere | **Protected** |
| Operator of guard *and* exit of one circuit | Correlate entry/exit timing | That circuit carries one share, not the message; guards are stable for months; paranoid mode adds mixing delays | **Mitigated** |
| `k`-path adversary (holds guard+exit on `k` of the `n` share paths simultaneously) | Full timing correlation plus share capture | Path selection enforces disjoint guards, ASes, jurisdictions, making simultaneous `k` positions an occupation problem | **Mitigated** — this is the designed residual risk; raise `n`, `k` to taste |
| Global passive adversary (sees all traffic everywhere) | Correlate everything | Fast mode: nothing. Paranoid mode: mixnet with delays and cover traffic | **Out of model (fast mode)** — declared, as Tor declares it |

## What the dispersal changes, precisely

Classical onion routing fails *catastrophically* on one bad draw: control guard and exit of
the single circuit and you get both linkage (who talks to whom) **and**, where the
destination's own encryption is absent or broken, content. Under dispersal:

- **Content** is unconditionally protected below `k` captured shares. No computational
  assumption is involved. This floor cannot be eroded by cryptanalysis or quantum progress.
- **Linkage** (metadata) on a single violated share path is still a real loss: the
  adversary learns that *some* flow ran between you and a destination's share collector.
  Dispersal narrows what one circuit betrays; it does not nullify it. Stable guards,
  AS-disjoint path selection, and paranoid-mode mixing are the mitigations.

## Assumptions

1. The underlying networks (ISPs, IXPs, cables, clouds) are hostile or compromised.
2. The design, code, and all documents are fully known to every adversary (Kerckhoffs).
3. Relays are run by strangers; a constant fraction is malicious and colluding.
4. Endpoints are honest: a compromised phone loses before the first packet leaves.
   Device security is out of scope, stated without pretense.
5. Users can obtain the client. Reproducible builds plus a public spec (anyone can
   reimplement from scratch) are the answer to binary poisoning and to the disappearance
   of any official distribution channel.

## Non-goals

- Protecting a user whose device is compromised.
- Hiding *that* a region uses circumvention tools in aggregate (fast mode).
- Content moderation at the network layer. The network carries packets, not opinions;
  it protects dissidents and their opponents with the same mathematics. An infrastructure
  is credible only if it cannot choose sides.

## Open problems

Marked for attack — each deserves its own issue:

1. **Disjointness enforcement.** How does a client *verify* that `n` paths do not share an
   AS, a jurisdiction, a data center — using only its gossip sample, against relays that
   can lie about location?
2. **Sybil and eclipse resistance** of gossip sampling without a central allocator.
   Walking Onions assumes an authority-signed snapshot; we removed the authority. What
   replaces its anti-sybil function — proof of long-term keys? social-graph weighting?
   bandwidth verification by randomized probing?
3. **Parameter economics.** Defaults for `n`, `k` per traffic class; when does Rabin IDA
   (cheaper, computational) replace Shamir (unconditional) for bulk data, and is that
   downgrade ever acceptable by default?
4. **Share-timing correlation.** `n` shares entering the network within milliseconds are
   themselves a fingerprint. Jitter, batching, decoy shares: what does each cost?
5. **Cover traffic economics** in paranoid mode on metered mobile connections.
6. **Blackout addressing.** Identity-based routing over mesh store-and-forward without a
   DHT reachable from inside the blackout.
7. **Bootstrap with zero contacts** for the social-graph bridge distribution.
8. **Update governance.** Multi-signature releases across jurisdictions: how many signers,
   how chosen, how replaced — without creating the committee that becomes the kill switch.
