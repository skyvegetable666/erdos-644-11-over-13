# Verification and provenance

## Evidence levels

The package has three separate ingredients:

1. A written combinatorial reduction from any hypothetical high-transversal
   family to the necessary real inequalities in [PROOF.md](../PROOF.md).
2. Exact reconstruction of the selected support costs and all 27 formula
   groups from the configuration.
3. An exact arithmetic and propositional refutation of those formulas.

The Python checker verifies the second and third ingredients. It also
checks the arithmetic in the small-rank reduction. It does not formally
prove the set-theoretic constructions or the published theorem used for
small ranks. External review and novelty are not established by these
checks. A finite search for an example is not a premise of the result.

## Formula map

The saved model's `labels` field identifies every group:

| Group labels | Mathematical source |
| --- | --- |
| `partition_extrema` | PROOF Section 4, attained small and large pairs |
| `lexicographic_attainer` | Sections 3 and 5, minimum good profile |
| `balanced_middle_pair_query` | Section 5, integer query lowering the profile |
| `attained_pair_gap` | Section 5, the global restriction applied to x and Y |
| `root`, `maximum_small_root` | Sections 3-5, all necessary good-profile conditions |
| Names ending in `_response` | Section 6, guarded queries and strict trace caps |
| Names ending in `_left` or `_right` | Sections 4-6, actual good replacements |
| Names containing `_static_`, `_tree_`, `_zero_core_` | Sections 7-8, full pair covers and integer rounding |

There are four independent response edges. The model does not assert
that they are equal or introduce a single joint incidence realization.
Each inequality is necessary for the actual response of its own query.
Unavailable queries impose no response constraints.

## Files

| File | Role |
| --- | --- |
| `verify.py` | Release entry point, integrity checks, fixed configuration, small ranks |
| `verifier/lexicographic_bound_model.py` | Necessary-model reconstruction |
| `verifier/three_extrema_086_model.py` | Exact support audit and dual-direction enumeration |
| `verifier/exact_linear_logic.py` | Rational linear forms, CNF compilation, Farkas and RUP checks |
| `verifier/verify_linear_refutation.py` | Certificate validation |
| `verifier/*_configuration.json` | The fixed four-query selection |
| `verifier/targeted_0849_supports.json` | Full membership-mask supports; the older name is intentional |
| `verifier/*_model.json` | Saved formulas, labels, coefficient, and audit counts |
| `verifier/*_certificate.json` | Exact rational theory clauses and the propositional proof |
| `MANIFEST.json` | SHA-256 and size of every release input |
| `PROVENANCE.json` | Source names and hashes of unchanged research artifacts |
| `reports/verification.json` | Recorded release verification output |

The core modules retain some unused research options. The release entry
point requires equality with the complete fixed configuration before
using them; those additional options are not dependencies of this proof.
The maximum-pair appendix includes the full auxiliary integer construction,
so its historical references to other research notes are not required.

The certificate's `source` field retains the original relative research
path. It is a provenance label. The release entry point opens the model
in `verifier/` and compares its formulas exactly; no external workspace
or absolute path is accessed.

## Reproducibility boundary

Run `python3 -I -S verify.py` with Python 3.11 or newer. The `-I` flag
isolates the interpreter from user path settings, and `-S` disables
site-package loading. No discovery solver is imported by the selected
configuration. The checker rejects optimized Python modes because its
assertions are proof checks.

`MANIFEST.json` protects against accidental edits or incomplete copies;
it is not a substitute for a cryptographic signature or an external
review. A deliberately changed file and manifest require a new review.
Reports are outputs, not certificate premises, and are not part of the
input manifest. The GitHub workflow repeats verification on Python 3.11
and 3.13 without installing any Python dependencies.

## Deliberate simplification of the small-rank step

The original research checker revalidated earlier 17/20, 171/200, 6/7,
and auxiliary bound artifacts to handle small ranks. That complete old
chain passed again during repository preparation on 2026-10-29.

This release replaces only that dependency chain with the published
$f(k,6)=k$ theorem for $k\geq2$, plus the elementary singleton case.
For $k<20$ these bounds are already below $11k/13+8$. The main
configuration, model, support data, rational certificate, and core
checker code remain unchanged. The replacement and its citation are
explicit in [PROOF.md](../PROOF.md) and [REFERENCES.md](../REFERENCES.md).
