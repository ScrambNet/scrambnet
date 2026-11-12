"""Locks the load-bearing numbers of dropecon_sim.py (roadmap 4.3, OP-9).

These asserts ARE the defended-parameters result: if the model changes, the
test fails and the spec's numbers must be re-derived. Each test encodes a
red-team finding that was verified against the real rendezvous.py constants.
"""

import unittest

import dropecon_sim as sim


class FloodingEconomics(unittest.TestCase):
    def test_no_defensible_puzzle_window(self):
        """A: no hardness z is both phone-affordable (<2s) AND botnet-deterring
        (gpu refill/hr below any plausible honest deposits/day). The empty
        window IS the result."""
        window = False
        for z in range(10, 48):
            phone = sim.puzzle_cost_seconds(z, sim.PHONE_HPS)
            gpu_hr = sim.deposits_per_hour(z, sim.GPU_HPS)
            if phone < 2.0 and gpu_hr < 100.0:
                window = True
        self.assertFalse(window, "a phone-affordable, botnet-deterring z appeared")

    def test_phone_affordable_band_prices_out_before_deterring(self):
        """The phone-affordable band (z<=20, <2s/dep) leaves the GPU refilling
        astronomically -- quantifies WHY the window is empty."""
        # z=20 is the last phone-affordable point...
        self.assertLess(sim.puzzle_cost_seconds(20, sim.PHONE_HPS), 2.0)
        # ...and there the GPU still refills a box >1e8 times/hour.
        self.assertGreater(sim.deposits_per_hour(20, sim.GPU_HPS), 1e8)

    def test_cap_does_not_protect_delivery(self):
        """B1 (the corrected central claim): even PHONE-class flooding buries
        honest mail past the B_SLOTS=8 retrieval window well inside one 900s
        poll period, at every usable hardness. The cap bounds storage, not
        delivery."""
        for z in (16, 18, 20, 22):
            bury8 = sim.evict_seconds(z, sim.PHONE_HPS, sim.B_SLOTS)
            self.assertLess(
                bury8, sim.POLL_PERIOD,
                f"at z={z} a phone cannot bury honest mail within a poll period")
        # a GPU does it in well under a second at the hardest phone-affordable z
        self.assertLess(sim.evict_seconds(20, sim.GPU_HPS, sim.B_SLOTS), 1.0)

    def test_gpu_botnet_ratio_is_the_hardware_ratio(self):
        """Sanity against the earlier off-by-140x bug: the gpu/botnet refill
        ratio must equal the hardware ratio (1000x) exactly, at any z."""
        for z in (16, 22, 28):
            g = sim.deposits_per_hour(z, sim.GPU_HPS)
            b = sim.deposits_per_hour(z, sim.BOTNET_HPS)
            self.assertAlmostEqual(g / b, sim.GPU_HPS / sim.BOTNET_HPS, places=6)


class PollingMetadata(unittest.TestCase):
    def test_independence_is_clean_coupling_leaks(self):
        """B: strict independence (c=0) is statistically clean on the TAIL
        statistic a drop exploits, while any coupling from c=0.05 leaks. A mean
        test would miss this -- that is why we assert on p_fast."""
        _, pf0 = sim._profile(0.0)
        _, pf5 = sim._profile(0.05)
        self.assertLess(pf0, 0.10, "c=0 should look independent on the tail")
        self.assertGreater(pf5, 0.10, "c=0.05 reactive polling should be caught")
        self.assertGreater(pf5, pf0 * 3, "the leak must dominate the baseline")

    def test_mean_is_a_blunt_detector(self):
        """The red-team point: the MEAN alone passes weakly-coupled schedules.
        At c=0.05 the tail already screams leak while the mean is still a large
        fraction of the c=0 baseline -- proving the mean must NOT be the
        detector (a mean-band test centred near POLL/2 would pass c=0.05)."""
        mean0, _ = sim._profile(0.0)
        mean5, pf5 = sim._profile(0.05)
        # the tail catches c=0.05 hard...
        self.assertGreater(pf5, 0.10, "tail must flag c=0.05 (sharp)")
        # ...while the mean has moved only partway from the c=0 baseline, i.e.
        # a mean test would still rate c=0.05 as near-independent (blunt).
        self.assertGreater(mean5, 0.20 * mean0,
                           "mean still a large fraction of baseline at c=0.05")

    def test_independence_mean_is_inspection_paradox(self):
        """At c=0 the mean deposit->poll latency is the renewal/inspection
        value E[L^2]/(2E[L])=466.7s, not POLL/2=450 -- within sampling noise."""
        mean0, _ = sim._profile(0.0)
        self.assertGreater(mean0, sim.POLL_PERIOD / 2 - sim.POLL_JITTER)
        self.assertLess(mean0, sim.POLL_PERIOD / 2 + sim.POLL_JITTER)


if __name__ == "__main__":
    unittest.main()
