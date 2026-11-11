# How ScrambNet compares

Honest positioning against the systems a reviewer will rightly name first.
This document states what ScrambNet does *differently*, and — more important —
what it does *worse*. If a cell below is wrong, open an issue: being wrong here
costs more than being wrong anywhere else in the repository.

## The one real difference

Every deployed anonymity system protects message **content** with a
computational assumption: break the cipher (today or with a future quantum
computer) and the content is readable. ScrambNet's content floor is
**information-theoretic**: below `k` captured shares there is no ciphertext to
break, because the content is not present in any `k−1` shares — a property of
Shamir secret sharing, not of any cipher's strength (invariant I-2). That is
the whole wager. Everything else here is prior art, composed.

This difference is **only about content**. For **linkage** (who talks to whom,
the metadata) ScrambNet is in the same hard fight as everyone else, and makes
no information-theoretic promise there in fast mode.

## Side by side

| | **ScrambNet** | **Tor** | **Nym / Loopix** | **Briar** |
|---|---|---|---|---|
| Primary use | Messaging (async, dead-drop) | Low-latency browsing | Messaging (mixnet) | Messaging, P2P |
| Content confidentiality | **Unconditional below `k` shares** | Computational (TLS + onion) | Computational | Computational |
| Linkage defense | Dispersed circuits + mix (paranoid) | Onion circuits | Poisson mixnet (strong) | Onion + contact graph |
| Directory / discovery | **None** — gossip + verifiable sample | ~9 directory authorities | Validators / nym-api | Introduction via contacts |
| Global passive adversary | Out of model (fast) / mix (paranoid) | Out of model | **In model** (mixnet) | Partial |
| Blackout / offline | Local mesh, store-and-forward | No | No | **Yes** (Bluetooth/Wi-Fi) |
| Incentive layer | None (volunteer) | Volunteer | **Token** | Volunteer |
| Maturity | **Pre-alpha spec + PoC** | Production, 20+ years | Production | Production |

## Where ScrambNet is behind, stated plainly

- **Maturity.** Tor, Nym and Briar are deployed, audited, and carry real
  traffic today. ScrambNet is a specification and a Python proof-of-concept.
  Nobody should route a real secret through it yet, and the repository says so.
- **Mixnet design.** Nym/Loopix have a rigorous, published Poisson-mix design
  with a global-passive-adversary model. ScrambNet's paranoid mode is a
  placeholder (OP-5) until someone does that work here too.
- **Linkage metadata.** The dead-drop retrieval pattern leaks polling cadence
  to a drop within an epoch (OP-9) — a cost Nym's continuous mixing pays down
  more thoroughly.
- **Bandwidth.** The unconditional floor costs `×n` bandwidth (×4 at the
  strawman). Tor costs ×1 for its weaker content guarantee. This is the price
  of the wager, not a bug, but it is a real price (OP-3).
- **Incentives.** Nym pays relays; ScrambNet asks volunteers, which historically
  caps growth.

## Why build it anyway

Because every other system's content guarantee has an expiry date written in
the assumptions of 2003–2017, and "harvest now, decrypt later" is a real
adversary strategy against dissidents whose messages must stay unreadable for
decades. A content floor that cannot be eroded by cryptanalytic or quantum
progress is worth a ×`n` bandwidth bill and the work of building the rest. If
that wager is wrong, the fastest way to find out is to attack it here.
