#!/usr/bin/env python3
"""Run every ScrambNet PoC demo and test suite, and report one verdict.

    python3 run_all.py

Exits non-zero if any demo errors or any test fails. No dependencies, no
network. This is the single command a reviewer runs first.
"""

import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEMOS = ["e2e.py", "dispersal.py", "rendezvous.py", "gossip.py",
         "network_sim.py", "sybil_sim.py"]
TEST_MODULES = ["test_e2e", "test_dispersal", "test_rendezvous", "test_gossip",
                "test_properties", "test_network_sim", "test_sybil_sim"]


def run_demos() -> bool:
    ok = True
    for demo in DEMOS:
        print(f"\n{'=' * 70}\n  demo: {demo}\n{'=' * 70}")
        r = subprocess.run([sys.executable, str(HERE / demo)])
        if r.returncode != 0:
            print(f"  !! {demo} exited {r.returncode}")
            ok = False
    return ok


def run_tests() -> bool:
    print(f"\n{'=' * 70}\n  tests\n{'=' * 70}")
    sys.path.insert(0, str(HERE))
    suite = unittest.TestLoader().loadTestsFromNames(TEST_MODULES)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    demos_ok = run_demos()
    tests_ok = run_tests()
    print(f"\n{'=' * 70}")
    if demos_ok and tests_ok:
        print("  VERDICT: all demos ran and all tests passed.")
        sys.exit(0)
    print("  VERDICT: FAILURES above (demos_ok="
          f"{demos_ok}, tests_ok={tests_ok}).")
    sys.exit(1)
