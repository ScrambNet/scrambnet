# ScrambNet Specification — Part 7: The Security Argument for I-2

**Status: DRAFT.** This part proves, or bounds, the one claim everything else
rests on: the unconditional content floor (I-2). It is normative where it states
a requirement (`SA-n`) and expository elsewhere. If the argument here is wrong,
the project is wrong, and the fastest way to find out is to attack *this file*.

The claim is deliberately narrow. Read the two sentences in §1 first; everything
after is their justification and their price.

## 1. What is proved, in two sentences

- **Unconditional tier (the floor).** An adversary who observes any `k−1` of the
  `n` shares of a message learns **nothing** about the end-to-end ciphertext —
  not "nothing feasible", but nothing at all, against unbounded computation and
  any future quantum computer — because the `k−1` shares are *statistically
  independent of the secret* (Shamir, proved in §3).
- **Computational tier (the belt).** An adversary who obtains `k` or more shares
  reconstructs the ciphertext and then faces the end-to-end AEAD; from there,
  content confidentiality is exactly the confidentiality of ChaCha20-Poly1305
  under a key the adversary does not hold (SP-1a), which **is** a computational
  assumption.

These two tiers are **disjoint and exhaustive**: every adversary holds either
`< k` shares (tier 1) or `≥ k` (tier 2), and the guarantee in each is stated
without reference to the other. The rest of this part proves tier 1 rigorously,
states precisely why tier 2 cannot be unconditional, and nails the one place the
two tiers could leak into each other (§4: the AEAD key must be invisible below
`k`).

## 2. Model and adversary

- A **message** is a byte string `M`. The sender first computes the ciphertext
  `C = AEAD-Seal(K, N, M)` (SP-1a), where `K = HKDF(kpair, "e2e-content")` and
  `N` is the message nonce. `C` — never `M` — is what enters dispersal.
- Dispersal is `(n, k)` Shamir over GF(2⁸), **per byte**: for byte position `j`,
  the secret byte `c_j` is the constant term of an independent, uniformly random
  degree-`(k−1)` polynomial `f_j`, and share `i` at position `j` is `f_j(i)` for
  distinct nonzero evaluation points `x_1,…,x_n ∈ GF(2⁸)\{0}` (the share
  indices). "Independent, uniform" is load-bearing and is itself a requirement
  (SA-3 below).
- The **below-`k` adversary** sees: any `k−1` complete shares (every byte
  position of those `k−1` indices), plus everything public — the spec, the
  evaluation points, `n`, `k`, the wire bytes of other packets. It does **not**
  see `K`, `N`, or any share beyond its `k−1`. It has unbounded computation.
- We prove a property of `C` (the ciphertext). What the adversary ultimately
  wants is `M`; §4 shows the `C`-level result transfers to `M` because `K` is
  not in the adversary's view.

## 3. The floor: any `k−1` shares are independent of the secret (tier 1)

**SA-1 (per-byte perfect secrecy).** Fix a byte position `j`. Let the secret
byte be `s = c_j` and the polynomial be
`f_j(x) = s + a_1 x + … + a_{k−1} x^{k−1}` with `a_1,…,a_{k−1}` independent and
uniform over GF(2⁸). For any set of `k−1` distinct nonzero points
`x_{i_1},…,x_{i_{k−1}}` and any target values `y_1,…,y_{k−1}`:

> the number of coefficient tuples `(a_1,…,a_{k−1})` consistent with
> `f_j(x_{i_t}) = y_t` for all `t` is **exactly one, for every candidate `s`**.

*Proof.* Fix `s`. The `k−1` equations `f_j(x_{i_t}) = y_t` are linear in the
`k−1` unknowns `a_1,…,a_{k−1}`; their coefficient matrix is the Vandermonde
matrix on the distinct nonzero points `x_{i_t}` (columns `x, x², …, x^{k−1}`),
which is invertible over the field. So for each `s` there is exactly one
solution. Hence `Pr[shares = (y_1,…,y_{k−1}) | secret = s]` is the same
(`= 1 / 256^{k−1}`) for every `s`: the shares are **independent of `s`**. ∎

This is the enumeration the PoC runs by brute force for `k = 3`
(`poc/dispersal.py`, `floor_demo()` — all 256 candidate bytes come back equally
consistent, in exactly one way each). SA-1 is the general statement of what that
demo checks for one case.

**SA-2 (the whole secret, not one byte — joint independence).** Let the
ciphertext be `C = c_1 c_2 … c_L` (all `L` bytes). The sender draws the
coefficient tuples for the `L` positions **independently** (SA-3). Then the full
`k−1`-share view — the length-`L` byte strings held at `k−1` indices — is
*jointly* independent of `C`:

> `Pr[view = v | C = c]` is identical for every `c ∈ (GF(2⁸))^L`.

*Proof.* The view factors over positions: the bytes the adversary sees at
position `j` depend only on `(c_j, a^{(j)}_1,…,a^{(j)}_{k−1})`, and across
positions the coefficient draws are independent (SA-3). So
`Pr[view = v | C = c] = ∏_{j=1}^{L} Pr[view_j = v_j | c_j]`, and by SA-1 each
factor equals `1/256^{k−1}` regardless of `c_j`. The product is therefore
`1/256^{(k−1)L}` for **every** `c`. Independence of `C` follows. ∎

SA-2 is the step the PoC's old tests did **not** cover: `floor_demo()` is one
byte and the statistical tests checked only a marginal (one position's
distribution). The product-over-positions argument is what makes the floor a
statement about the *message*, and it holds **only because** the per-position
coefficients are independent — which is exactly the failure mode SA-3 guards.

**SA-3 (coefficient randomness is floor-critical). [normative]** The polynomial
coefficients `a^{(j)}_t` MUST be drawn from a cryptographically secure RNG,
independently across both coefficient index `t` and byte position `j`. The floor
is exactly as strong as this randomness and no stronger:

- **Reuse across positions** (e.g. one coefficient tuple reused for every byte,
  or a short repeating key-stream of coefficients) breaks SA-2's independence:
  the factorization fails, the `k−1` shares become *correlated* with `C`, and an
  adversary can gain information about `C` by cross-correlating positions. A
  floor built on reused coefficients is not a floor.
- **Low-entropy RNG** (a weak or predictable generator) collapses the uniform
  draw of SA-1: if the adversary can predict or enumerate the coefficient
  distribution, the "exactly one consistent tuple per `s`" count is no longer
  uniform over `s`, and the shares leak.

This is the single most important implementation requirement in the whole
specification. It is cheap to satisfy and catastrophic to get wrong, and unlike
an AEAD weakness it cannot be fixed by rotating a key later — a message split
under bad coefficients is compromised forever. A conforming implementation MUST
treat the coefficient RNG as its highest-assurance component (see also the
reference-crypto requirements, roadmap 3.1).

## 4. The seam: the AEAD key must be invisible below `k` (no leak between tiers)

SA-2 proves the `k−1` shares are independent of the **ciphertext `C`**. The
adversary wants the **plaintext `M`**. The bridge is that `M = AEAD-Open(K,N,C)`
and the below-`k` adversary does not hold `K`. This is only true if `K` never
appears in anything that adversary sees — which is a requirement, not a
coincidence:

**SA-4 (key separation across the floor). [normative]** No value derivable by a
below-`k` adversary may reveal `K = HKDF(kpair, "e2e-content")` or `kpair`. In
particular:

- `K` MUST NOT be placed in any share, tag, or packet field. (In this design it
  is not: `K` is used only at the endpoints, to seal and open `C`; the shares
  carry bytes of `C`, and the SP-7 tag is derived from a *label-separated* key
  `HKDF(kpair, "tag")`, not from `K` — see §5 and SP-7a.)
- Therefore a below-`k` adversary's view is independent of `C` (SA-2) **and**
  carries no information about `K`. It can neither read `C` (nothing there) nor
  obtain `K` to attack a future `C`. The two tiers do not leak into each other.

If SA-4 were violated — if any below-`k`-observable value were a function of `K`
— the floor would still hide *this* `C`, but the adversary could harvest `K` and
read it the moment it later obtains `k` shares, or read *other* messages under
the same `K`. SA-4 is what keeps the unconditional tier from silently becoming
computational.

## 5. Why tier 2 is computational, stated honestly

At `k` or more shares the adversary reconstructs `C` exactly (Lagrange
interpolation — this is the *intended* path, it is how the recipient reads mail).
From `C`, confidentiality of `M` is precisely the confidentiality of
ChaCha20-Poly1305 under `K`. That is a computational assumption: it can in
principle be broken by cryptanalysis of the cipher. It is **not** broken by a
future quantum computer via Shor, because `K` comes from a pre-shared *symmetric*
secret with no Diffie-Hellman transcript to invert (SP-1a); Grover costs at most
a halving of the effective key length, hence the ≥256-bit recommendation. So the
honest statement of tier 2 is: *as strong as a symmetric AEAD under a key the
adversary does not have, and no stronger* — a real, conventional, quantum-aware
computational guarantee, not an unconditional one. The project never claims
otherwise, and every public document now states the regime (roadmap 0.1).

## 6. What this part does **not** prove

- **Linkage / metadata.** I-2 is about content, not about who talks to whom.
  Nothing here hides that *some* flow occurred on a captured share path; that is
  the threat model's admitted residual, narrowed by dispersal, not nullified.
- **Availability.** A hostile party on a share path can corrupt or drop a share;
  the AEAD fails closed (SP-7a), so this is denial of service, not disclosure.
  SA-1…SA-4 say nothing about the message *arriving*, only about what a below-`k`
  adversary *learns* if it does not.
- **Timing correlation between shares (SP-9 / OP-4).** SA-2 is about the *values*
  of the shares, not their emission times. `n` shares entering the network within
  milliseconds are a fingerprint even though their bytes are independent of `C`.
  That is an open problem, not something this proof addresses.
- **The AEAD itself.** Tier 2 inherits whatever is true of ChaCha20-Poly1305. If
  that cipher falls, tier 2 falls; the floor (tier 1) does not.

## 7. Requirements introduced here

- **SA-1** — per-byte perfect secrecy of any `k−1` shares (proved).
- **SA-2** — joint independence over the whole secret (proved, given SA-3).
- **SA-3** — *coefficient randomness is floor-critical*: CSPRNG, independent per
  position and per coefficient. **[normative, highest assurance]**
- **SA-4** — key separation across the floor: no below-`k`-observable value
  reveals `K` or `kpair`. **[normative]**

SA-1 and SA-2 are theorems; SA-3 and SA-4 are the two conditions under which the
theorems describe the real system. Break any of the four — find a view the proof
missed, a correlation SA-3 lets through, a field that carries `K` — and you have
broken I-2. That is the invitation.
