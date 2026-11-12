# Running a ScrambNet node — exposure and the neutrality posture

**Running any ScrambNet node is a visible, deliberate act with real and non-zero
risk.** This document is honest about that. What follows tells you what each role
reveals and what it provably cannot reveal, so you can decide. It is a technical
and posture statement, **not legal advice**: this project is pseudonymous and
cannot know your jurisdiction, your adversary, or your law. Where the stakes
warrant it, seek your own counsel.

This is an informative brief, not a normative spec part. It leans on claims the
specification already makes — the invariants `I-1…I-4`, the dead-drop rules
(Part 6), the path-selection residuals (Part 3), the inference-dataset residuals
(Part 8) — and it points at them rather than restating them. Where the spec
declares a residual openly, this brief carries it openly too; it does not soften.

## What each role sees, and what it cannot

Each statement has the same shape: **what the role sees · what it provably cannot
see, and the exact limit of that claim · the honest residual.** The roles are the
ones the architecture defines ("Who runs what"); nothing here invents a role the
network does not have.

### Pure client

As a client you are the lowest-exposure role — "near-invisible," riding bridges
and chameleon transports — but **not zero-exposure**, and this brief will not
pretend otherwise. Your **guard** (your first hop) sees your real IP address and
when you are active (see below); that is a client-side exposure, not merely a
guard's property. Retrieval also has a standing cost and metadata surface: a
client polls its drops on a mandatory fixed schedule (`RZ-9`), ~212 MB/month
across four drops before you send anything (`RZ-16b`), and that schedule — not
the content — is observable. You are low-exposure; you are not invisible.

### Guard (a client's first hop)

A guard is the one relay that sees a client's real IP address and activity
timing. If you run a guard, you learn that a particular IP spoke ScrambNet to
you, and when. You do **not** learn where that traffic was going or what it
contained: by `I-4` every packet crossing you is fixed-size noise
indistinguishable from uniform random bytes, and you hold only one share of one
message travelling one of several paths.

The exact limit of "you cannot reconstruct the message." The content floor
(`I-2`) is unconditional **below `k` captured positions**: hold fewer than `k`
shares and they are information-theoretically noise, with no computational or
quantum escape. But *reaching* that floor depends on the `n` paths being
genuinely **disjoint**, and disjointness is **inferred, not proven** (`OP-1`;
`PS-11`, "believed disjointness is not real disjointness"). A chosen, hostile
map can *steer* an adversary's relays into position and drive content capture
"from ~0% to 100% at ~15% ownership" (`PS-12`/`ID-8a` — a finding the project
carries openly after an earlier overstatement was broken). So the honest claim is
not "a guard cannot reconstruct," full stop; it is "no coalition reconstructs
**below `k` captured positions**, and whether your paths truly reach that floor
is an unverified property a steering adversary can defeat above a threshold."

**The honest residual:** you do see client IPs. That is the sharpest exposure of
any relay role, and it is structural, not a leak to be fixed. IPs of people who
use ScrambNet pass through your node and are visible to anyone who can watch its
connections.

### Middle relay

A middle relay sees neither end. By the Sphinx construction and `I-4` it cannot
tell whether its predecessor is the originating client or another relay, nor
whether its successor is the last hop. It sees no client IP (that is the guard's
position), no destination, no content; it holds one encrypted share. It is the
lowest-information relay role — noise passing between two other machines. Its
exposure is the general one every role shares (below): running it is a visible
act, and it forwards traffic you cannot inspect.

### Drop (dead-drop storage, Part 6)

A drop stores shares deposited into boxes and serves them when polled. What it
stores is, by `I-2`, information-theoretically unreadable: each stored share is
below `k` and indistinguishable from random noise to anyone — **including you,
the operator** — without the other shares, which are on other drops you do not
control (`RZ-5`: no single drop ever holds two shares of one message; the drop
set is `d = n = 4`, `k = 3`, so a drop holds exactly one share, `< k`). You
cannot read what you store, cannot tell two boxes' contents apart, and cannot
link a deposit to a sender (`RZ-2`/`RZ-10`, `SP-7`). This claim is exact and it
is not softened: a drop operator is genuinely content-blind.

**Content-blind is not the same as delivery-neutral, and this is the honest
residual.** A drop sees **timing**: the public polling cadence (`RZ-9`) and the
deposit times into the boxes it holds, within one epoch; a drop holding several
boxes can correlate deposit *timestamps* across them even under perfect poll
independence (`RZ-16`/`OP-9`, carried openly in the rendezvous spec §9). And a
drop *can* deny **delivery** without reading anything: oldest-first eviction plus
the 8-slot retrieval window means a flooder — even a cheap phone — can bury
honest mail past the window in ~17 seconds (`RZ-15`), a delivery-flooding residual
the spec declares has no sufficient defense yet (`OP-9`). So: you store unreadable
noise, but you observe *that* noise arrived and was collected and when, and the
storage mechanics are a delivery surface. That timing-and-delivery exposure is the
drop's genuine residual, declared not hidden.

### Bridge (entry point distributed along the social graph)

A bridge is an entry point handed person-to-person where the open network is
blocked (Lox-style trust levels). It sees guard-level information for the clients
that reach it (their IP, nothing downstream). Its distinctive exposure is **being
discoverable as a bridge**: a censor who successfully poses as a user can learn
your bridge's address and block or watch it. Social-graph distribution limits how
fast and how widely an address leaks — "a censor can pose as one user; it cannot
pose as everyone's friend" — but does not make a bridge undiscoverable.

**The honest residual:** running a bridge means an address of yours is, by
design, circulating among strangers-of-strangers, some of whom may be
adversaries. Enumeration-resistance is an arms race the threat model calls
sustainable, not won.

### Mesh node / gateway (blackout layer)

A mesh node relays device-to-device over Wi-Fi Direct / Bluetooth during a
blackout; a gateway bridges the mesh back to the internet when a route exists.
Its content exposure is the same as any relay — fixed-size shares it cannot read
(`I-2`/`I-4`). Its distinctive exposure is **physical and local**: its visibility
is a radio signal at neighborhood scale, correlatable to a location and
potentially a person, precisely when and where an adversary has switched off the
internet and is most motivated. This is why the architecture makes it always an
explicit opt-in. A **gateway** carries *both* exposures at once: the physical/local
exposure on the mesh side, **and** the ordinary relay exposure on its internet
side — its internet-facing IP is an observable ScrambNet node to its own ISP —
while still never being a clear-web exit (below).

**The honest residual:** of all roles this one trades the strongest
content-blindness for the weakest operator-anonymity. The bytes are noise; the
transmitter is in a place. No invariant protects a radio's physical locatability.

### The clear-web exit that does not exist

ScrambNet has **no clear-web exit role**, and this matters most for operators.
The clear-web exit is the single most exposed role in Tor: a Tor exit's IP
appears as the apparent source of whatever its users send to the open internet,
and that operator receives the abuse complaints, takedown notices, and
law-enforcement attention for traffic they neither chose nor can see. ScrambNet
has no equivalent. A message's terminal hop delivers a share into a dead drop
(Part 6) — unreadable noise in project-internal storage — not out to an arbitrary
third-party host. **No ScrambNet node's address appears as the origin of
attributable traffic arriving at an outside service** (the mesh gateway touches
the internet, but it carries ScrambNet-internal noise toward a relay, not a
user's traffic out to a clear-web host). This is why the architecture states a
relay/drop operator's exposure is "structurally lower than a Tor exit's" — a
**technical**-exposure comparison, never a claim about your legal liability.
Stated precisely: this removes the *specific* exit-node exposure; it does **not**
make any role risk-free, and it does not make ScrambNet an exit proxy — it
structurally is not one, and that absence is a feature, including for you.

### Running more than one role

Most of the statements above describe a single role in isolation. One machine
commonly runs several — guard, relay, and drop together — and co-location creates
correlations none of the single-role statements show. A drop holding several
boxes correlates deposit timing across them (`RZ-16` §9); a relay that is **also
a user** and is "up exactly when its operator chats is an intersection attack on
itself" (the architecture names this directly). The discipline the architecture
prescribes is the mitigation: an always-on schedule independent of your own use,
so your uptime says nothing about your activity. If you run more than one role,
your exposure is not the minimum of the roles — it is their combination.

## The abuse-handling posture

This is the part a hostile reader will test hardest, so every sentence of it is
built on a true inability, and none of it introduces a lever.

**(a) The inability, stated as a security property.** ScrambNet cannot read,
identify, target, or content-selectively block or prioritize any message, user,
or content. This is not a policy we adopt and could reverse; it is a property of
the design. A drop stores shares that are information-theoretically unreadable
below `k` (`I-2`); a relay forwards fixed-size noise it cannot distinguish from
any other (`I-4`); there is no registry of users (there is no sign-up), no
directory authority, and no privileged party anywhere in the protocol (`I-3`).
The project has no key, no switch, and no position in the network from which
content *could* be inspected or filtered. The same mathematics protects everyone
because it cannot tell anyone apart, and that indiscriminacy is what makes the
protection trustworthy: a network that *could* choose sides is one a powerful
adversary could *make* choose sides. (One honest scope note: content-blindness is
not delivery-neutrality — the storage mechanics of a drop are a delivery surface,
`RZ-15` — so "cannot block" here means *cannot content-selectively block*, which
is the property that matters for neutrality.)

**(b) What the project genuinely can do.** What we can do, we do in the open:
publish the complete design so anyone can study, attack, or reimplement it
(`I-1`); receive and act on **vulnerability** reports under the security policy
(SECURITY.md); fix defects; and keep saying plainly what the network does and does
not protect. That is the whole list. None of it involves looking at, reaching for,
or acting on anyone's traffic, because the design gives us no way to do so — and
the vulnerability channel is for defects in the design and code, never a channel
to report traffic or users, because there is nothing we could do with such a
report and its existence must not imply otherwise.

**(c) What the project refuses to build, and why.** We will not build a
moderation capability, a reporting backdoor, a content filter, a user block-list,
a "lawful access" tap, or any other mechanism that lets the project, an operator,
or anyone else read, target, or suppress content or users. We refuse not out of
indifference to harm but because such a mechanism is self-defeating on its own
terms. Any lever that can be aimed at content called "abuse" is the same lever,
pointed the other way, aimed at content called "dissent" — it is one capability,
and whoever can compel its use decides what it targets. It would be precisely the
single point of control `I-3` forbids and the side-choosing the threat model rules
out of scope. The moment such a lever exists, the network's promise is false for
everyone, including the people it was built to protect; the adversary no longer
has to break the mathematics, only to seize the lever. The absence of a moderation
mechanism is not a gap we failed to fill — it is a load-bearing security property
we are refusing to destroy. (Any flooding admission control the project ever
adopts — the open `OP-9` question `RZ-15` leaves unsolved — MUST be
content-blind and identity-blind by construction, and the leading candidate gates
by possession of a per-relationship contact card, not by viewpoint; an admission
rule that had to *identify a sender* or *inspect a deposit* would be a lever and is
forbidden under this same posture.)

**(d) The honest cost.** This is not free, and we will not pretend otherwise. A
network that cannot choose sides cannot choose *against* harm either. ScrambNet
can be used for things its authors find repugnant, and the project cannot prevent
that by design. The usual analogies — the postal system cannot read every letter,
a telephone network cannot listen for "bad" calls, TLS cannot refuse to encrypt a
criminal's connection — carry the shape of the point but **understate** it, and
the difference is the whole claim: post, telephone, and TLS endpoints *can* be
compelled by warrant to intercept a specific target, because a vantage point and
a key exist. ScrambNet's "cannot" is **stronger** — there is no position from
which a compelled operator *could* hand over content below `k` (`I-2`), and no
single party that *could* be ordered to publish a poisoned view of the network
(`I-3`; the spec names the "coerced, subpoenaed, or seized" reality directly).
The protections are indiscriminate because selective protection is not protection
— it is a list of who is allowed to be safe, kept by whoever holds the pen. We
accept the cost with open eyes: a tool powerful enough to protect the powerless
from the powerful cannot come with a switch the powerful can flip. The honest
summary is not "ScrambNet prevents abuse." It is: **ScrambNet protects
communication, and that protection does not come with an off-switch — for anyone,
against anyone, including us.**

## Where you are exposed anyway

Stated plainly and left standing — no "but don't worry," no implied safety.

- **Running any node is a visible act.** A relay publishes an address; a bridge
  circulates one; a mesh node emits a radio signal. The mathematics protects the
  *content and linkage of traffic*, not the *fact that your machine is on the
  network*. If being seen to run anonymity infrastructure is itself your risk, no
  invariant removes it.
- **A guard sees client IPs.** Structural, not a bug. IPs of ScrambNet users pass
  through your guard and are visible to anyone who can watch its connections.
- **A drop sees timing and shapes delivery.** Unreadable content, yes — but
  deposit and polling times within an epoch, cross-box deposit-timing
  correlation, and the eviction/flooding delivery surface are real, declared
  residuals (`RZ-15`/`RZ-16`/`OP-9`).
- **A bridge is discoverable.** By design it is handed to strangers; some may be
  adversaries. Enumeration-resistance is an arms race, not a guarantee.
- **A mesh node is physically locatable.** The bytes are noise; the transmitter
  is in a place, precisely when an adversary has switched off the internet.
- **Reaching the content floor depends on disjointness you cannot verify.** The
  `I-2` floor below `k` is unconditional; that your paths or drops are truly
  independent is inferred, not proven (`OP-1`/`PS-11`), and a steering map can
  defeat it above a threshold (`PS-12`). Run with that known.
- **Your local law can compel you regardless of what the bytes are.** This project
  cannot tell you what any authority may demand of you, and it will not pretend
  the network's content-blindness is a legal shield — it is a technical fact about
  the bytes, not a jurisdiction-specific legal conclusion. That a drop *cannot*
  read what it stores is true and may matter, or may not, depending on a law this
  pseudonymous project cannot know. **This is where you need your own counsel, not
  ours.** We state what is technically revealed; what it means for you, legally,
  is yours to find out.
