"""Verify the published 11/13 package using only Python's standard library."""

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
ARTIFACTS = ROOT / "verifier"
PREFIX = "targeted_eleven_thirteenths"


def verify_hashes():
    manifest = json.loads((ROOT / "MANIFEST.json").read_text())
    if manifest["format"] != 1 or not manifest["files"]:
        raise ValueError("Unsupported or empty manifest")
    for name, record in manifest["files"].items():
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file():
            raise ValueError("Missing or invalid package path: " + name)
        content = path.read_bytes()
        if len(content) != record["bytes"] or hashlib.sha256(content).hexdigest() != record["sha256"]:
            raise ValueError("Integrity check failed: " + name)
    return len(manifest["files"])


def verify():
    if not __debug__:
        raise RuntimeError("Assertions are part of the checker; do not run Python with -O or -OO")
    checked_files = verify_hashes()
    sys.path.insert(0, str(ARTIFACTS))
    from lexicographic_bound_model import formulas
    from verify_linear_refutation import verify as verify_refutation

    configuration = json.loads((ARTIFACTS / (PREFIX + "_configuration.json")).read_text())
    assert configuration == {
        "coefficient": "11/13", "gap": ["9/26", "9/26"],
        "partition": "artificial", "gap_certificate": None,
        "support_file": "targeted_0849_supports.json",
        "large_rank_additive": 8, "uniform_additive": 8,
        "minimum_largest_balanced": True, "minimum_largest_pair_gap": True,
        "attained_pair_gap": True, "strict_extremal_bounds": True,
        "strict_response_atoms": True,
        "root_covers": {"static": [439, 449]}, "maximum_small_covers": {},
        "queries": [
            {"name": "U0", "pivot": 0, "fraction": "0", "tree": [2031, 2047], "biclique": [882]},
            {"name": "UhD", "pivot": 0, "fraction": "1/2", "strict_side": "d",
             "strict_level": "largest", "tree": [448], "right_covers": {"static": [449]}},
            {"name": "U1D", "pivot": 0, "fraction": "1", "strict_side": "d",
             "strict_level": "largest", "tree": [2029]},
            {"name": "V1D", "pivot": 1, "fraction": "1", "strict_side": "d",
             "strict_level": "middle", "tree": [1552]},
        ],
        "minimum_large_fractions": [],
    }
    coefficient = Fraction(11, 13)
    assert Fraction(3, 4) <= coefficient < 1
    minimum_rank = (3 / (1 - coefficient)).__floor__() + 1
    assert minimum_rank == 20 and 3 < (1 - coefficient) * minimum_rank

    regenerated = formulas(configuration)
    assert regenerated == json.loads((ARTIFACTS / (PREFIX + "_model.json")).read_text())
    certificate = ARTIFACTS / (PREFIX + "_certificate.json")
    assert json.loads(certificate.read_text())["formulas"] == regenerated["formulas"]
    expected_supports = {"three_bin_directions": 10, "four_bin_directions": 101,
                         "static_supports": 2, "tree_supports": 5, "biclique_supports": 1}
    assert regenerated["support_audit"] == expected_supports
    arithmetic = verify_refutation(certificate)
    assert arithmetic["formulas"] == 27
    assert arithmetic["exact_farkas_checks"] == 919
    assert arithmetic["rup_additions"] == 63

    # The published f(k,6)=k theorem covers 2<=k<20; k=1 is elementary.
    small_ranks = []
    for rank in range(1, minimum_rank):
        known_bound = 2 if rank == 1 else rank
        assert known_bound <= coefficient * rank + 8
        small_ranks.append(rank)
    return {
        "status": "passed",
        "claimed_bound": "tau(H) <= 11k/13 + 8",
        "coefficient": str(coefficient), "additive_constant": 8,
        "main_argument_minimum_rank": minimum_rank,
        "manifest_files_checked": checked_files,
        "formula_groups_regenerated": len(regenerated["formulas"]),
        "support_audit": regenerated["support_audit"],
        "refutation_audit": {key: value for key, value in arithmetic.items()
                             if key not in ("source", "hypergraph_model_and_cover_lemmas_audited")},
        "small_rank_comparisons_checked": small_ranks,
        "small_rank_dependency": "Published f(k,6)=k for k>=2; elementary k=1 case. See REFERENCES.md.",
        "small_rank_dependency_reproved_by_code": False,
        "combinatorial_reduction": "PROOF.md and docs/maximum_pair_lemma.md; not formally mechanized",
        "third_party_python_packages_required": False,
        "external_review_or_priority_established": False,
        "original_three_quarters_conjecture_resolved": False,
        "python_version": sys.version.split()[0],
        "verified_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Also save the verification report as JSON")
    args = parser.parse_args()
    report = verify()
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
