"""Tests for the network simulator realism pass (roadmap 2.1).
Run: python3 test_network_sim.py

These lock the properties the experiment's conclusions depend on: that
selection reasons over the client's BELIEF while the adversary exploits GROUND
TRUTH, that inference error degrades REAL disjointness even when believed
disjointness holds, and that the AS-level adversary dominates the node-level
one. Statistical checks use generous margins."""

import secrets
import unittest

import network_sim as ns

SR = secrets.SystemRandom()


class InferenceLayer(unittest.TestCase):
    def test_zero_error_belief_equals_truth(self):
        net = ns.Network.random(60, n_as=20, n_juris=5, infer_error=0.0)
        for r in net.relays:
            self.assertEqual(r.inferred_asn, r.asn)   # belief == reality

    def test_error_introduces_wrong_or_unknown(self):
        net = ns.Network.random(400, n_as=30, n_juris=5, infer_error=0.5)
        wrong = sum(1 for r in net.relays
                    if r.inferred_asn is not None and r.inferred_asn != r.asn)
        unknown = sum(1 for r in net.relays if r.inferred_asn is None)
        # ~50% corrupted, split between wrong-AS and unknown; both must occur.
        self.assertGreater(wrong, 20)
        self.assertGreater(unknown, 20)
        self.assertLess(wrong + unknown, len(net.relays))   # some stay correct

    def test_unknown_never_counts_as_disjoint(self):
        # Two relays both 'unknown' must get distinct believed-AS sentinels,
        # so selection never treats one unknown as disjoint from another.
        a = ns.Relay(1, asn=5, juris="A", inferred_asn=None)
        b = ns.Relay(2, asn=9, juris="B", inferred_asn=None)
        self.assertNotEqual(ns._believed_as(a), ns._believed_as(b))


class SelectionBeliefVsTruth(unittest.TestCase):
    def test_selection_uses_belief_not_truth(self):
        """Believed-AS-disjoint paths can share a TRUE AS when inference is
        wrong: that gap is exactly what the adversary exploits. Over many
        trials with high error, at least some selected path-sets must be
        believed-disjoint yet truly-AS-colliding."""
        collided = 0
        trials = 400
        for _ in range(trials):
            net = ns.Network.random(60, n_as=12, n_juris=5, infer_error=0.5)
            paths = ns.select_paths(net, n=4, disjoint="as")  # reasons on belief
            if paths is None:
                continue
            guards_true_as = [p[0].asn for p in paths]
            if len(set(guards_true_as)) < len(guards_true_as):
                collided += 1   # two guards share a TRUE AS despite belief-disjoint
        self.assertGreater(collided, 0,
                           "inference error should sometimes yield truly-colliding "
                           "paths that selection believed were disjoint")

    def test_truth_mode_is_cleaner_than_belief_mode(self):
        """Selecting on ground truth yields fewer true-AS collisions than
        selecting on a noisy belief -- the quantified value of solving OP-1."""
        def collisions(use_truth):
            c = 0
            for _ in range(300):
                net = ns.Network.random(60, n_as=12, n_juris=5, infer_error=0.4)
                paths = ns.select_paths(net, 4, disjoint="as", use_truth=use_truth)
                if paths is None:
                    continue
                tas = [p[0].asn for p in paths]
                c += len(tas) - len(set(tas))
            return c
        self.assertLess(collisions(use_truth=True), collisions(use_truth=False))


class Adversaries(unittest.TestCase):
    def test_as_level_sees_at_least_node_level(self):
        """The AS-level adversary correlates a superset of what the node-level
        one does: owning a relay in an AS subsumes owning that exact relay."""
        for _ in range(200):
            net = ns.Network.random(50, n_as=10, n_juris=5,
                                    adversary_relays=15, adversary_as=3)
            paths = ns.select_paths(net, 4, disjoint="none")
            if paths is None:
                continue
            node_break = ns.adversary_breaks(paths, k=2)
            as_break = ns.adversary_breaks_as_level(paths, k=2)
            if node_break:
                self.assertTrue(as_break)   # node-level break implies AS-level

    def test_higher_error_raises_mean_leak(self):
        """The headline monotonicity: mean linkage leak grows with inference
        error (more believed-disjoint-but-truly-colliding circuits)."""
        def mean_leak(err):
            (_, _, _, leak, _), = ns.sweep([80], n=4, k=3, requested="as",
                                           frac_adv=0.35, adv_as=3,
                                           infer_error=err, as_level_adv=True,
                                           trials=1500)
            return leak
        self.assertLess(mean_leak(0.0), mean_leak(0.6))


class RoundTrip(unittest.TestCase):
    def test_message_survives_simulated_path(self):
        self.assertEqual(ns._demo_full_message_roundtrip(), 4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
