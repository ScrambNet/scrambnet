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
  At or above `k` shares the adversary reassembles the ciphertext and meets the end-to-end
  AEAD — a computational belt, keyed from a pre-shared symmetric secret so that even this
  tier resists a future-quantum "harvest now, decrypt later" adversary (spec SP-1a). The
  claim is the floor's permanence, not the belt's unbreakability.
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

<a id="open-problems"></a>
## Open problems

Marked for attack. Each problem is discussed in **one** place: a single
[issue](https://github.com/ScrambNet/scrambnet/issues) per problem, with the
English text and all translations in the same thread. Read the problem in any
language here; discuss it there, in the one issue, so no discussion is split.

1. **Disjointness enforcement.** A first path-selection mechanism now exists in draft
   ([spec Part 3](spec/03-path-selection.md)) with an executable strawman in
   `poc/network_sim.py`; what remains open is the hard core: how does a client *verify*
   that `n` paths do not share an AS, a jurisdiction, a data center — using only its gossip
   sample and a trustlessly distributed inference dataset (I-3), against relays that can lie
   about everything except their signatures?
2. **Sybil and eclipse resistance** of gossip sampling without a central allocator.
   Walking Onions assumes an authority-signed snapshot; we removed the authority. What
   replaces its anti-sybil function — proof of long-term keys? social-graph weighting?
   bandwidth verification by randomized probing?
3. **Parameter economics.** Defaults for `n`, `k` per traffic class; when does Rabin IDA
   (cheaper, computational) replace Shamir (unconditional) for bulk data, and is that
   downgrade ever acceptable by default?
4. **Share-timing correlation.** Content unlinkability between shares (SP-7) is settled and
   implemented in the PoC; *timing* is not. `n` shares entering the network within
   milliseconds are themselves a fingerprint. Jitter, batching, decoy shares: what does each
   cost in latency, and what does it actually buy against an adversary watching several
   exits?
5. **Cover traffic economics** in paranoid mode on metered mobile connections.
6. **Blackout addressing.** Identity-based routing over mesh store-and-forward without a
   DHT reachable from inside the blackout.
7. **Bootstrap with zero contacts** for the social-graph bridge distribution.
8. **Update governance.** How a client comes to run a newer release without a kill switch.
   Addressed in draft by [spec Part 11](spec/11-update-governance.md) (`UG-1..UG-9`): the
   answer came out **minimalist** — no authoritative signer set and no push of any kind
   (reproducible builds + cross-published hashes + a freshness index; signatures only
   locate, never authorize). What stays open is the residual Part 11 §10 declares rather
   than solves: no push means **no forced patch**, so a vulnerable — or already
   compromised — client may never adopt the fix, and revocation of a reviewed-but-malicious
   release reduces to public review (`I-1`) and `OP-2`. The hard part was never "how many
   signers" but conceding that refusing both an authority and a push buys patch-latency as
   its price.
9. **Dead-drop metadata and economics.** A drop sees deposit times and polling cadence for
   a box within one epoch (spec Part 6). Polling distributions and decoy cost on metered
   connections, deletion semantics, deposit pricing against flooding, storage incentives:
   what does each defense cost, and what does each leak?
10. **Dependency-author honesty without self-declaration.** Reproducible builds
    ([spec Part 10](spec/10-reproducible-build.md)) prove a binary matches its public
    source, never that the source is honest (RB-12b): a backdoor in a pinned dependency is
    reproduced faithfully for every rebuilder and reproduction is blind to it (RB §10.1).
    You cannot verify a pseudonymous crate author is honest — or that two crates have
    *independent* authors — from anything they self-declare. This is the same problem that
    appears for **relays** (OP-1, path disjointness), **release signers** (OP-8,
    jurisdictional diversity), and **mesh gateways** (OP-6, physical independence): verifying
    a party's independence or honesty without trusting its self-declaration. The honest
    answer here, as there, may be a *bounded, declared residual* — public review (I-1),
    audit, and a minimized dependency surface that bounds the attack rather than a
    cryptographic check that removes it. It is the software-supply-chain face of the project's
    deepest recurring problem, not a new orphan.
