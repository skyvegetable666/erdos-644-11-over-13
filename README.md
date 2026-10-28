# Erdos Problem 644: an 11/13 upper bound

[![Verify](https://github.com/skyvegetable666/erdos-644-11-over-13/actions/workflows/verify.yml/badge.svg)](https://github.com/skyvegetable666/erdos-644-11-over-13/actions/workflows/verify.yml)

This research release presents an internally checked, computer-assisted
argument for

$$
f(k,7)\leq \frac{11}{13}k+8.
$$

Here every subfamily of **at most seven** edges of a $k$-uniform hypergraph
must have a transversal of size at most two. A transversal is a set of
vertices meeting every edge.

**Status:** the exact certificate passes an independent checker. The
combinatorial reduction is a written mathematical argument, not a formally
mechanized proof. External mathematical review and literature priority
have not been established. The conjectured coefficient $3/4$ remains open
in this work. Research and code were developed with AI assistance.

## Verify

Use Python 3.11 or newer. No installation, third-party Python packages,
solver, GPU, or network access is required after cloning.

```sh
git clone https://github.com/skyvegetable666/erdos-644-11-over-13.git
cd erdos-644-11-over-13
python3 -I -S verify.py
```

Successful verification exits with code zero and reports:

| Check | Expected result |
| --- | ---: |
| Regenerated necessary formula groups | 27 |
| Exact rational arithmetic conflicts | 919 |
| RUP proof additions | 63 |
| Three-block dual directions | 10 |
| Four-block dual directions | 101 |
| Selected supports: static / tree / biclique | 2 / 5 / 1 |

The checker verifies SHA-256 hashes, reconstructs the model from the
configuration and audited supports, checks equality with the saved
certificate premises, and verifies the arithmetic and propositional
refutation. Assertions are part of this checker: **do not use `-O` or
`-OO`**. The entry point rejects those modes.

To save a fresh report:

```sh
python3 -I -S verify.py --output reports/local.json
```

The main certificate treats $k\geq20$. For $2\leq k<20$, this release
uses the published theorem $f(k,6)=k$ and checks the numerical comparison
with $11k/13+8$. The case $k=1$ is elementary. See [references](REFERENCES.md).
This simpler small-rank step avoids depending on the earlier experimental
chain of upper-bound certificates.

## Read the proof

1. [PROOF.md](PROOF.md): definitions, integer reductions, four queries,
   candidate-pair graphs, fractional covers, rounding, and the certificate.
2. [Maximum-pair lemma](docs/maximum_pair_lemma.md): a full integer proof
   of the three-anchor ingredient.
3. [Verification notes](docs/VERIFICATION.md): evidence boundaries,
   artifact layout, provenance, and the mapping from formulas to lemmas.
4. [Recorded verification](reports/verification.json): the release audit;
   rerun the checker to verify your own checkout.

## What the result says

The coefficient is $11/13\approx0.846154$. Together with the standard
complete-family lower bound, the claimed argument yields

$$
\frac34\leq\liminf_{k\to\infty}\frac{f(k,7)}k
\leq\limsup_{k\to\infty}\frac{f(k,7)}k\leq\frac{11}{13}.
$$

This does not prove that the limit exists or that it equals $3/4$.
The earlier internal bound $17k/20+4$ has a smaller additive constant;
$11/13$ improves its asymptotic coefficient by $1/260$, and gives the
smaller displayed finite bound only when $k>1040$. That earlier certificate
is not part of this focused release.

The published 1999 upper bound has coefficient $7/8$. This repository
does **not** claim to establish the best bound in the current literature.
The [problem page](https://www.erdosproblems.com/644) was checked on
2026-10-29; a problem-page check is not an exhaustive literature review.

## Review and provenance

The main certificate, model, support data, and core verifier modules are
preserved byte for byte from the research artifacts. [PROVENANCE.json](PROVENANCE.json)
records their source names and hashes. [MANIFEST.json](MANIFEST.json)
covers the release inputs; generated reports are separate outputs.

Review is particularly useful for the combinatorial necessity of the
27 formula groups, the strict response inequalities, and the integer
rounding budgets. A passing program establishes its encoded checks;
the written reduction remains an essential part of the theorem.

Original research artifact date: 2026-10-26. Repository preparation:
2026-10-29. See [REFERENCES.md](REFERENCES.md) for the primary sources.
