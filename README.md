# ScrambNet

*An anonymity network that asks for no acts of faith — not in the secrecy of its algorithms, not in their computational strength, not in any central party.*

**[English](README.md)** · [Italiano](README.it.md) · [Español](README.es.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [中文](README.zh-CN.md)

**Status: pre-specification.** No code yet, by design: threat model first, then the wire specification, then code. This repository is the meeting point for people who want to build it.

## Three refusals

Most anonymity networks stand on three legs of trust. ScrambNet is designed to remove all three:

1. **No secrecy of design.** Kerckhoffs's principle, taken literally: public RFC-style specification, open source, reproducible builds. The adversary may read every line; security lives in user keys and in the shape of the network.
2. **No reliance on computational hardness.** "Breaking this would take billions of years" is a promise about the universe's laziness, and such promises have a history of expiring (DES, RC4, SHA-1 — and quantum computers are on the horizon). The load-bearing wall must not expire.
3. **No single point to seize.** No directory authorities, no indispensable server, no update key held by one party. The kill switch is not forbidden; it is nonexistent.

## The core idea: strength from dispersal

Every message is split with Shamir secret sharing into `n` shares such that any `k` reconstruct it and `k−1` are **mathematically indistinguishable from noise** — not hard to decrypt: empty. The shares travel over disjoint paths: different guards, different jurisdictions, when needed different transports (one share inside an ordinary TLS flow, one inside what looks like a video call, one over local mesh).

```mermaid
flowchart LR
    M["Message"] --> S{{"scramble<br/>n=4 · k=3"}}
    S -- "s1" --> R1(("relay")) --> D["Recipient<br/>any 3 shares suffice"]
    S -- "s2" --> R2(("relay")) --> D
    S -- "s3" --> R3(("relay")) --> D
    S -- "s4" --> R4(("relay")) --> D
```

Reading the traffic stops being a cryptanalysis problem and becomes a problem of physical occupation: the adversary must hold `k` points of the network at the same instant. Onion encryption remains, demoted to a second belt — if it ever falls, the network does not become readable; it becomes less convenient.

The cost is declared up front: `n` shares cost `n×` the bandwidth. That is the trade this paradigm proposes — efficiency in exchange for security without assumptions.

## Architecture at a glance

| Layer | Name | What it does |
|---|---|---|
| L0 | Identity | Keypairs generated on-device. No registration, no phone number, no e-mail. An identity nobody issues is an identity nobody can revoke. |
| L1 | Discovery | No directory authorities. Gossip of self-signed relay lists; each client holds a verifiable sample (cf. Walking Onions). New users enter along the social graph (cf. Tor's Lox). |
| L2 | Routing | Per-share onion circuits: 3 hops, fixed-size Sphinx packets, long-lived guards. Two gears: fast (browsing latency) and paranoid (mixnet with delays and cover traffic). |
| L3 | Transport | Chameleon wrappers: the traffic imitates ordinary TLS (uTLS, ECH) or WebRTC calls. Blocking it must cost the censor more than it earns. |
| L4 | Blackout | When the internet is switched off: local mesh (Wi-Fi Direct, Bluetooth), store-and-forward. The network degrades; it does not die. |

Full details: [docs/architecture.md](docs/architecture.md) · Honest limits: [docs/threat-model.md](docs/threat-model.md)

## What it does not promise

A global passive adversary that watches all traffic at once defeats the fast mode — the same limit Tor has declared since its first design paper. Only the paranoid (mixnet) mode addresses it. A network that promises total protection is lying, and the people who run real risks deserve to know exactly where the umbrella ends.

## Almost nothing to invent

Shamir (1979), Rabin's Information Dispersal (1989), Chaum's DC-nets (1988), Sphinx (2009), Tor's Snowflake and Lox, the Noise Protocol Framework, Briar and Reticulum for the blackout layer, Walking Onions for sampled discovery. The real work is composition and discipline: if any detail of the design must stay secret for the system to work, that detail is a defect.

## Roadmap

1. **Threat model** — under discussion now, in the issues. Attack it.
2. **Wire specification** — the share packet, the gossip record, the handshake. RFC-style, public.
3. **Reference client** — one small, boring client. Mobile-first: anonymity that only runs on a new laptop is not for the people who need it most.

## Contributing

Pseudonymous contributions are welcome and expected — see [CONTRIBUTING.md](CONTRIBUTING.md). Discussion happens in the issues of this repository for now. Translations of the documentation are a valued first contribution.

One rule above all: **this network carries packets, not opinions.** It protects dissidents and their opponents with the same mathematics. Political adversaries are not enemies, and an infrastructure is credible only if it cannot choose sides.

## License

Specification and documentation: [CC0 1.0](LICENSE) (public domain). Future code will choose its license by contributor consensus.
