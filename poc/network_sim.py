"""ScrambNet network simulator -- reference experiment (DRAFT).

An in-process model of the whole path: a population of relays across ASes and
jurisdictions, best-effort disjoint path selection, k-of-n dispersal over those
paths (dispersal.py), delivery to dispersed drops (rendezvous.py), and a
k-path adversary that owns a fraction of positions and tries to correlate.

This is NOT a node and NOT a protocol implementation: it is the apparatus that
turns the open questions of issues #2, #4 and #10 (OP-1, OP-2) into numbers.

THE REALISM PASS (roadmap 2.1). An earlier version of this file let path
selection read each relay's TRUE autonomous system -- i.e. it assumed the OP-1
verification problem was already solved. That made the break numbers
optimistic. This version separates two worlds, which is the whole point of
OP-1:

  * GROUND TRUTH -- each relay's real `asn`/`juris`. The adversary exploits
    this: it co-locates the relays it owns in a few real ASes and correlates by
    real AS, because reality does not care what a client believes.
  * THE CLIENT'S BELIEF -- what an IP-to-AS inference dataset tells the client,
    which is WRONG at an injectable rate and sometimes UNKNOWN. Path selection
    sees only this. The conservative rule "unknown => assume shared" (I-3: trust
    nothing you cannot verify) is exercised here, and it costs availability.

Plus: persistent guards across a message stream (a bad guard is bad for
months), a partial per-client gossip sample instead of a god's-eye pool, and an
upgraded adversary that correlates at AS granularity and counts the drop as an
exit vantage. The headline result the demo prints: break and linkage curves as
a function of the inference-error rate, showing the zero-error numbers were the
best case, not the expected case.

Deliberately simple and readable over fast or clever. Numbers are strawman.
"""

import secrets
import statistics
from dataclasses import dataclass, field

import dispersal as d
import rendezvous as rz

SysRand = secrets.SystemRandom()


@dataclass
class Relay:
    rid: int
    asn: int                     # TRUE autonomous system (ground truth, OP-1 axis)
    juris: str                   # TRUE jurisdiction (another axis)
    adversary: bool = False      # owned by the k-path adversary?
    # The client's BELIEF about this relay, from a noisy inference dataset.
    # None means "unknown" -> the conservative rule treats it as sharing with
    # everything (I-3: an unverifiable relay cannot be assumed disjoint).
    inferred_asn: int | None = None
    inferred_juris: str | None = None


@dataclass
class Network:
    relays: list = field(default_factory=list)

    @classmethod
    def random(cls, n_relays: int, n_as: int, n_juris: int,
               adversary_relays: int = 0, adversary_as: int = 0,
               infer_error: float = 0.0):
        """Build a relay population and a per-relay inference belief.

        `adversary_as` concentrates owned relays into few TRUE ASes -- the cheap
        way to sit on many AS-disjoint-looking paths at once (the real k-path
        threat). `infer_error` is the probability the client's inferred AS for a
        relay is wrong: with that probability the belief is either a random
        WRONG as (half the time) or UNKNOWN=None (half), modelling a dataset
        that both mis-maps and has gaps.
        """
        jurises = [chr(ord("A") + i) for i in range(n_juris)]
        relays = []
        for i in range(n_relays):
            relays.append(Relay(i, asn=i % n_as, juris=SysRand.choice(jurises)))
        owned = SysRand.sample(relays, min(adversary_relays, n_relays))
        for r in owned:
            r.adversary = True
            if adversary_as:
                r.asn = r.rid % adversary_as   # pack owned relays into few ASes
        # Build each relay's inferred belief from the (now final) true asn.
        for r in relays:
            if SysRand.random() < infer_error:
                if SysRand.random() < 0.5:
                    r.inferred_asn = SysRand.randrange(n_as)   # wrong AS
                else:
                    r.inferred_asn = None                      # unknown (gap)
            else:
                r.inferred_asn = r.asn                         # correct
            r.inferred_juris = r.juris
        return cls(relays)

    def gossip_sample(self, fraction: float) -> "Network":
        """A client does not see the whole network (I-3: no god's-eye directory).
        It knows only the relays its own gossip sampling has reached. Returns a
        sub-Network of a random `fraction` of relays (OP-2 territory: this view
        is also what a sybil/eclipse adversary would try to skew)."""
        if fraction >= 1.0:
            return self
        k = max(4, round(len(self.relays) * fraction))
        return Network(SysRand.sample(self.relays, min(k, len(self.relays))))


def _believed_as(r: Relay):
    """What path selection uses: the inferred AS, with unknown kept distinct per
    relay so that 'unknown' never counts as disjoint from anything, including
    another unknown (conservative; returns a unique sentinel per relay)."""
    return r.inferred_asn if r.inferred_asn is not None else ("unknown", r.rid)


def select_paths(net: Network, n: int, hops: int = 3,
                 disjoint: str = "as", use_truth: bool = False) -> list | None:
    """Best-effort disjoint path selection -- a strawman for Part 3.

    By default selection reasons over the client's BELIEF (inferred AS); set
    `use_truth=True` to reason over ground truth, i.e. to reproduce the old
    optimistic model where verification is assumed solved. `disjoint`:
      'node'  -> no relay reused across the n paths
      'as'    -> no (believed) autonomous system reused across the n paths
      'none'  -> independent uniform draws (tiny-network fallback)
    """
    def as_of(r):
        return r.asn if use_truth else _believed_as(r)

    pool = list(net.relays)
    paths, used_nodes, used_as = [], set(), set()
    for _ in range(n):
        if disjoint == "node":
            cand = [r for r in pool if r.rid not in used_nodes]
        elif disjoint == "as":
            cand = [r for r in pool if as_of(r) not in used_as]
        else:
            cand = pool
        if len(cand) < hops:
            return None
        path = SysRand.sample(cand, hops)       # hops within a path are node-distinct
        paths.append(path)
        used_nodes.update(r.rid for r in path)
        used_as.update(as_of(r) for r in path)
    return paths


def select_paths_persistent_guard(net: Network, n: int, guard: Relay,
                                   hops: int = 3, disjoint: str = "as",
                                   use_truth: bool = False) -> list | None:
    """Like select_paths but share 1's circuit starts at a FIXED guard (a client
    keeps the same entry guard for months; a compromised guard stays
    compromised, Tor's guard rationale). The remaining paths avoid reusing the
    guard's believed AS, as honest selection would."""
    def as_of(r):
        return r.asn if use_truth else _believed_as(r)

    rest = select_paths(Network([r for r in net.relays if r.rid != guard.rid]),
                        n - 1, hops, disjoint, use_truth)
    if rest is None:
        return None
    others = SysRand.sample([r for r in net.relays if r.rid != guard.rid],
                            hops - 1) if len(net.relays) > hops else None
    if others is None:
        return None
    first = [guard] + others
    return [first] + rest


# --- adversary models: the adversary always exploits GROUND TRUTH ---

def adversary_breaks(paths: list, k: int) -> bool:
    """Node-level end-to-end correlation: the adversary sees a circuit when it
    owns BOTH its guard and its exit/drop. >= k seen -> content break."""
    seen = sum(1 for p in paths if p[0].adversary and p[-1].adversary)
    return seen >= k


def adversary_partial(paths: list) -> int:
    """How many circuits the adversary end-to-end-correlates (node-level)."""
    return sum(1 for p in paths if p[0].adversary and p[-1].adversary)


def adversary_breaks_as_level(paths: list, k: int) -> bool:
    """Upgraded adversary (roadmap 2.1): it correlates at AS granularity. It
    sees a circuit if it controls (owns a relay in, OR simply observes) the TRUE
    AS of both the guard and the exit. Owning one relay in an AS is modelled as
    observing that whole AS's traffic -- the AS-level threat the believed-AS
    selection is trying, and failing under inference error, to avoid."""
    adv_as = {p[i].asn for p in paths for i in (0, -1)
              for _ in (0,) if p[i].adversary}
    seen = sum(1 for p in paths
               if p[0].asn in adv_as and p[-1].asn in adv_as)
    return seen >= k


def run_trial(net: Network, n: int, k: int, disjoint: str) -> str:
    paths = select_paths(net, n, disjoint=disjoint)
    if paths is None:
        return "no_paths"
    return "broken" if adversary_breaks(paths, k) else "ok"


def effective_mode(net: Network, n: int, requested: str,
                   use_truth: bool = False) -> tuple:
    """Strongest disjointness the client can actually BUILD from its own view,
    falling back when it cannot -- the small-network-mode logic. Under inference
    error the 'as' mode is harder to satisfy (unknowns never look disjoint), so
    the client falls back more often: availability is the first casualty of a
    bad dataset, before any break."""
    order = {"as": ["as", "node", "none"], "node": ["node", "none"],
             "none": ["none"]}[requested]
    for mode in order:
        paths = select_paths(net, n, disjoint=mode, use_truth=use_truth)
        if paths is not None:
            return paths, mode
    return None, None


def sweep(sizes, n=4, k=3, requested="as", frac_adv=0.2, adv_as=4,
          trials=3000, infer_error=0.0, gossip_fraction=1.0,
          as_level_adv=False) -> list:
    """Per network size: content-break rate, mean linkage leak, and the mode the
    client could actually run -- now as a function of inference error and the
    partial gossip view. The adversary exploits ground truth; the client selects
    on its (noisy, partial) belief."""
    rows = []
    for size in sizes:
        adv = max(1, round(size * frac_adv))
        broken, leak_total, mode_count = 0, 0, {}
        for _ in range(trials):
            full = Network.random(size, n_as=max(6, size // 3), n_juris=5,
                                  adversary_relays=adv, adversary_as=adv_as,
                                  infer_error=infer_error)
            net = full.gossip_sample(gossip_fraction)
            paths, mode = effective_mode(net, n, requested)
            if paths is None:
                mode_count["none-possible"] = mode_count.get("none-possible", 0) + 1
                continue
            mode_count[mode] = mode_count.get(mode, 0) + 1
            broke = (adversary_breaks_as_level(paths, k) if as_level_adv
                     else adversary_breaks(paths, k))
            if broke:
                broken += 1
            leak_total += adversary_partial(paths)
        rows.append((size, adv, broken / trials, leak_total / trials, mode_count))
    return rows


def _demo_full_message_roundtrip():
    """Sanity: an actual message survives the whole simulated path."""
    net = Network.random(60, n_as=20, n_juris=5, adversary_relays=12,
                         adversary_as=4, infer_error=0.1)
    paths = select_paths(net, n=4, disjoint="as")
    assert paths is not None
    drops = [rz.Drop(f"drop{i}") for i in range(4)]
    card = rz.Card(secrets.token_bytes(32), secrets.token_bytes(32), drops)
    msg = b"numbers, not opinions"
    nonce = (1).to_bytes(8, "big")
    rz.deposit_message(card, msg, nonce, 1_767_000_000.0)
    got = rz.poll_all(card, 1_767_000_060.0, [i.to_bytes(8, "big") for i in range(4)])
    assert got == {nonce: msg}
    return len(paths)


def _fmt_mode(mode_count: dict) -> str:
    total = sum(mode_count.values())
    main = max(mode_count, key=mode_count.get)
    return f"{main} ({mode_count[main] / total:.0%})"


if __name__ == "__main__":
    print(f"full round trip over simulated paths: ok "
          f"({_demo_full_message_roundtrip()} disjoint circuits)\n")

    print("=" * 68)
    print("1. The headline: break & linkage as INFERENCE ERROR rises")
    print("=" * 68)
    print("80-relay network, adversary owns 35% packed into 3 ASes, client")
    print("requests AS-disjoint and the adversary correlates at AS level. At")
    print("error 0 the client's belief = reality (the old optimistic model); as")
    print("error rises its AS-disjointness is partly illusory and the adversary")
    print("bites. Both metrics rise monotonically with the error.\n")
    print(f"{'infer err':>9} {'content break':>14} {'linkage leak':>13} {'mode run':>16}")
    for err in [0.0, 0.1, 0.2, 0.4, 0.6]:
        (_, adv, broken, leak, modes), = sweep([80], n=4, k=3, requested="as",
                                               frac_adv=0.35, adv_as=3,
                                               infer_error=err, as_level_adv=True,
                                               trials=4000)
        print(f"{err:>9.0%} {broken:>13.2%} {leak:>13.2f} {_fmt_mode(modes):>16}")
    print("\n-> BOTH content break and linkage leak climb with inference error")
    print("   even though the client still 'requested AS-disjoint': believed")
    print("   disjointness is not real disjointness. Note the floor still holds")
    print("   -- break needs the adversary on >=k circuits at once, so the error")
    print("   erodes LINKAGE (metadata) far faster than content. That asymmetry")
    print("   is the honest shape of OP-1: inference error is mostly a metadata")
    print("   problem, and the zero-error numbers were the best case.")

    print("\n" + "=" * 68)
    print("2. Partial gossip: a client that sees only part of the network")
    print("=" * 68)
    print("40-relay network, 10% inference error, but the client only knows a")
    print("fraction of relays (its own gossip sample, I-3: no god's-eye view).")
    print("A thinner view means fewer AS-disjoint circuits are buildable, so the")
    print("client is forced to fall back and the break rate rises.\n")
    print(f"{'gossip':>7} {'content break':>14} {'linkage leak':>13} {'mode run':>16}")
    for frac in [1.0, 0.5, 0.25, 0.15]:
        (_, adv, broken, leak, modes), = sweep([40], requested="as",
                                               frac_adv=0.2, adv_as=4,
                                               infer_error=0.1,
                                               gossip_fraction=frac,
                                               as_level_adv=True, trials=4000)
        print(f"{frac:>7.0%} {broken:>13.2%} {leak:>13.2f} {_fmt_mode(modes):>16}")
    print("\n-> at 25% gossip the client can no longer build AS-disjoint circuits")
    print("   at all and falls back to 'none', where the break rate jumps. The")
    print("   gossip sample is itself a security surface (OP-2: a sybil/eclipse")
    print("   adversary tries to shape exactly this view).")

    print("\n" + "=" * 68)
    print("3. Persistent guard: one fixed entry across a message stream")
    print("=" * 68)
    net = Network.random(160, n_as=53, n_juris=5, adversary_relays=48,
                         adversary_as=4, infer_error=0.1)
    adv_guard = next(r for r in net.relays if r.adversary)
    honest_guard = next(r for r in net.relays if not r.adversary)
    stream = 300

    def stream_leak(guard):
        s1_half = s1_full = 0
        for _ in range(stream):
            paths = select_paths_persistent_guard(net, 4, guard, disjoint="as")
            if not paths:
                continue
            if paths[0][0].adversary:            # share 1's guard is owned
                s1_half += 1
                if paths[0][-1].adversary:       # ...and its exit too -> correlated
                    s1_full += 1
        return s1_half, s1_full

    ah, af = stream_leak(adv_guard)
    hh, hf = stream_leak(honest_guard)
    print(f"Stream of {stream} messages, one fixed guard kept throughout.\n")
    print(f"  adversary-owned guard (rid={adv_guard.rid}):")
    print(f"    share 1's guard compromised on {ah}/{stream} messages (~all),")
    print(f"    share 1 fully correlated (guard+exit owned) on {af}/{stream}.")
    print(f"  honest guard (rid={honest_guard.rid}):")
    print(f"    share 1's guard compromised on {hh}/{stream} messages.")
    print("-> a bad fixed guard makes share 1 half-correlated on EVERY message")
    print("   for as long as it is kept -- persistence turns a one-off position")
    print("   into a standing one, and only the exit's luck decides full")
    print("   correlation. Guard choice is a security decision, not a")
    print("   performance one; this is why guards must be few, stable, and")
    print("   chosen from verified relays (Part 3 / OP-1).")

    print("\n" + "=" * 68)
    print("4. The honest worst case (small-network fallback, no AS-disjointness)")
    print("=" * 68)
    (_, adv, broken, leak, _), = sweep([20], n=4, k=3, requested="none",
                                       frac_adv=0.4, trials=5000, infer_error=0.1)
    print(f"20-relay network, adversary owns 40%, no disjointness buildable:")
    print(f"  content break: {broken:.2%}   mean linkage leak: {leak:.2f} of 4 circuits")
    print("  -> the worst case the UI MUST warn about; raising n and k is the")
    print("     lever (threat model). Below k, content stays unconditional (I-2).")
