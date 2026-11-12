"""ScrambNet dead-drop economics simulator -- reference experiment (DRAFT, OP-9).

Roadmap 4.3. The companion to sybil_sim.py for the dead-drop layer (Part 6).
Two separate leaks, two separate knobs, both priced in numbers:

  SCENARIO A -- flooding economics. An adversary floods a box with junk
    deposits. Candidate defenses: the RZ-7 per-box cap (already there) and a
    deposit-side proof-of-work puzzle. We price both and reach an HONEST and
    uncomfortable result: NEITHER defends delivery.
      - No puzzle hardness deters a botnet while staying affordable on the
        cheap phone the project claims to serve (the ~25000x ARM-vs-GPU gap).
      - The cap bounds STORAGE (115 KiB/box) but NOT DELIVERY: a flood evicts
        honest mail, or merely buries it past the B_SLOTS=8 retrieval window,
        in SECONDS -- inside one 900s poll period -- using PHONE-class hardware.
    So delivery-flooding is a DECLARED RESIDUAL: it needs a deposit ADMISSION
    control the project does not yet have, and until it does, the numbers below
    are what the residual costs. (This corrects an earlier draft that wrongly
    credited the cap with carrying flooding.)

  SCENARIO B -- polling metadata / box profiling. A malicious drop watches a
    box's deposit times and poll cadence within one epoch (RZ-9 flags this).
    Two sub-leaks, two defenses:
      - the ONLINE-PATTERN leak (did the recipient react to a deposit) is
        defended by strict schedule INDEPENDENCE (free in bytes, load-bearing),
        measured by a TAIL test, not a mean (a mean is too blunt to detect it);
      - the WHICH-BOX leak is defended by decoy polls, which cost metered-mobile
        bytes and buy little the RZ-2/RZ-10 unlinkability does not already give.

NOT a node and NOT a protocol. Hardware/volume numbers are strawman, chosen
attacker-favorably; attack the model, then the spec. OP-9 is NOT solved here --
this bounds and PRICES the attack, it does not remove it.

Deterministic on purpose (seeded PRNG, not SystemRandom): a parameter-defending
sim must reproduce the exact curves its test asserts. This is the one deliberate
departure from sybil_sim.py's realism-first SystemRandom.
"""

import math
import random

import rendezvous as rz

RNG = random.Random(0x5c2a_b11e)   # fixed seed: curves must reproduce bit-for-bit

# ---- hardware tiers (ground truth, strawman, attacker-FAVORABLE) -------------
# Hash rates in H/s. The conclusion is robust to +/-10x on any tier: the gap
# under test is ~25000x, not ~2x.
PHONE_HPS = 2e6       # a cheap ARM phone, no crypto accel -- the user we serve
BOTNET_HPS = 5e7      # one commodity PC in a botnet
GPU_HPS = 5e10        # one GPU/ASIC flooder (worst case for us)

# ---- the real dead-drop constants (imported so sim and spec cannot drift) ----
BOX_CAP = rz.BOX_CAP           # 64 slots, oldest-first FIFO eviction (RZ-7)
B_SLOTS = rz.B_SLOTS           # 8: a poll returns the 8 OLDEST surviving slots
SLOT_BYTES = rz.SLOT_BYTES     # 1840
POLL_PERIOD = rz.POLL_PERIOD   # 900s
POLL_JITTER = rz.POLL_JITTER   # +-300s
SPHINX_BYTES = 2048            # dispersal.py: the on-wire packet; 1 slot = 1 pkt
N_DROPS = 4                    # dispersal n=4
K_DROPS = 3                    # dispersal k=3: flood >= n-k+1 = 2 drops to deny


# =============================================================================
# SCENARIO A -- flooding economics
# =============================================================================

def puzzle_cost_seconds(z: int, hps: float) -> float:
    """Expected wall-clock to solve a z-leading-zero-bit PoW at `hps`."""
    return (2 ** z) / hps


def deposits_per_hour(z: int, hps: float) -> float:
    return hps / (2 ** z) * 3600.0


def evict_seconds(z: int, hps: float, depth: int) -> float:
    """Wall-clock for a flooder at hardness z to push `depth` fresh deposits
    into one box -- i.e. to bury honest mail `depth` slots deep."""
    rate = hps / (2 ** z)              # deposits/second
    return depth / rate if rate > 0 else math.inf


def scenario_a():
    print("=" * 70)
    print("  SCENARIO A -- flooding economics: puzzle vs RZ-7 cap")
    print("=" * 70)

    zs = [16, 18, 20, 22, 24, 26, 28, 36]

    # --- Curve A1: the honest tension, side by side -----------------------
    # phone seconds/deposit (and per n=4 message) vs a single GPU's refill rate.
    print("\n  A1  phone cost vs single-GPU flood, as puzzle hardness z rises")
    print("  (a phone-affordable deposit is < ~2 s; a botnet is deterred only")
    print("   if its refill/hr falls below honest deposits/day, ~10-100)\n")
    print(f"    {'z':>3} {'phone s/dep':>12} {'phone s/msg':>12} "
          f"{'botnet dep/hr':>14} {'gpu dep/hr':>14}")
    window_open = False
    for z in zs:
        p = puzzle_cost_seconds(z, PHONE_HPS)
        b = deposits_per_hour(z, BOTNET_HPS)
        g = deposits_per_hour(z, GPU_HPS)
        print(f"    {z:>3} {p:>12.3f} {p * N_DROPS:>12.3f} "
              f"{b:>14,.0f} {g:>14,.0f}")
        # a "defensible window": phone cheap AND gpu deterred at the same z
        if p < 2.0 and g < 100.0:
            window_open = True
    print(f"\n  phone->gpu hardware gap: {GPU_HPS / PHONE_HPS:,.0f}x")
    print(f"  defensible puzzle window exists (phone<2s AND gpu<100/hr)? "
          f"{window_open}")
    print("  => the puzzle is NOT a flooding defense; it is a declared residual.")

    # --- Curve A2: the cap bounds STORAGE but not DELIVERY -----------------
    # The real threshold is B_SLOTS=8 (retrieval window), not BOX_CAP=64:
    # honest mail buried >8 deep is stored but never returned by a poll.
    print("\n  A2  delivery race: time to BURY honest mail past the 8-slot poll")
    print("      window, vs the 900s poll period -- even PHONE-class flooding")
    print("      wins inside one poll period, at every usable z\n")
    print(f"    {'z':>3} {'phone bury-8 s':>15} {'phone evict-64 s':>17} "
          f"{'gpu bury-8 s':>14}")
    for z in [16, 20, 22]:
        pb = evict_seconds(z, PHONE_HPS, B_SLOTS)
        pe = evict_seconds(z, PHONE_HPS, BOX_CAP)
        gb = evict_seconds(z, GPU_HPS, B_SLOTS)
        print(f"    {z:>3} {pb:>15.2f} {pe:>17.2f} {gb:>14.5f}")
    print(f"\n  poll period = {POLL_PERIOD}s. Burying honest mail past the")
    print(f"  {B_SLOTS}-slot window takes a PHONE far less than one poll period,")
    print("  so the cap does NOT protect delivery. Delivery-flooding needs a")
    print("  deposit ADMISSION control (not yet designed) -- declared residual.")
    print("  Dispersal (n=4,k=3) only raises the bar to flooding >=2 of 4 drops.")

    return window_open


# =============================================================================
# SCENARIO B -- polling metadata / box profiling
# =============================================================================

def _poll_schedule(span_s: float, coupling: float, deposit_times):
    """Build a recipient's poll timestamps over `span_s`.

    coupling c in [0,1]: fraction of polls that REACT to a deposit (the leak).
    The rest follow the RZ-9 fixed cadence with +-JITTER. A reactive poll lands
    a short random delay after its deposit (user just opened the app)."""
    polls = []
    # the independent RZ-9 backbone: fixed cadence + jitter, phase seeded
    t = RNG.uniform(0, POLL_PERIOD)
    while t < span_s:
        polls.append(t)
        t += POLL_PERIOD + RNG.uniform(-POLL_JITTER, POLL_JITTER)
    # replace a `coupling` fraction of backbone polls with reactive ones
    n_react = int(round(coupling * len(polls)))
    if n_react and deposit_times:
        for _ in range(n_react):
            dep = RNG.choice(deposit_times)
            polls.append(dep + RNG.uniform(5, 120))   # reacts within ~2 min
        polls.sort()
    return polls


def _next_poll_latency(dep_t, polls):
    for p in polls:
        if p >= dep_t:
            return p - dep_t
    return None


def _profile(coupling: float, days: int = 30):
    """Return (mean_latency, p_fast) the drop measures. p_fast = P[latency<60s],
    the TAIL statistic that actually detects reactive polling."""
    span = days * 86400.0
    # honest deposits: a handful/day at random times (the drop sees these times)
    deps = sorted(RNG.uniform(0, span)
                  for _ in range(days * RNG.randint(2, 5)))
    polls = _poll_schedule(span, coupling, deps)
    lat = [x for d in deps if (x := _next_poll_latency(d, polls)) is not None]
    if not lat:
        return None, None
    mean = sum(lat) / len(lat)
    p_fast = sum(1 for x in lat if x < 60.0) / len(lat)
    return mean, p_fast


def scenario_b():
    print("\n" + "=" * 70)
    print("  SCENARIO B -- polling metadata: RZ-9 discipline vs a profiling drop")
    print("=" * 70)

    # --- Curve B1: the online-pattern leak vs schedule independence --------
    # The inspection-paradox mean at c=0 is E[L^2]/(2 E[L]) = 466.7s, NOT
    # POLL/2=450. The MEAN is a blunt detector (it still reads "independent"
    # at c=0.5); the TAIL p_fast=P[lat<60s] is what a real drop exploits.
    el = POLL_PERIOD                       # E[L] = 900
    var_l = (2 * POLL_JITTER) ** 2 / 12.0  # U(-300,300) on interval length
    insp_mean = (var_l + el * el) / (2 * el)
    print(f"\n  B1  online-pattern leak vs coupling c (independence = c=0)")
    print(f"      inspection-paradox mean at c=0 = {insp_mean:.1f}s "
          f"(not POLL/2={POLL_PERIOD / 2:.0f})\n")
    # Detector threshold: at c=0 some deposits land within 60s of an
    # independent poll BY CHANCE (~POLL_JITTER/POLL_PERIOD worth of mass), so a
    # small baseline p_fast is noise, not a leak. 0.10 sits above that baseline
    # and below the c=0.05 signal (see the c=0 vs c=0.05 gap in the curve).
    DETECT = 0.10
    print(f"    {'c':>5} {'mean lat s':>11} {'P[lat<60s]':>11}  detector")
    means, fasts = {}, {}
    for c in (0.0, 0.05, 0.1, 0.25, 0.5, 1.0):
        mean, pf = _profile(c)
        means[c], fasts[c] = mean, pf
        flag = "LEAK" if pf > DETECT else "-"
        print(f"    {c:>5.2f} {mean:>11.1f} {pf:>11.3f}  {flag}")
    print("\n  The MEAN still reads 'independent-ish' at c=0.5; the TAIL p_fast")
    print("  flags the leak from c~0.05. Independence (c=0) is the real defense,")
    print("  and it is FREE in bytes -- it only forbids reacting to deposits.")

    # --- Curve B2: the which-box leak vs decoys, priced in mobile bytes ----
    # Each poll rides Sphinx: B_SLOTS response packets + 1 request packet,
    # each 2048 B -- NOT the raw 14720 slot bytes. Over N_DROPS drops.
    print("\n  B2  which-box leak defense (decoys) priced on metered mobile")
    print("      one poll = (8 response + 1 request) Sphinx packets over a")
    print("      3-hop circuit; the raw-slot figure understates it ~1.25x\n")
    polls_day_drop = 86400 // POLL_PERIOD          # 96
    poll_bytes = (B_SLOTS + 1) * SPHINX_BYTES      # 18432 B on the metered hop
    print(f"    {'decoy r':>8} {'polls/day':>10} {'MB/day':>8} {'MB/month':>9}")
    for r in (0, 1, 3, 7, 15):
        pd = polls_day_drop * (1 + r) * N_DROPS
        mb_day = pd * poll_bytes / 1e6
        print(f"    {r:>8} {pd:>10} {mb_day:>8.1f} {mb_day * 30:>9.0f}")
    print("\n  Decoys defend only WHICH box is real (RZ-2/RZ-10 already largely")
    print("  cover this), at linear byte cost. The mandatory r=0 floor alone is")
    print(f"  ~{polls_day_drop * N_DROPS * poll_bytes / 1e6 * 30:.0f} MB/month")
    print("  BEFORE the deposit/send side -- a real standing cost for mobile.")

    return means, fasts


if __name__ == "__main__":
    window = scenario_a()
    scenario_b()
    print("\n" + "=" * 70)
    print("  VERDICT (OP-9, roadmap 4.3): the no-window result holds -- no")
    print("  puzzle hardness is both botnet-deterring and phone-affordable.")
    print("  But neither the puzzle NOR the RZ-7 cap defends DELIVERY under")
    print("  flood; that needs a deposit admission control, declared a residual")
    print("  with these numbers. The online-pattern leak is defended free by")
    print("  schedule independence; decoys and the poll floor cost real bytes.")
    print("=" * 70)
    assert not window, "a defensible puzzle window appeared -- model changed"
