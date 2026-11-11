"""Tests for the sybil/eclipse simulator (OP-2, roadmap 2.4).
Run: python3 test_sybil_sim.py

These pin the two bounds the design (Part 2 GR-11..GR-20a) rests on: source
mixing makes eclipse structurally impossible below a controlled-class threshold,
and 'count only verified' makes sybil inflation worthless. OP-2 is NOT solved;
these are the bounds, not a cure."""

import unittest

import sybil_sim as ss


class EclipseBound(unittest.TestCase):
    def test_one_controlled_class_never_eclipses_at_half_cap(self):
        """GR-19 bound: with the per-class cap f<=1/2, an adversary owning ONE
        of the three classes can never eclipse -- the cap keeps the other two
        (honest) classes in every sample."""
        rows = ss.eclipse_curve([0.5, 0.34, 0.25], adversary_class_counts=[1],
                                trials=300)
        for f in (0.5, 0.34, 0.25):
            self.assertEqual(rows[(1, f)], 0.0,
                             f"one class eclipsed at f={f}")

    def test_all_classes_controlled_can_eclipse(self):
        """The declared residual: owning ALL classes breaks the independence
        assumption source-mixing rests on, and eclipse becomes possible."""
        rows = ss.eclipse_curve([0.25], adversary_class_counts=[3], trials=300)
        self.assertGreater(rows[(3, 0.25)], 0.0)

    def test_eclipse_needs_more_classes_as_cap_shrinks(self):
        """A smaller cap forces the adversary to own more classes: owning 1
        class is harmless at every cap, which is the monotone direction that
        matters (A <= min(1, a*f), so a=1 gives <= f but the two honest classes
        still satisfy the honest-needed floor)."""
        rows = ss.eclipse_curve([0.5, 0.25], adversary_class_counts=[1],
                                trials=300)
        self.assertEqual(rows[(1, 0.5)], 0.0)
        self.assertEqual(rows[(1, 0.25)], 0.0)


class Churn(unittest.TestCase):
    def test_churn_collapses_persistent_eclipse(self):
        """GR-19a/§7: persistent eclipse is a rate. With no churn the adversary
        holds the eclipse; modest churn makes staying eclipsed across rounds
        exponentially unlikely (an honest vantage is reached)."""
        rows = ss.churn_curve([0.0, 0.25, 0.5], trials=300)
        self.assertGreater(rows[0.0], rows[0.25])     # churn helps
        self.assertGreater(rows[0.25], rows[0.5])
        self.assertLess(rows[0.5], 0.2)               # strong churn ~ frees it


class SybilInflation(unittest.TestCase):
    def test_verified_share_stays_near_zero_under_inflation(self):
        """GR-20 / PS-10: raw sybil share climbs toward 1 as free identities are
        added, but the VERIFIED share stays ~0 because a sybil has no bandwidth a
        probe can confirm."""
        rows = ss.sybil_inflation([1, 10, 50], trials=300)
        for mult in (1, 10, 50):
            raw, ver = rows[mult]
            self.assertLess(ver, 0.05, f"verified share leaked at {mult}x sybils")
        # and the raw share does climb (the attack is real on raw count)
        self.assertGreater(rows[50][0], rows[1][0])

    def test_sybil_has_no_verified_bandwidth(self):
        pop = ss.make_population(n_honest=20, n_sybil=80)
        sybils = [r for r in pop if r.sybil]
        honest = [r for r in pop if not r.sybil]
        self.assertTrue(all(r.verified_bw < 0.5 for r in sybils))
        self.assertTrue(all(r.verified_bw >= 0.5 for r in honest))


class SourceMixing(unittest.TestCase):
    def test_sample_respects_per_class_cap(self):
        pop = ss.make_population(n_honest=120, n_sybil=0)
        sample = ss.sample_with_gr8(pop, size=30, cap_fraction=0.5)
        from collections import Counter
        counts = Counter(r.source for r in sample)
        cap = int(0.5 * 30)
        for c, k in counts.items():
            self.assertLessEqual(k, cap, f"class {c} exceeded the cap")


if __name__ == "__main__":
    unittest.main(verbosity=2)
