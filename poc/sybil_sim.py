"""ScrambNet sybil / eclipse simulator -- reference experiment (DRAFT, OP-2).

The companion to network_sim.py for the OTHER half of the discovery problem.
network_sim.py asks "are the n chosen paths really disjoint?" (OP-1). This file
asks "is the client's VIEW of the network -- its gossip sample -- itself honest,
or has a sybil/eclipse adversary shaped it?" (OP-2, roadmap 2.4).

It turns the Part 2 defenses into numbers:
  - GR-8 source mixing: the stored sample mixes independent source CLASSES
    (social-graph bridge, gossip exchange, direct probing) and no class may
    exceed a fraction f of the sample. We measure the eclipse probability as a
    function of f and how many classes the adversary controls.
  - GR-9 / PS-10 "count only verified": identities are free, so a sybil inflates
    the RAW record count arbitrarily, but cannot inflate VERIFIED bandwidth it
    does not have. We measure what "count only verified" actually buys.

NOT a node and NOT a protocol. Numbers are strawman; attack the model, then the
spec. OP-2 is NOT solved here -- this bounds the attack, it does not remove it.
"""

import secrets
import statistics
from dataclasses import dataclass, field

SR = secrets.SystemRandom()

# The independent source classes a sample mixes (GR-8). Strawman set of 3.
CLASSES = ("bridge", "gossip", "probe")


@dataclass
class Record:
    rid: int
    sybil: bool                 # a free fake identity (GR-9): cheap, unlimited
    source: str                 # which class delivered it (GR-8)
    true_bw: float              # real forwarding capacity (0 for a sybil shell)
    # A sybil can CLAIM any bandwidth; verified_bw is what a probe (GR-7)
    # actually measured. A sybil's verified_bw is ~0 because it has no capacity.
    claimed_bw: float = 0.0
    verified_bw: float = 0.0


def make_population(n_honest: int, n_sybil: int,
                    adversary_classes: tuple = ()) -> list:
    """A record population the client might sample from.

    Honest relays carry real bandwidth and arrive over any class. Sybils are
    free fakes (GR-9) that CLAIM bandwidth but have none; an adversary that owns
    a source CLASS can stuff that class with its sybils (the eclipse lever).
    """
    recs = []
    rid = 0
    # A class the adversary CONTROLS delivers only adversary records -- honest
    # relays do not reach the client through a class the adversary owns. So
    # honest relays arrive only over the NON-controlled classes.
    honest_classes = [c for c in CLASSES if c not in adversary_classes] or list(CLASSES)
    for _ in range(n_honest):
        bw = SR.uniform(1, 10)
        recs.append(Record(rid, sybil=False, source=SR.choice(honest_classes),
                            true_bw=bw, claimed_bw=bw, verified_bw=bw))
        rid += 1
    for _ in range(n_sybil):
        # a sybil claims a big bandwidth but verification finds ~nothing; it
        # arrives over a class the adversary controls (or any, if none specified)
        src = SR.choice(adversary_classes) if adversary_classes else SR.choice(CLASSES)
        recs.append(Record(rid, sybil=True, source=src,
                            true_bw=0.0, claimed_bw=SR.uniform(5, 10),
                            verified_bw=SR.uniform(0.0, 0.2)))
        rid += 1
    return recs


def sample_with_gr8(pop: list, size: int, cap_fraction: float) -> list:
    """GR-8: draw a stored sample that mixes classes, with NO class exceeding
    `cap_fraction` of the sample. Returns the sampled records.

    Without the cap a single flooded class dominates the sample; the cap forces
    the adversary to own MULTIPLE classes to dominate, which is the whole point.
    """
    per_class_cap = max(1, int(cap_fraction * size))
    by_class = {c: [r for r in pop if r.source == c] for c in CLASSES}
    out = []
    # round-robin across classes, each capped, until we have `size` or run dry
    for c in CLASSES:
        take = min(per_class_cap, len(by_class[c]))
        out += SR.sample(by_class[c], take)
    # if under size (some classes thin), top up from the remainder, still
    # respecting that we never exceed the cap per class (already enforced above)
    return out[:size]


def eclipsed(sample: list, honest_needed: int = 1) -> bool:
    """A client is 'eclipsed' for a decision if its sample contains fewer than
    `honest_needed` honest (non-sybil, real-bandwidth) records to choose from --
    the adversary has crowded the honest relays out of the client's view."""
    honest = sum(1 for r in sample if not r.sybil)
    return honest < honest_needed


def verified_fraction(sample: list, bw_threshold: float = 0.5) -> float:
    """PS-10 / GR-9: the fraction of the sample that survives 'count only
    independently verified'. A sybil's verified_bw is ~0, so it is counted out;
    an honest relay's probe (GR-7) confirms its capacity."""
    if not sample:
        return 0.0
    verified = sum(1 for r in sample if r.verified_bw >= bw_threshold)
    return verified / len(sample)


# --- experiments: the curves roadmap 2.4 asks for ---

def eclipse_curve(cap_fractions, adversary_class_counts,
                  n_honest=50, sybil_per_class=100, sample_size=30,
                  trials=300) -> dict:
    """Eclipse probability as a function of the GR-8 per-class cap and how many
    of the 3 classes the adversary controls (stuffs with sybils)."""
    rows = {}
    for n_adv_classes in adversary_class_counts:
        adv_classes = CLASSES[:n_adv_classes]
        for f in cap_fractions:
            ecl = 0
            for _ in range(trials):
                n_sybil = sybil_per_class * max(1, n_adv_classes)
                pop = make_population(n_honest, n_sybil, adv_classes)
                sample = sample_with_gr8(pop, sample_size, f)
                if eclipsed(sample, honest_needed=4):   # need >=4 for n=4 paths
                    ecl += 1
            rows[(n_adv_classes, f)] = ecl / trials
    return rows


def sybil_inflation(sybil_multipliers, n_honest=40, sample_size=30,
                    trials=300) -> dict:
    """What 'count only verified' (PS-10) buys: the adversary's share of the
    sample by RAW count vs by VERIFIED count, as it adds more sybils."""
    rows = {}
    for mult in sybil_multipliers:
        n_sybil = int(n_honest * mult)
        raw_share, ver_share = [], []
        for _ in range(trials):
            pop = make_population(n_honest, n_sybil)
            sample = sample_with_gr8(pop, sample_size, cap_fraction=0.5)
            if not sample:
                continue
            raw = sum(1 for r in sample if r.sybil) / len(sample)
            # verified count: sybils have verified_bw ~0, filtered out
            ver_pool = [r for r in sample if r.verified_bw >= 0.5]
            ver = (sum(1 for r in ver_pool if r.sybil) / len(ver_pool)
                   if ver_pool else 0.0)
            raw_share.append(raw)
            ver_share.append(ver)
        rows[mult] = (statistics.mean(raw_share), statistics.mean(ver_share))
    return rows


def churn_curve(churn_rates, adversary_class_count=2, cap_fraction=0.5,
                rounds=8, n_honest=50, sybil_per_class=100, sample_size=30,
                trials=300) -> dict:
    """The 'detect, make permanent eclipse costly' claim is a RATE (GR-19a/§7).
    A client re-samples each round; with churn probability `c` a controlled
    class is, this round, repopulated from the honest pool (the adversary cannot
    hold every class forever). We measure the probability a client stays
    eclipsed across ALL `rounds` -- persistent eclipse -- as a function of `c`.
    Higher churn => an honest vantage is reached sooner => persistent eclipse
    becomes exponentially less likely. This does NOT cover first-contact
    eclipse (a client with no honest vantage ever), the declared OP-2 residual.
    """
    rows = {}
    adv_classes = CLASSES[:adversary_class_count]
    for c in churn_rates:
        persistent = 0
        for _ in range(trials):
            eclipsed_every_round = True
            for _r in range(rounds):
                # each round, each adversary class churns to honest with prob c
                live_adv = tuple(cl for cl in adv_classes if SR.random() > c)
                pop = make_population(n_honest,
                                     sybil_per_class * max(1, len(live_adv)),
                                     live_adv)
                sample = sample_with_gr8(pop, sample_size, cap_fraction)
                if not eclipsed(sample, honest_needed=4):
                    eclipsed_every_round = False
                    break
            if eclipsed_every_round:
                persistent += 1
        rows[c] = persistent / trials
    return rows


if __name__ == "__main__":
    print("=" * 68)
    print("1. Eclipse probability vs the GR-8 per-class cap f")
    print("=" * 68)
    print("A client needs >=4 honest records in its sample to build 4 paths.")
    print("The adversary floods the classes it controls with free sybils (GR-9).")
    print("GR-8 caps each class at fraction f of the sample, so the adversary")
    print("must own MORE classes to eclipse as f shrinks.\n")
    caps = [0.9, 0.5, 0.34, 0.25]
    rows = eclipse_curve(caps, adversary_class_counts=[1, 2, 3])
    print(f"{'adv classes':>12} " + " ".join(f"f={f:<5}" for f in caps))
    for nac in [1, 2, 3]:
        cells = " ".join(f"{rows[(nac,f)]:6.1%}" for f in caps)
        print(f"{nac:>12}  {cells}")
    print("\n-> owning 1 of 3 classes never eclipses once f<=1/2 (the cap keeps")
    print("   2 honest classes in the sample). Owning ALL 3 classes eclipses")
    print("   regardless of f -- source mixing assumes the classes are")
    print("   INDEPENDENT; an adversary who controls every class breaks that")
    print("   assumption, and that is the declared OP-2 residual.")

    print("\n" + "=" * 68)
    print("2. Sybil inflation: what 'count only verified' (PS-10) buys")
    print("=" * 68)
    print("Identities are free (GR-9), so sybils inflate the RAW sample share")
    print("arbitrarily. But a sybil has no real bandwidth, so a probe (GR-7)")
    print("verifies ~nothing, and 'count only verified' discounts it.\n")
    mults = [1, 3, 10, 50]
    sr = sybil_inflation(mults)
    print(f"{'sybils/honest':>13} {'raw share':>12} {'verified share':>16}")
    for m in mults:
        raw, ver = sr[m]
        print(f"{m:>13} {raw:>11.1%} {ver:>15.1%}")
    print("\n-> raw sybil share climbs toward 100% as the adversary adds free")
    print("   identities; the VERIFIED share stays near 0, because verification")
    print("   measures bandwidth a sybil does not have (GR-9/PS-10). 'Count only")
    print("   verified' converts a free attack into one that costs REAL")
    print("   bandwidth -- a real, expensive adversary, not a sybil (accepted).")

    print("\n" + "=" * 68)
    print("3. Churn: persistent eclipse is a RATE, not a state")
    print("=" * 68)
    print("An adversary owning 2 of 3 classes can eclipse a sample NOW, but it")
    print("cannot hold every class forever. Each round a controlled class churns")
    print("back to the honest pool with probability c; we measure the chance a")
    print("client stays eclipsed across 8 rounds.\n")
    cr = churn_curve([0.0, 0.1, 0.25, 0.5])
    print(f"{'churn rate c':>13} {'persistent-eclipse prob':>24}")
    for c in (0.0, 0.1, 0.25, 0.5):
        print(f"{c:>13} {cr[c]:>23.1%}")
    print("\n-> at c=0 the adversary holds the eclipse; even modest churn collapses")
    print("   persistent eclipse fast (an honest vantage is reached within a few")
    print("   rounds). This is the 'detect, make permanent eclipse costly' claim,")
    print("   as a number. It does NOT cover a client eclipsed from first contact")
    print("   -- that has no honest vantage ever, the declared OP-2 residual.")

    print("\n" + "=" * 68)
    print("4. The honest residual (OP-2 is NOT solved)")
    print("=" * 68)
    print("Source mixing bounds eclipse ONLY while the classes are independent;")
    print("verification bounds sybil ONLY down to the cost of real bandwidth.")
    print("No overlay-only mechanism makes gossip sampling fully sybil/eclipse-")
    print("proof without the central allocator I-3 forbids. This file measures")
    print("the bounds; it does not claim to remove the attack.")
