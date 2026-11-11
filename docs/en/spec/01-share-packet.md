# ScrambNet Specification — Part 1: Share Packet

**Status: DRAFT.** Strawman sizes are marked `(s)`. Attack them by requirement number.

## 1. Scope

The share packet is the only unit that crosses the overlay: it carries one share of
one message through one onion circuit. Everything in this part serves two goals:
the unconditional floor (I-2) and wire uniformity (I-4).

## 2. Layering

```
plaintext message
  └─ end-to-end AEAD (pre-shared pair key, SP-1a)  [computational]
       └─ Shamir split: n shares, threshold k      [unconditional floor]
            └─ per-share onion encryption, own circuit, Sphinx format
                 └─ chameleon transport (Part 4)
```

- **SP-1.** The sender MUST apply end-to-end encryption *before* dispersal, and
  dispersal MUST be applied to the end-to-end ciphertext. With fewer than `k`
  shares the adversary learns nothing about the ciphertext unconditionally
  (Shamir); with `k` or more shares it still faces the end-to-end AEAD. The
  unconditional floor and the computational belt compose; neither replaces the
  other. The belt is demonstrated end to end in `poc/e2e.py`
  (encrypt → split → reconstruct → decrypt, fail-closed on tamper).
- **SP-1a (content-key establishment, and the post-quantum consequence).**
  The end-to-end AEAD key MUST be derived from the **pre-shared symmetric pair
  secret** `kpair` carried by the contact card (Part 6, RZ-2), by a
  label-separated KDF: `content_key = HKDF-BLAKE2s(kpair, "e2e-content")`,
  distinct from the SP-7 tag key and the box-id key derived from the same
  `kpair`. There MUST be no asymmetric key agreement in the content path. This
  is a deliberate choice with a load-bearing consequence: a `≥k`,
  record-everything adversary with a future large-scale quantum computer still
  cannot read content, because there is no Diffie-Hellman transcript for Shor
  to break — only a symmetric secret the parties already share, and Grover
  costs the AEAD at most a halving of its key strength (hence a ≥256-bit
  derived key is RECOMMENDED where margin matters). "Harvest now, decrypt
  later" is therefore defeated at **both** tiers: below `k` by Shamir
  (unconditional), at or above `k` by a symmetric AEAD under a pre-shared key
  (no public-key assumption to harvest). The honest cost is the **bootstrap**:
  `kpair` must first reach the recipient over a prior confidential channel (the
  out-of-band contact-card exchange, Part 6). Any residual public-key or PQ-KEM
  assumption lives there, in the card exchange — not in the content path — and
  carrying a card exchange that is itself post-quantum is an orthogonal,
  layered choice, not a precondition for the floor. The AEAD suite is
  ChaCha20-Poly1305 (suite `0x01`); `msg_nonce` (SP-7) is the AEAD nonce, which
  binds the two layers and makes a reused nonce doubly fatal (SP-7 tag
  collision *and* AEAD confidentiality loss — see SP-7).
- **SP-2.** Default dispersal parameters for messaging: `n = 4`, `k = 3` (s).
  Bulk transfer profiles MAY use Rabin IDA instead of Shamir, and MUST be
  labeled as computational in the client UI, because IDA has no unconditional
  floor (OP-3).

## 3. Wire format

- **SP-3.** Every packet on every link MUST be exactly `P = 2048` bytes (s).
- **SP-4.** Every byte of the packet MUST be indistinguishable from uniform
  random to an observer without the relevant keys, at every hop (Sphinx
  property; I-4). In particular there is no cleartext version, suite, length,
  hop counter, or share index.

Layout (sizes strawman, 3-hop maximum):

| Field | Size (s) | Visible to |
|---|---|---|
| `alpha` — Sphinx group element (X25519) | 32 B | everyone (uniform) |
| `beta` — Sphinx routing info, 3 × 48 B, padded | 144 B | peeled per hop |
| `gamma` — per-hop MAC | 16 B | current hop |
| `delta` — payload, AEAD-wrapped per hop | 1856 B | exit → recipient leg |

- **SP-5.** Relays MUST maintain a replay cache of seen `gamma` values per key
  epoch and MUST drop replays silently (standard Sphinx replay defense).
- **SP-6.** Relays MUST emit packets in constant-size batches with
  implementation-defined jitter in fast mode, and MUST follow the mix strategy
  (stop-and-go or Poisson mix, TBD) in paranoid mode. The strategy choice is
  OP-5 territory and deliberately unresolved here.

## 4. Share payload (inside `delta`, end of the circuit)

Decrypted by the recipient only:

| Field | Size (s) | Notes |
|---|---|---|
| `tag` | 16 B | recipient-keyed PRF tag, see SP-7 |
| `index` | 1 B | share index `1..n` |
| `params` | 1 B | packed `k`, `n` (4 bits each) |
| `share` | 1792 B | Shamir share bytes |
| `pad` | rest | random |

- **SP-7 (no cross-path linkability).** Two shares of the same message MUST NOT
  carry any equal or correlatable value observable by anyone except the
  recipient. Share-set membership is signaled only by `tag`:
  `tag = PRF(K_r, msg_nonce ‖ index)` where `K_r` is a recipient-held key and
  `msg_nonce` is carried inside the end-to-end layer. An exit relay, or a
  coalition of exits, MUST NOT be able to tell whether two packets belong to
  the same message. This requirement is load-bearing: without it, dispersal
  degrades into an enumeration convenience for the adversary.
- **SP-7a (share integrity: accepted fail-closed residual).** The `tag` says
  *which* message a packet claims to belong to; it does **not** authenticate
  the `share` bytes or the `params` (`k,n`) byte. Shamir reconstruction has no
  integrity of its own, so a hostile drop or exit that flips bits in one share
  — or lies about `k,n` — yields a consistent-but-wrong plaintext candidate
  that Shamir cannot detect. This is **caught one layer up**: the end-to-end
  AEAD (SP-1a) fails its tag on any corrupted reconstruction and the recipient
  discards the message rather than acting on garbage (demonstrated in
  `poc/dispersal.py`, test `test_tampered_share_fails_closed`). The residual is
  therefore **not a confidentiality loss but a targeted denial of service**: a
  single malicious vantage point on one of the `n` share paths can make a
  specific message fail to reconstruct, at the cost of one flipped bit. The
  verdict for this draft is to **accept and document** that residual rather
  than add a per-share MAC, for two reasons: (1) a per-share authenticator
  would spend payload bytes and introduce a second key to manage without
  removing the DoS — a drop that can corrupt a share can equally *drop* it, and
  `n−k` such losses are already tolerated by design; (2) the AEAD already makes
  the failure safe (fail-closed), so the open question is availability, not
  secrecy. The honest mitigations are redundancy (`n−k` margin), path
  disjointness so no single vantage point sits on `k` of the `n` paths (OP-1),
  and retry over fresh paths. A future revision MAY add an optional per-share
  binding for availability-critical profiles; it is deliberately not mandated
  here. `k,n` is vector-locked (nibble order, Part 3 §3.2 vectors) so an
  implementation cannot *accidentally* disagree, only a malicious party can lie.
- **SP-7b (no equal tag across colluding drops, and nonce ownership).** The
  property that must hold: no two packets a coalition of drops can see carry an
  equal `tag` unless the sender reused a `(msg_nonce, index)` pair. *Argument:*
  `tag = PRF(K_r, msg_nonce ‖ index)` with `msg_nonce` a fixed 8 bytes and
  `index` a fixed 1 byte, so the PRF input is an unambiguous fixed-width
  encoding of `(msg_nonce, index)` — the map `(msg_nonce, index) ↦ input` is
  injective. A keyed BLAKE2s PRF gives equal outputs only on equal inputs
  (bar a ~`2^-128` collision), so equal tags imply an equal `(msg_nonce, index)`.
  The `n` shares of one message share one `msg_nonce` but use *distinct* indices
  `1..n`, hence distinct inputs, hence distinct tags: a coalition of drops
  cannot tell two shares of one message apart from two unrelated packets. Two
  *different* messages collide a tag only if they reuse a `msg_nonce`.
  Therefore **nonce ownership is a MUST**: a sender MUST NOT reuse a
  `msg_nonce` under one `kpair`. Reuse is doubly fatal — it collides SP-7 tags
  (making a share set linkable) *and*, because `msg_nonce` is the AEAD nonce
  (SP-1a), it destroys ChaCha20-Poly1305 confidentiality (a two-time pad, pinned
  by `test_nonce_reuse_is_detectable_catastrophe`). A strictly increasing
  per-`kpair` message counter satisfies this; the counter's high-water mark MUST
  survive restarts. At the storage layer, a drop MUST drop a redeposit of an
  already-stored `(box_id, slot)` (replay) and evicts oldest-first under the
  per-box cap (RZ-7), so a replayed deposit neither multiplies nor displaces
  honest mail beyond the declared cap.
- **SP-8.** A message that does not fill the share payload (`1792` bytes, less
  the 2-byte length prefix) MUST be padded with random bytes before splitting;
  a message that exceeds it is fragmented at a layer above this one
  (fragmentation design TBD, interacts with OP-4). Shamir's honest price: every
  share is as long as the secret, so an (n, k) dispersal transmits ×`n` the
  ciphertext volume (OP-3).
- **SP-9 (timing).** The sender MUST NOT emit the `n` shares as a simultaneous
  burst. Shares SHOULD be emitted with randomized per-share delay; the
  distribution and its cost on latency are OP-4 and unresolved. Clients MAY
  emit decoy shares (packets with random `tag`) at a configurable rate.

## 5. The circuit handshake (there is none — it is Sphinx)

The suite once named `Noise_XK_25519_ChaChaPoly_BLAKE2s` as a "circuit handshake"
that nothing specified, an I-1 defect: a hostile implementer could not build an
interoperable node, because there was no transcript to build. **The resolution is
to delete the line.** Sphinx already performs the per-hop key agreement a circuit
needs, so a separate Noise handshake is a vestige — most likely inherited from the
WireGuard "Noise handshakes" lineage without noticing Sphinx had already eaten the
job. This section records that decision and specifies, normatively, the handshake
that Sphinx *is*, so I-1 is met by specification, not by a second protocol.

**The decision, in one paragraph.** `alpha` (SP-3, 32 B, X25519) is a *per-packet
client ephemeral*; each relay derives the hop secret from `alpha` and its static
`onion` key (GR-2 key 2). That is ephemeral–static Diffie–Hellman per hop,
forward-secret *at epoch granularity* (CH-6), relay-authenticated through the
gossip record's Ed25519 signature — exactly what a circuit needs and all it needs.
A second stateful `Noise_XK` handshake would re-run the same DH, add round-trips a
one-shot dispersed share cannot afford, put a second wire format on the link that
I-4 would then have to launder, and buy **one** property Sphinx lacks: hiding the
*initiator's* static key. ScrambNet's circuit client has **no static key at all**
(it is anonymous by construction), so that property is vacuous. `XK` authenticates
machinery for a key that does not exist. Replacing Sphinx with XK (more round-trips
for less), or using XK for a side channel (every stateful client↔relay flow —
gossip GR-6, probing GR-12/GR-13 — is deliberately tunnelled *through* Sphinx so
the client stays unnamed, so no such channel wants a direct session) both fail on
inspection. The spec is better for deleting the line.

```
  THE "HANDSHAKE" IS THE SPHINX HEADER. NOTHING ELSE EXISTS.

  client (no static key)     guard G          middle M          exit X
  ─────────────────────     ───────          ────────          ──────
   per packet: pick ONE ephemeral x ; alpha_0 = x·B   (B = X25519 base)
        │
        │  share packet  [ alpha_0 | beta | gamma | delta ]   (SP-3)
        │────────────────────────▶│
        │     G: s_G = DH(alpha_0, onion_G) ─► hop key; peel one beta layer
        │     G: alpha_1 = blind(alpha_0)   (Sphinx re-randomisation)
        │                          │────────────────▶│
        │                          │  M: s_M = DH(alpha_1, onion_M) ─► hop key
        │                          │                  │──────────▶│
        │                          │                  │  X: s_X = DH(alpha_2, onion_X)
        ▼                          ▼                  ▼           ▼
   NO handshake RTT. NO second wire format. NO Noise message. The DH is
   ephemeral(client)·static(relay) at EACH hop, carried entirely in `alpha`.

   What Noise XK would have added, and why it is deleted:
      → e ; ← e,ee,s,es ; → s,se   (extra RTT, relay names a session, and the
      third message carries the INITIATOR static XK exists to hide — which our
      keyless client does not have, so there is nothing to send and no reason to run it)
```

- **CH-1 (delete the vestige).** Suite `0x01` has **no** Noise handshake; the
  Part 0 suite table row is removed. An implementation MUST NOT emit, expect, or
  negotiate any Noise handshake message on a circuit; a packet that is not a
  Part-1 share packet is not part of this protocol. *Attack this by naming a
  circuit operation the Sphinx header cannot perform — a hostile review tried and
  found none.*
- **CH-2 (the circuit handshake is the Sphinx header).** Per-hop key agreement
  MUST be the Sphinx construction of SP-3/SP-4: for each hop `i`, the relay
  computes `s_i = X25519(alpha_i, onion_i)` where `alpha_i` is the blinded group
  element it receives and `onion_i` is its static key (GR-2 key 2). All hop keys
  (routing-info stream cipher, the `gamma` MAC, the `delta` AEAD) MUST be derived
  from `s_i` by HKDF-BLAKE2s with distinct fixed labels (`"sphinx-rho"`,
  `"sphinx-mu"`, `"sphinx-delta"` — exact bytes vector-locked under roadmap 3.2).
  There is no other key agreement in the circuit layer.
- **CH-3 (the initiator is keyless, by construction).** A circuit client MUST NOT
  possess or present any long-term static key on the circuit path. Its only
  asymmetric secret is the **per-packet ephemeral** scalar `x` behind `alpha_0`,
  which MUST be freshly sampled from a CSPRNG per packet (roadmap 3.1 applies —
  the forward secrecy below is exactly as strong as this RNG) and destroyed after
  the packet is built. With no client static key, no initiator-hiding pattern has
  anything to hide; `XK`/`IK`/`KK` are all inapplicable to the circuit path (CH-7).
- **CH-4 (relay static authentication, without a handshake signature).** A client
  MUST obtain each relay's `onion` static key *only* from a gossip record whose
  Ed25519 signature (GR-2 key 7) over the canonical encoding — which covers key 2
  — it has verified (GR-4). Relay authentication is **offline and transferable**:
  once, when the record is validated, not interactively per circuit. There MUST
  NOT be an in-circuit relay signature (it would be a selector and a wire
  fingerprint, I-4). The honest limit: a client authenticates *the key*, not an
  *identity beyond that signature* — the sybil/eclipse residual lives in Part 2
  (OP-2, GR-19a/GR-20a), not here.
- **CH-5 (static-key rotation — the ≤7-day exposure window).** A relay MUST rotate
  its `onion` static key at least every `7` days (s), and MUST zeroize the private
  half of a retired key once the in-flight grace has passed; a relay that retains
  old statics enlarges its own exposure window and is non-conforming. Clients MUST
  reject a record whose `expiry` exceeds `created + 7 days` (GR-2 key 6). The
  rotation ceiling is enforced at both ends and is the ceiling on the
  static-compromise window (CH-6).
- **CH-5a (the `ee` gap, and the fix that is not XK).** A hostile review named the
  one property the deletion costs: because the hop DH is ephemeral(client)·
  **static**(relay), an adversary who records a relay's link traffic and then
  seizes its `onion` static *within the live epoch* can recompute that epoch's
  per-hop secrets and recover one hop's **linkage** for up to 7 days of recorded
  packets (never content — CH-6). A Noise `ee` would deny even that. This is a
  real regression from a *full interactive* handshake, but it is **not** a reason
  to keep `XK` (whose initiator-hiding does not close it) and is closable without
  a handshake: a deployment that judges the window too wide MUST either (a)
  **shorten rotation** below 7 days (CH-5 is a ceiling, not a target), or (b) add
  an **optional relay pre-key `ee`** — a short-lived ephemeral pre-key published
  in the gossip record, mixed into the hop secret at **zero** extra round-trips —
  rotated and destroyed so a late static seizure yields nothing for its lifetime.
  The pre-key's record field and rotation belong with GR-2 if a deployment adopts
  it; CH-5a settles only that the gap is real, bounded to linkage, and closable
  without the deleted handshake.
- **CH-6 (the forward-secrecy statement, precisely).** `[claim-critical]` An
  adversary that compromises relay `R`'s **static** `onion` private key at time `T`
  (and nothing else — ephemerals never left the clients and were destroyed, CH-3):
  (a) **past traffic is safe across epochs** — packets whose hop at `R` used an
  earlier, rotated-and-destroyed static are not decryptable (the key is gone,
  CH-5; the client ephemeral's discrete log is gone, CH-3); forward secrecy is at
  epoch granularity, the ≤7-day rotation being that granularity. (b) **Within the
  live epoch, exposure is one hop's *linkage*, never content** — for packets sent
  while the seized static was live, the adversary recomputes `s_i` for hops at `R`
  and peels `R`'s layer, learning `R`'s predecessor/successor, i.e. the metadata a
  malicious relay already sees. It yields **no** content: unconditional below `k`
  (I-2, Part 7), and above `k` the end-to-end AEAD is keyed from a pre-shared
  symmetric `kpair` with no DH transcript for the seized key to touch (SP-1a). A
  seized static buys *one hop's linkage on one epoch's packets* — exactly the
  guard+exit correlation the dispersal/disjointness design already treats as
  *mitigated, not eliminated*; compromising the static moves the adversary no
  further than *running* that relay already does.
- **CH-7 (initiator-hiding is not needed; the hop is `N`-shaped, not `XK`).**
  `[claim-critical]` Does the client need XK's hidden-initiator-static property?
  **No**, dispositively: the client has no initiator static key (CH-3), so the
  property is vacuous. In Noise's vocabulary the one-shot hop is a one-way,
  ephemeral-initiator, known-static-responder agreement — the shape of Noise `N`
  (`→ e, es`), not `XK`. The circuit uses no literal Noise message (CH-2: it is
  Sphinx, which subsumes this shape); the two messages XK adds past `N` carry
  nothing and exist only to authenticate a key we do not have. Initiator hiding is
  already provided more strongly by Sphinx (SP-4 uniformity; the client is never
  an endpoint a relay can name, GR-12). We replaced XK's initiator-hiding with
  *"the initiator is anonymous and keyless,"* which needs no pattern to hide what
  is not there.
- **CH-8 (relay↔relay sessions, if ever, are out of this part and not `XK`).** A
  future control or peering channel needing a stateful, bidirectional,
  mutually-authenticated session between two **named** parties (e.g. relay-to-relay
  link encryption) is a separate document and MUST still satisfy I-4 (CH-9). Even
  there `XK` is wrong: both relays' statics are **public** in their gossip records,
  so there is nothing to hide and an already-known-static pattern (`IK`/`KK`) fits.
  This section specifies no such channel; it only forecloses re-importing `XK` by
  reflex.
- **CH-9 (I-4 by having no second wire format).** `[claim-critical]` The circuit
  layer puts nothing on the wire but Part-1 share packets, every byte uniform
  (SP-4). There is **no** Noise handshake message to make uniform — the cleanest
  I-4 outcome, achieved by *not having* a second protocol. A Noise XK transcript
  has recognizable structure (message-length pattern, `e`/`s` public-key fields);
  keeping XK would have *added* an obfuscation requirement that deletion removes.
  Any future session channel (CH-8) inherits this obligation in its own document.

**What section 5 does not decide.** The Sphinx parameters themselves (group,
blinding, MAC, exact HKDF labels and chaining) are §3 and roadmap 3.2's vectors;
CH-2 references them. Post-quantum: suite `0x02` may replace the X25519 hop DH with
a PQ KEM — CH-6's forward-secrecy *shape* is unchanged (ephemeral + ≤7-day static
rotation), the primitive changes, and the I-2 content floor is PQ-safe regardless
(SP-1a). The relay↔relay channel (CH-8) and the optional pre-key `ee` field
(CH-5a) are left to future parts. CH-4 authenticates a *key a record signed*, not
an identity beyond it: the gossip/eclipse residual is Part 2's (OP-2).

## 6. What this part does not decide

Path selection and disjointness enforcement (OP-1), mix parameters (OP-5),
fragmentation (SP-8), decoy economics (SP-9) are open on purpose. Each has a
numbered issue; argue there, with numbers.
