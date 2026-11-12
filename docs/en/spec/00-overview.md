# ScrambNet Specification — Part 0: Conventions and Structure

**Status: DRAFT.** Every number in this specification is a strawman to be attacked,
not a decision. Attack it through the issues; change it through PRs.

## How to read this specification

- The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, **MAY** are to be
  interpreted as described in RFC 2119.
- Requirements are numbered and stable: `SP-n` (share packet, Part 1), `CH-n`
  (circuit handshake, Part 1 §5), `GR-n`
  (gossip record, Part 2), `PS-n` (path selection, Part 3), `RZ-n` (rendezvous,
  Part 6), `SA-n` (security argument, Part 7), `ID-n` (inference dataset,
  Part 8), `RI-n` (reference-implementation requirements, Part 9), `RB-n`
  (reproducible build and supply chain, Part 10), `UG-n` (update governance,
  Part 11), `CT-n` (chameleon transports, Part 4), `BL-n` (blackout and
  mixed-mesh link diversity, Part 5). Issues and PRs reference requirements by
  number.
- `OP-n` references point to the open problems list in
  [threat-model.md](../threat-model.md#open-problems).
- A conforming implementation implements every MUST of every part it claims.

## Design invariants

These four invariants outrank everything else in the spec. A proposal that violates
one of them is rejected regardless of what it buys.

- **I-1 (Kerckhoffs).** The specification is complete: a hostile implementer with
  this document and no other knowledge MUST be able to build an interoperable,
  equally secure node. If a detail must stay secret for the system to work, the
  detail is a defect.
- **I-2 (Unconditional floor).** The confidentiality of message content against an
  adversary holding fewer than `k` shares MUST NOT depend on any computational
  assumption. Layers above the dispersal MAY be computational; the floor is not.
- **I-3 (No single point).** No protocol step may require a party, key, or address
  that cannot be replaced by an untrusted substitute. This includes discovery,
  updates, and bootstrap.
- **I-4 (Uniformity).** Everything observable on the wire by a party without the
  relevant keys MUST be indistinguishable from uniform random bytes of fixed
  length. No cleartext versions, flags, or lengths.

## Cryptographic suite

Suite identifiers are one byte, negotiated nowhere: the suite is fixed per network
epoch and carried implicitly by the packet version (I-4 forbids cleartext
negotiation). Suite `0x01` (strawman):

| Role | Primitive |
|---|---|
| Per-hop key agreement | Sphinx ephemeral–static X25519 (no separate handshake; Part 1 §5) |
| Key exchange | X25519 |
| AEAD | ChaCha20-Poly1305 |
| Hash / KDF / PRF | BLAKE2s / HKDF-BLAKE2s |
| Signatures (gossip records) | Ed25519 |
| Packet format | Sphinx (Danezis–Goldberg 2009) parameters, Part 1 |
| Dispersal | Shamir secret sharing over GF(2^8), per byte |

Rationale: fast without hardware acceleration (anonymity that only runs on a new
laptop is not for the people who need it most), nothing exotic, every primitive has
a decade of public attacks behind it. Post-quantum note: by I-2 the confidentiality
floor survives a quantum adversary already; a PQ handshake (suite `0x02`) is a
planned upgrade, not an emergency.

## Encoding conventions

- All integers are unsigned, network byte order (big-endian).
- Fixed sizes everywhere a field crosses the wire (I-4). Variable-length data
  exists only inside AEAD-protected payloads, length-prefixed with 2 bytes.
- Gossip records use canonical CBOR (RFC 8949 §4.2.1) — Part 2.

## Parts

1. [Part 1 — Share packet](01-share-packet.md): the fixed-size unit that carries
   one share of one message through one circuit.
2. [Part 2 — Gossip record](02-gossip-record.md): the self-signed relay descriptor
   and the rules for exchanging and sampling them.
3. [Part 3 — Circuit construction and path selection](03-path-selection.md):
   disjointness targets, inference without self-declaration, guards, and the
   small-network fallback (OP-1).
4. [Part 6 — Rendezvous and delivery](06-rendezvous.md): contact cards,
   dispersed dead drops, and retrieval by polling.
5. [Part 7 — The security argument for I-2](07-security-argument.md): the
   proof that any `k−1` shares are independent of the secret, the two
   conditions it rests on (coefficient randomness, key separation), and an
   honest statement of what is not proved.
6. [Part 8 — The inference dataset](08-inference-dataset.md): how a client
   obtains the IP-to-AS and coarse-jurisdiction map Part 3 infers from, with no
   authority — a reproducible content-addressed artifact, a permissionless
   transparency log, declared trust-on-first-use, and the error rate the map
   admits and feeds to the simulator (OP-1 distribution, roadmap 2.3).
7. [Part 9 — Reference-implementation requirements](09-reference-implementation.md):
   what a real node MUST do that the proof-of-concept toy omits — constant-time
   field and X25519 arithmetic, CSPRNG and fork-safety discipline, nonce and
   replay state across restarts and snapshot restores, a misuse-resistant
   fail-closed API, and memory zeroization — each `RI-n` tied to the threat and
   the invariant it protects, on the principle that an information-theoretic floor
   is only as unconditional as the code that computes it (roadmap 3.1).
8. [Part 10 — Reproducible build and supply chain](10-reproducible-build.md): how
   a party trusts a binary without trusting whoever built it — reproduction, not
   signature, as the arbiter — against pseudonymous contributors with no
   identity-bound keys; content-pinned toolchain and dependencies, a hermetic
   build, a stranger's rebuild-and-compare, and the honest residuals (a backdoor in
   faithfully-reproduced source, a reproducibly-miscompiling compiler, and the
   reduction to OP-2 for the user who cannot rebuild). Seam with item 4.1: same
   trust anchor, separate signer sets (roadmap 4.2).
9. [Part 11 — Update governance](11-update-governance.md): how a client comes to
   run a *newer* binary without trusting whoever released it — no authoritative
   signer set and no push of any kind (two owner-bound decisions). Permissionless
   log-append announcement, pull/gossip discovery, manual opt-in adoption bound to
   reproduction and freshness, a reproducible-downgrade defense, a permissionless
   forceless known-bad report (never an authoritative revocation), and
   self-verifying opt-in refuse-to-run. Carries its central residual openly: no
   push means no forced patch — a vulnerable or compromised client may never adopt
   the fix (`UG-n`, roadmap 4.1 / OP-8).
10. [Part 4 — Chameleon transports](04-chameleon-transports.md): the transport
   threat model and an honest realism assessment — the part most likely to rot.
   It makes no claim to win the censorship arms race; its one claim is that the
   I-2 content floor does not depend on the transport at all (`CT-16`): a
   transport buys *reachability*, which is allowed to fail down the L1→L4 ladder
   and, at a total shutdown with no mesh, to zero, without content below `k` ever
   being revealed. Covers the 2026 censor (JA4 fingerprinting, active probing,
   entropy/TLS-in-TLS flow detection, ECH's DNS-dependent reality, protocol
   whitelisting), the uTLS maintenance treadmill, and the verdict that multi-cover
   dispersal buys availability, not camouflage (`CT-n`, roadmap 5.1 / OP-7).
11. [Part 5 — Blackout and mixed-mesh link diversity](05-blackout-mesh.md): the
   largest unwritten design, returned as an honest *partial* result. The mesh is
   a layer, not a mode: losing an uplink is one more hop to a neighbour gateway,
   and the `n` shares SHOULD leave through independent gateways, extending I-3 to
   the physical exit — as an *availability* property (`BL-16`), the mesh never
   moving the I-2 floor. Carries three residuals at full strength: gateway
   independence is unverifiable inside a blackout (`BL-6`), a mesh node is
   physically locatable (`BL-18`), and it exposes a radio-layer identity the
   overlay cannot rotate (`BL-18a`). Needs its own store-and-forward envelope
   (`BL-12`); consistent with Part 4's CT-18a — no neighbour, no delivery
   (`BL-n`, roadmap 5.2 / OP-6).
