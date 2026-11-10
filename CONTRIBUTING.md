# Contributing to ScrambNet

The project is at the pre-specification stage. The most valuable contributions right now,
in order:

1. **Attack the threat model.** Open an issue against any claim in
   [docs/threat-model.md](docs/threat-model.md), especially the open problems list.
2. **Propose specification text.** PRs against `docs/` — RFC-style, one mechanism per PR.
3. **Translate.** The READMEs exist in six languages; `docs/` is English-only so far.
   Translations and corrections by native speakers are first-class contributions.
4. **Prior-art pointers.** If something here reinvents a wheel, name the wheel. The design
   philosophy is to compose published, attacked work, never to invent where citation works.

## How we work

- One topic per issue. Design debates live in issues, decisions get recorded in `docs/`.
- English is the canonical language of `docs/`; if you edit a README in one language,
  either update the others or say in the PR that they are now stale.
- No code until the threat model and wire spec stabilize. When code starts: one small,
  boring, mobile-first reference client.

## Pseudonymity policy

Real names are not required and never will be. Pseudonymous and anonymous contributions
are first-class. There is no CLA; by contributing you release your contribution to the
documentation under [CC0 1.0](LICENSE).

If your own threat model calls for it, protect yourself:

- Use your forge's noreply address in commits:
  `git config user.email "USERNAME@users.noreply.github.com"`
- Commit in UTC so your timezone does not leak:
  `git config alias.ci '!TZ=UTC git commit'`
- Do not sign commits with a key tied to your legal identity; if you sign, use a key
  created for this pseudonym alone.
- Do not reuse nicknames from elsewhere, and remember that prose style is a fingerprint.

## Neutrality

This network carries packets, not opinions. It protects dissidents and their opponents
with the same mathematics; political adversaries are not enemies. Proposals that would
make the network favor or disfavor particular viewpoints, origins, or destinations will
be declined regardless of the viewpoint — that neutrality is the project's security
argument as much as its ethics.
