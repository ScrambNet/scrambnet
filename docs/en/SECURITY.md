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
  below). We aim to acknowledge within a reasonable time; please allow for a
  pseudonymous, volunteer-paced project.

Please do not include your legal identity in a report unless you want it
public. Pseudonymous reports are welcome and get the same consideration.

## Scope

In scope: the specification in `docs/`, the PoC in `poc/`. Out of scope: the
security of a contributor's own device or account; the GitHub platform itself;
denial of service against this repository.

## Project key

A PGP key for `scrambnet@proton.me` for encrypted reports will be published
here and in the repository. Until a signed key is listed in this file, treat
email as confidential-but-unauthenticated and keep the most sensitive details
for a channel you can verify.

## Disclosure

Coordinated disclosure for anything that could endanger users of a future
deployment; immediate public discussion for everything at this pre-alpha stage,
where there are no users to endanger and the goal is to break the design before
anyone relies on it.
