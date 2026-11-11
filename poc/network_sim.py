"""ScrambNet network simulator -- reference experiment (DRAFT).

An in-process model of the whole path: a population of relays across ASes and
jurisdictions, best-effort disjoint path selection, k-of-n dispersal over those
paths (dispersal.py), delivery to dispersed drops (rendezvous.py), and a
k-path adversary that owns a fraction of positions and tries to correlate.

This is NOT a node and NOT a protocol implementation: it is the apparatus that
turns the open questions of issues #2, #4 and #10 into numbers. It models what
an adversary *observes* (which relays a share's circuit touches, who holds a
drop), not real packets -- Sphinx already guarantees the on-wire indistinguish-
ability (see dispersal.py); here we measure the topology-and-selection layer
the spec leaves to Part 3.

Deliberately simple and readable over fast or clever. Numbers are strawman and
meant to be argued with on the issues.

What a trial models (one message, n=4 shares, k=3 to reconstruct):

    sender                                         drops (one share each)
      |  share 1 --[ guard ]--[ mid ]--[ exit ]-->  box 1  \
      |  share 2 --[ guard ]--[ mid ]--[ exit ]-->  box 2   |  recipient
      |  share 3 --[ guard ]--[ mid ]--[ exit ]-->  box 3   |  polls, takes
      |  share 4 --[ guard ]--[ mid ]--[ exit ]-->  box 4  /   any 3, rebuilds

    The adversary owns some relays. It "sees" a circuit when it owns BOTH its
    guard and its exit (end-to-end correlation). Count seen circuits:
        seen >= k  ->  content break   (holds >= k shares AND links them)
        seen <  k  ->  content safe (I-2), but each seen circuit still leaks
                       that *some* flow ran -> linkage/metadata loss
    Disjoint path selection keeps the adversary's relays (and whole ASes) from
    landing on many circuits at once. That is the Part-3 lever this file meters.
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
    asn: int                 # autonomous system (a disjointness axis, OP-1)
    juris: str               # jurisdiction (another axis)
    adversary: bool = False  # owned by the k-path adversary?


@dataclass
class Network:
    relays: list = field(default_factory=list)

    @classmethod
    def random(cls, n_relays: int, n_as: int, n_juris: int,
               adversary_relays: int = 0, adversary_as: int = 0):
        """Build a relay population. The adversary can own relays spread as it
        likes; `adversary_as` concentrates them into few ASes, the cheap way to
        sit on many AS-disjoint paths at once (the real k-path threat)."""
        jurises = [chr(ord("A") + i) for i in range(n_juris)]
        relays = []
        for i in range(n_relays):
            relays.append(Relay(i, asn=i % n_as, juris=SysRand.choice(jurises)))
        owned = SysRand.sample(relays, min(adversary_relays, n_relays))
        for r in owned:
            r.adversary = True
            if adversary_as:
                r.asn = r.rid % adversary_as   # pack owned relays into few ASes
        return cls(relays)


def select_paths(net: Network, n: int, hops: int = 3,
                 disjoint: str = "as") -> list | None:
    """Best-effort disjoint path selection -- a strawman for Part 3.

    Returns n paths of `hops` relays each, or None if the network cannot supply
    them under the requested disjointness. `disjoint`:
      'node'  -> no relay reused across the n paths
      'as'    -> no autonomous system reused across the n paths (stronger)
      'none'  -> independent uniform draws (what a tiny network falls back to)
    This is exactly the knob the 'small-network mode' proposal turns down.
    """
    pool = list(net.relays)
    paths, used_nodes, used_as = [], set(), set()
    for _ in range(n):
        if disjoint == "node":
            cand = [r for r in pool if r.rid not in used_nodes]
        elif disjoint == "as":
            cand = [r for r in pool if r.asn not in used_as]
        else:
            cand = pool
        if len(cand) < hops:
            return None
        # within one path, hops are always node-distinct
        path = SysRand.sample(cand, hops)
        paths.append(path)
        used_nodes.update(r.rid for r in path)
        used_as.update(r.asn for r in path)
    return paths


def adversary_breaks(paths: list, k: int) -> bool:
    """The designed residual risk, made countable.

    A share's circuit is 'seen' if the adversary owns both its entry (guard)
    and its exit/drop -- the classic end-to-end correlation position. With k or
    more share-circuits seen at once, the adversary links the message (and holds
    >= k shares). Below k, dispersal's unconditional floor stands untouched.
    """
    seen = sum(1 for p in paths if p[0].adversary and p[-1].adversary)
    return seen >= k


def adversary_partial(paths: list) -> int:
    """How many of the n share-circuits the adversary end-to-end-correlates.
    Even below k (no content), each seen circuit is a linkage leak: the
    adversary learns *some* flow ran to a drop. This is the metadata loss the
    threat model admits dispersal narrows but does not nullify."""
    return sum(1 for p in paths if p[0].adversary and p[-1].adversary)


def run_trial(net: Network, n: int, k: int, disjoint: str) -> str:
    paths = select_paths(net, n, disjoint=disjoint)
    if paths is None:
        return "no_paths"                       # network too small for the mode
    return "broken" if adversary_breaks(paths, k) else "ok"


def effective_mode(net: Network, n: int, requested: str) -> tuple:
    """A client asks for the strongest disjointness it can actually build and
    falls back when the network is too small -- the small-network-mode logic.
    Returns (paths, mode_used)."""
    order = {"as": ["as", "node", "none"], "node": ["node", "none"],
             "none": ["none"]}[requested]
    for mode in order:
        paths = select_paths(net, n, disjoint=mode)
        if paths is not None:
            return paths, mode
    return None, None


def sweep(sizes, n=4, k=3, requested="as", frac_adv=0.2, adv_as=4,
          trials=3000) -> list:
    """Per network size: how often the adversary breaks content (>=k circuits),
    the mean number of share-circuits it correlates (linkage leak), and which
    disjointness mode the client could actually run. Fraction of adversary
    relays is held fixed -- this is the curve issue #4 asks for."""
    rows = []
    for size in sizes:
        adv = max(1, round(size * frac_adv))
        broken, leak_total, mode_count = 0, 0, {}
        for _ in range(trials):
            net = Network.random(size, n_as=max(6, size // 3), n_juris=5,
                                  adversary_relays=adv, adversary_as=adv_as)
            paths, mode = effective_mode(net, n, requested)
            if paths is None:
                mode_count["none-possible"] = mode_count.get("none-possible", 0) + 1
                continue
            mode_count[mode] = mode_count.get(mode, 0) + 1
            if adversary_breaks(paths, k):
                broken += 1
            leak_total += adversary_partial(paths)
        rows.append((size, adv, broken / trials, leak_total / trials, mode_count))
    return rows


def _demo_full_message_roundtrip():
    """Sanity: an actual message survives the whole simulated path once we
    have viable disjoint circuits, losing n-k shares to adversary-dropped
    circuits."""
    net = Network.random(60, n_as=20, n_juris=5, adversary_relays=12, adversary_as=4)
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

    print("k-path adversary vs network size (n=4, k=3; adversary owns 20% of")
    print("relays, packed into 4 ASes; client requests AS-disjoint, falls back)\n")
    print(f"{'relays':>7} {'adv':>4} {'content break':>14} {'linkage leak':>13} {'mode run':>14}")
    print(f"{'':>7} {'':>4} {'(>= k circuits)':>14} {'(of 4 circ.)':>13} {'(most common)':>14}")
    for size in [12, 20, 40, 80, 160, 320]:
        (_, adv, broken, leak, modes), = sweep([size], requested="as")
        print(f"{size:>7} {adv:>4} {broken:>13.2%} {leak:>13.2f} {_fmt_mode(modes):>14}")

    print("\nThe adversary that actually bites: no AS-disjointness available")
    print("(small-network fallback), adversary owns 40% of a 20-relay network\n")
    (_, adv, broken, leak, _), = sweep([20], n=4, k=3, requested="none",
                                       frac_adv=0.4, trials=5000)
    print(f"  content break: {broken:.2%}   mean linkage leak: {leak:.2f} of 4 circuits")
    print("  -> this is the honest worst case the UI must warn about, and the")
    print("     reason raising n and k 'to taste' is a real lever (threat model).")

    print("\nReading:")
    print("- Content (>= k shares): the unconditional floor means a content")
    print("  break needs the adversary on BOTH ends of >= 3 of the 4 circuits")
    print("  at once -- rare, and it vanishes as AS-disjoint selection becomes")
    print("  buildable. Below that, content stays unconditionally safe (I-2).")
    print("- Linkage (metadata): what the threat model admits dispersal narrows")
    print("  but never nullifies -- it falls with size but is nonzero, and")
    print("  worst on the tiny network that cannot build AS-disjoint circuits.")
    print("- Mode: a 12-20 relay network simply CANNOT run AS-disjoint; it")
    print("  falls back, and the client must say so (small-network mode, #4).")
