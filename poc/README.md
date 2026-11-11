# Dispersal core — reference PoC

Executable companion to spec [Part 1](../docs/en/spec/01-share-packet.md) and
[Part 6](../docs/en/spec/06-rendezvous.md). Pure
Python 3, standard library only, written to be read and attacked: this is an
executable specification, not the future node.

What it demonstrates:

- the **full SP-1 composition**, executed, not asserted: `e2e.py` encrypts the
  message under a pre-shared pair key (ChaCha20-Poly1305, verified against the
  RFC 8439 test vectors), then `dispersal.send()` splits the *ciphertext* and
  `receive()` reconstructs and decrypts — encrypt → split → reconstruct →
  decrypt, with a flipped share failing closed at the AEAD, never reconstructed
  to garbage (SP-1, SP-1a);
- (n, k) Shamir splitting over GF(2^8), per byte, and reconstruction from any
  k shares (SP-1, SP-2);
- the unconditional floor (I-2), by brute force: `floor_demo()` enumerates
  every polynomial consistent with k−1 observed shares and finds all 256
  candidate secret bytes *exactly equally consistent* — nothing is learned,
  even with unbounded compute;
- SP-7 recipient-keyed tags (keyed BLAKE2s) and the tag-window recognition
  they imply;
- SP-8 random padding and the share-payload layout of Part 1 §4;
- the honest price: an (n, k) dispersal transmits ×n the ciphertext volume
  (issue #4).

Run:

    python3 e2e.py              # SP-1 belt: AEAD KAT + seal/open round trip
    python3 test_e2e.py         # AEAD test suite (RFC 8439 vectors)
    python3 dispersal.py        # demo: full SP-1 encrypt->split->...->decrypt
    python3 test_dispersal.py   # test suite, includes vectors.json
    python3 rendezvous.py       # Part 6 demo: drops, disciplined polling
    python3 test_rendezvous.py  # Part 6 test suite
    python3 network_sim.py      # experiment: k-path adversary vs network size
    python3 test_properties.py  # statistical property tests (uniformity, SP-7)
    python3 run_all.py          # every demo + every test, one verdict

## The experiment: what the adversary buys, in numbers

`network_sim.py` turns the open questions of issues #2/#4/#10 into a table. It
models one message as n=4 shares over 4 disjoint circuits into 4 drops; a
k-path adversary owns a fraction of relays and "sees" a circuit when it holds
both its guard and its exit:

    sender                                         drops (one share each)
      |  share 1 --[guard]--[mid]--[exit]-->  box 1  \
      |  share 2 --[guard]--[mid]--[exit]-->  box 2   |  recipient polls,
      |  share 3 --[guard]--[mid]--[exit]-->  box 3   |  takes any 3,
      |  share 4 --[guard]--[mid]--[exit]-->  box 4  /   reconstructs

- **seen >= k** -> content break (and only then; below k the I-2 floor holds
  unconditionally, at any network size);
- **seen < k** -> content safe, but each seen circuit still leaks that *some*
  flow ran — the metadata loss the threat model admits dispersal narrows but
  never nullifies.

The result it prints: content breaks are rare and vanish as the network grows
enough to build AS-disjoint circuits; linkage leak is small but nonzero and
worst on a tiny network that *cannot* build them — which is exactly why a young
network must run, and declare, a degraded "small-network mode" (issue #4).
These numbers are strawman: reproduce them, break the model, argue on the
issues.

`vectors.json` carries cross-implementation vectors: an implementation that
matches them interoperates at this layer.

What it is **not**: production code. The AEAD in `e2e.py` is pure-Python and
**not constant-time** — it is correct (it matches the RFC 8439 vectors) but
leaks through timing, so a real node MUST use a vetted constant-time library.
No constant-time arithmetic anywhere, no networking, no onion layer. Do not use
it to protect anything.

*Traduzioni: [italiano](README.it.md) · [español](README.es.md) ·
[Deutsch](README.de.md) · [français](README.fr.md) · [中文](README.zh-CN.md)*
