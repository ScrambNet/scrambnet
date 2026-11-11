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


class SteeringAttackAndPS12Defense(unittest.TestCase):
    """PS-12: a hostile map steers AS-disjoint selection onto the adversary and
    breaks CONTENT (the critical hole a red-team found), and the PS-12 defense
    detects and blocks it. These tests pin both the attack and the fix so a
    regression that reintroduces the hole fails here."""

    @staticmethod
    def _honest(size, frac_adv):
        return ns.Network.random(size, n_as=max(6, size // 3), n_juris=5,
                                 adversary_relays=round(size * frac_adv),
                                 adversary_as=3, infer_error=0.0)  # belief=reality

    def _steering(self, size, frac_adv):
        net = self._honest(size, frac_adv)
        ns.make_steering_map(net)          # ground truth unchanged; belief attacked
        return net

    def test_steering_map_breaks_content_without_defense(self):
        """The attack: with the undefended selector, a steering map puts the
        adversary on >=k circuits deterministically -> content break, every
        time, at only 20% ownership."""
        broken = 0
        for _ in range(200):
            net = self._steering(80, 0.20)
            paths = ns.select_paths(net, 4, disjoint="as")
            if paths and ns.adversary_breaks_as_level(paths, k=3):
                broken += 1
        self.assertGreater(broken, 190)   # ~all 200; the deterministic break

    def test_detect_steering_no_false_positive_on_honest_map(self):
        """The defense must not cry wolf: an honest map is never flagged."""
        fp = sum(1 for _ in range(300)
                 if ns.detect_steering(self._honest(80, 0.20)))
        self.assertEqual(fp, 0)

    def test_detect_steering_catches_the_attack(self):
        tp = sum(1 for _ in range(300)
                 if ns.detect_steering(self._steering(80, 0.20)))
        self.assertGreater(tp, 290)       # ~all

    def test_detector_catches_multi_group_evasion(self):
        """A red-team evaded the first detector (which keyed on 'one giant AS')
        by collapsing the honest pool into a FEW ASes instead of one. The fixed
        detector keys on the singleton fraction (the adversary's fake-distinct
        relays, which it cannot avoid), so it catches the effective steering
        regime (honest_groups 1..5, a 10-100% content break) regardless of how
        the honest pool is grouped."""
        for g in (1, 2, 3, 5):
            caught = 0
            for _ in range(200):
                net = self._honest(80, 0.40)
                ns.make_steering_map(net, honest_groups=g)
                if ns.detect_steering(net):
                    caught += 1
            self.assertGreater(caught, 190,
                               f"multi-group steering g={g} evaded the detector")

    def test_detector_no_false_positive_under_inference_noise(self):
        """Inference noise also creates singletons; the detector must not mistake
        a noisy honest map for steering. The 'few crowded ASes' clause keeps it
        quiet even at heavy error."""
        for err in (0.1, 0.2, 0.4):
            fp = 0
            for _ in range(200):
                net = ns.Network.random(80, n_as=26, n_juris=5,
                                        adversary_relays=16, adversary_as=3,
                                        infer_error=err)
                if ns.detect_steering(net):
                    fp += 1
            self.assertLess(fp, 10, f"too many false positives at error {err}")

    def test_ps12_defense_blocks_the_break(self):
        """With PS-12, the steering map yields a 'steering-anomaly' (the client
        falls back) instead of compromised circuits -- zero content breaks."""
        anomaly = breaks = 0
        for _ in range(200):
            net = self._steering(80, 0.20)
            out = ns.select_paths_ps12(net, 4, disjoint="as")
            if out == "steering-anomaly":
                anomaly += 1
            elif isinstance(out, list) and ns.adversary_breaks_as_level(out, k=3):
                breaks += 1
        self.assertGreater(anomaly, 190)
        self.assertEqual(breaks, 0)       # the hole is closed

    def test_ps12_defense_leaves_honest_selection_intact(self):
        """No collateral damage: an honest map still builds 4 circuits."""
        ok = 0
        for _ in range(200):
            out = ns.select_paths_ps12(self._honest(80, 0.20), 4, disjoint="as")
            if isinstance(out, list) and len(out) == 4:
                ok += 1
        self.assertGreater(ok, 190)


class RoundTrip(unittest.TestCase):
    def test_message_survives_simulated_path(self):
        self.assertEqual(ns._demo_full_message_roundtrip(), 4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
