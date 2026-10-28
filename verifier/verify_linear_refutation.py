"""Verify rational theory clauses and a propositional RUP refutation.

This certifies the exported formulas only. Their mathematical necessity
must be checked separately before drawing a hypergraph conclusion.
"""

import argparse
from functools import reduce
from math import gcd
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exact_linear_logic import Compiler, check_rup, contradiction


def verify(path):
    data = json.loads(path.read_text())
    compiler = Compiler()
    for formula in data["formulas"]:
        compiler.require(formula)
    assert compiler.count == data["base_variables"]
    assert len(compiler.atoms) == data["base_atom_count"]
    assert len(compiler.clauses) == data["base_clause_count"]
    atoms = {int(key): value for key, value in data["atoms"].items()}
    assert len(atoms) == len(data["atoms"])
    assert all(atoms[key] == row for key, row in compiler.atoms.items())
    assert all(key in compiler.atoms or key > compiler.count for key in atoms)
    assert all(isinstance(key, int) and key > 0 and row and any(row)
               and all(isinstance(value, int) and value for value in row.values())
               and reduce(gcd, (abs(value) for value in row.values())) == 1
               for key, row in atoms.items())
    theory_clauses = []
    for row in data["theory_certificates"]:
        contradiction(atoms, row)
        theory_clauses.append([literal for literal, _ in row])
    checked = check_rup(compiler.clauses + theory_clauses, data["rup_proof"])
    return {"status": "verified_exact_refutation", "source": data["source"],
            "formulas": len(data["formulas"]), "base_clauses": len(compiler.clauses),
            "linear_atoms": len(atoms), "exact_farkas_checks": len(theory_clauses),
            "rup_additions": checked, "independent_of_smt_sat_and_lp": True,
            "hypergraph_model_and_cover_lemmas_audited": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("certificate", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.certificate), indent=2))
