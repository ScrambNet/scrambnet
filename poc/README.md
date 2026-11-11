# Dispersal core — reference PoC

Executable companion to spec [Part 1](../docs/spec/01-share-packet.md) and
[Part 6](../docs/spec/06-rendezvous.md). Pure
Python 3, standard library only, written to be read and attacked: this is an
executable specification, not the future node.

What it demonstrates:

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

    python3 dispersal.py        # demo
    python3 test_dispersal.py   # test suite, includes vectors.json
    python3 rendezvous.py       # Part 6 demo: drops, disciplined polling
    python3 test_rendezvous.py  # Part 6 test suite

`vectors.json` carries cross-implementation vectors: an implementation that
matches them interoperates at this layer.

What it is **not**: production code. No constant-time arithmetic, no
networking, no onion layer, no end-to-end AEAD (per SP-1 this layer only ever
sees opaque ciphertext). Do not use it to protect anything.

*Traduzioni: [italiano](README.it.md) · [español](README.es.md) ·
[Deutsch](README.de.md) · [français](README.fr.md) · [中文](README.zh-CN.md)*
