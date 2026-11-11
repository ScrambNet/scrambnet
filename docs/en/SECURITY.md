# Security policy

ScrambNet is pre-alpha: a specification and a proof-of-concept, not a system to
protect real secrets with yet. The most valuable contribution you can make is a
break.

## What counts as a finding

- A flaw in the **design**: a way to read content below `k` captured shares; a
  way to link shares of one message (SP-7); an eclipse, sybil, or
  disjointness-defeating attack on discovery or path selection; anything that
  violates an invariant (I-1…I-4).
- A flaw in the **proof-of-concept** code under `poc/`. Note that the PoC
  deliberately uses non-constant-time arithmetic and toy constructions; those
  are documented non-goals, not findings. A deviation from the spec, or a
  spec defect the code reveals, is a finding.

## How to report

- **Design flaws and PoC issues that are not sensitive:** open a public issue.
  Open discussion is the point of this repository.
- **Anything you believe should be handled privately first:** email
  `scrambnet@proton.me`. Encrypt sensitive reports to the project key (see
  below). We aim to acknowledge **within 7 days**; if you have had no reply by
  then, treat it as lost in the pseudonymous plumbing and ping again on a public
  issue (without the sensitive detail) so we notice.

Please do not include your legal identity in a report unless you want it
public. Pseudonymous reports are welcome and get the same consideration.

## Scope

In scope: the specification in `docs/`, the PoC in `poc/`. Out of scope: the
security of a contributor's own device or account; the GitHub platform itself;
denial of service against this repository.

## Project key

A PGP key for `scrambnet@proton.me` is published in the repository as
[`scrambnet-pubkey.asc`](../../scrambnet-pubkey.asc). Encrypt sensitive reports
to it.

```
Fingerprint: E5B5 399D 751F 830D 35CB  5F4A 3087 9F3B F93D 44F7
Algorithm:   Ed25519 (sign) + Cv25519 (encrypt)
Created:     2026-11-11   Expires: 2028-11-10
```

Verify the fingerprint against this file (and, ideally, against a second copy of
this document on a different mirror) before trusting the key — the point of
publishing it in-band *and* as a committed file is that the two must agree.

To use it:

```
gpg --import scrambnet-pubkey.asc
gpg --fingerprint scrambnet@proton.me     # must match the line above
gpg --encrypt --armor -r scrambnet@proton.me your-report.txt
```

**Rotation (why the key expires, invariant I-3).** The key expires in two years;
it is deliberately not an immortal singleton. Before it lapses, the next key
will be published here and **signed by this one** while this one is still valid,
so the handover is verifiable rather than an act of faith. If this key is ever
lost or compromised before expiry, a revocation certificate (generated and held
offline at creation time) will be published here and pushed to
`keys.openpgp.org`, and a new key announced the same way. No single disclosure
key is a permanent point of trust.

## Disclosure

Coordinated disclosure for anything that could endanger users of a future
deployment; immediate public discussion for everything at this pre-alpha stage,
where there are no users to endanger and the goal is to break the design before
anyone relies on it.
