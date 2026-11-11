# Cross-implementation conformance (roadmap 3.2)

A second ScrambNet implementation, in any language, **conforms** to suite `0x01`
iff it reproduces every vector in [`vectors.json`](vectors.json) byte-for-byte —
the same check [`test_vectors.py`](test_vectors.py) runs against this reference
implementation. The vectors are the contract (I-1: a hostile implementer builds
an interoperable node from the spec and these vectors, with no other knowledge).

Each vector section pins one keyed construction and names the spec requirement it
locks:

| Section | Pins | Spec |
|---|---|---|
| `gf_mul`, `gf_tables` | GF(2⁸) field: `0x11b`, generator 3; `_EXP`/`_LOG` tables pinned normative (by hash and in full) | Part 7 / Part 1 |
| `shamir` | `split` determinism given fixed coefficients | SP-2 |
| `params` | the `(k,n)` packed byte: `params = (k<<4)|n`, `k = params>>4`, `n = params&0x0F` | SP-7a |
| `tags` | `share_tag = PRF(K_r, msg_nonce ‖ index)` | SP-7 / SP-7b |
| `hkdf` | HKDF-BLAKE2s — the KDF under `content_key`, `k_tag`, `box_id` | SP-1a / RZ-11 |
| `e2e` | the content path `seal`/`open_` (ChaCha20-Poly1305 under `content_key`) | SP-1a |
| `e2e_dispersal` | the **composition** encrypt → split → reconstruct → decrypt | SP-1 |
| `rendezvous` | `box_id` across drops and epochs, one HKDF discipline | RZ-3 / RZ-10 / RZ-13 |
| `records` | canonical CBOR + the strict Ed25519 profile, positives **and** negatives | Part 2 §2A, GR-21..GR-30 |
| `sphinx_hop` | **pending-implementation** — see below | Part 1 §5 CH-2 |

## How a second implementation certifies

1. Build the GF field and confirm `gf_tables.exp_blake2s` / `log_blake2s` match
   byte-for-byte — if the field differs, nothing else can agree.
2. Reproduce every positive vector's output exactly.
3. For `records`, additionally **reject** every negative vector, each for the
   `violates` clause it names (GR-30). The `mixed_order_A` / `mixed_order_R`
   negatives are the load-bearing ones: they are rejected only by GR-28's
   `[L]·P` subgroup test, so an implementation that used a permissive (ZIP-215)
   Ed25519 library — which would *accept* them — fails here. That is the test's
   purpose.
4. The reference Ed25519 in [`gossip.py`](gossip.py) is itself cross-checked
   bit-for-bit against an independent library in `test_gossip.py`; a second
   implementation inherits that assurance by matching the vectors.

## The one honest gap: `sphinx_hop`

The Sphinx per-hop key agreement (Part 1 §5, CH-2: `s_i = X25519(alpha_i,
onion_i)` and the hop keys via HKDF-BLAKE2s under labels
`sphinx-rho`/`sphinx-mu`/`sphinx-delta`) has **no reference implementation in this
toy** — `dispersal.py` operates only on the share payload and declares "no onion
layer." Its vectors are therefore **declared pending, not hand-waved**: until a
node implements the onion layer, two implementations are not yet proven to
interoperate at the circuit layer (I-1), and `sphinx_hop` records exactly that.
When the layer lands, `sphinx_hop` is replaced by `(alpha_i, onion_i) → s_i` and
the three label-derived hop keys, and the coverage guard in `test_vectors.py`
(`test_every_section_is_covered`) ensures the new vectors cannot be added without
a conformance check.

## Regenerating the vectors

`vectors.json` is generated, not hand-edited:
`_gen_record_vectors.py` emits the `records` section and
`_gen_conformance_vectors.py` emits `hkdf`/`gf_tables`/`params`/`e2e_dispersal`/
`sphinx_hop`; the rest are emitted by their own modules' demos. Re-running them
must leave the file unchanged (determinism is the point).
