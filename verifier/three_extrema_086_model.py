"""Explicit necessary conditions for tau > 43k/50 + 3.

The model uses the largest small pair x, the smallest large pair Y,
and a good triple (u,v,w) minimizing its largest pair. All quantities
are divided by k. See three_extrema_086_bound.md for the constructions.
This module uses exact arithmetic and imports no discovery code.
"""

from fractions import Fraction as Q
from itertools import combinations, product
import json
from pathlib import Path


C = Q(43, 50)
ALPHA = Q(113, 400)
BETA = Q(9, 25)
ROOT = Path(__file__).resolve().parent


def n(value):
    return ["num", str(value)]


def v(name):
    return ["var", name]


def add(*terms):
    return ["add", *terms]


def scale(value, term):
    return ["mul", str(value), term]


def sub(first, second):
    return add(first, scale(-1, second))


def le(first, second):
    return ["le", first, second]


def lt(first, second):
    return ["lt", first, second]


def conjunction(*terms):
    return ["and", *terms]


def disjunction(*terms):
    return ["or", *terms]


def implies(first, second):
    return ["implies", first, second]


def affine(row, point):
    return add(*(scale(coefficient, value) for coefficient, value in zip(row, point)))


def unique_solution(rows, rhs):
    size = len(rhs)
    matrix = [[Q(value) for value in row] + [Q(value)] for row, value in zip(rows, rhs)]
    for column in range(size):
        pivot = next((i for i in range(column, size) if matrix[i][column]), None)
        if pivot is None:
            return None
        matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
        divisor = matrix[column][column]
        matrix[column] = [value / divisor for value in matrix[column]]
        for i in range(size):
            if i != column:
                multiplier = matrix[i][column]
                matrix[i] = [a - multiplier * b for a, b in zip(matrix[i], matrix[column])]
    return tuple(row[-1] for row in matrix)


def dual_directions(bins):
    # All incomparable subset-sum ties, together with simplex boundaries.
    hyperplanes = {tuple(int(i == j) for i in range(bins)) for j in range(bins)}
    for signs in product((-1, 0, 1), repeat=bins):
        if -1 in signs and 1 in signs and next(value for value in signs if value) > 0:
            hyperplanes.add(signs)
    vertices = set()
    for selected in combinations(sorted(hyperplanes), bins - 1):
        point = unique_solution([(1,) * bins, *selected], [1] + [0] * (bins - 1))
        if point is not None and min(point) >= 0:
            vertices.add(point)
    return sorted(vertices)


def audit_supports(path=None):
    data = json.loads((path or ROOT / "extrema_cover_supports.json").read_text())
    directions = {bins: dual_directions(bins) for bins in (3, 4)}
    rows = {}
    adjacent = {"static": [(0, 1), (0, 2), (1, 2), (0, 3), (1, 4), (2, 5)],
                "tree": [(0, 1), (0, 2), (0, 3), (0, 4), (1, 5), (2, 6), (3, 7)],
                "biclique": [(0, 3), (1, 4), (2, 5)]}
    for kind, templates in data.items():
        assert kind in adjacent
        bins = 4 if kind == "static" else 3
        for index, support in templates.items():
            assert len(support) == (8 if kind == "tree" else 6)
            assert all(masks and len(masks) == len(set(masks))
                       and all(isinstance(mask, int) and 0 < mask < 1 << bins for mask in masks)
                       for masks in support)
            for first, second in adjacent[kind]:
                assert all(a & b for a in support[first] for b in support[second])
            if bins == 4:
                assert sum(len(masks) - 1 for masks in support) <= 3
            rows[kind, int(index)] = [
                [min(sum(weight[b] for b in range(bins) if mask >> b & 1) for mask in masks)
                 for masks in support] for weight in directions[bins]]
    audit = {"three_bin_directions": len(directions[3]),
             "four_bin_directions": len(directions[4]),
             "static_supports": len(data.get("static", {})),
             "tree_supports": len(data.get("tree", {}))}
    if "biclique" in data:
        audit["biclique_supports"] = len(data["biclique"])
    return rows, audit


def formulas():
    cover_rows, audit = audit_supports()
    x, y, p, r, u, vv, w = map(v, ("x", "Y", "p", "r", "u", "v", "w"))
    zero, one, c = n(0), n(1), n(C)
    result, labels = [], []

    def require(label, formula):
        labels.append(label)
        result.append(formula)

    def good(label, values, condition=True):
        requirements = [le(add(*values), add(one, x)), le(add(*values), n(3 - 2 * C)),
                        disjunction(*(le(u, value) for value in values))]
        requirements.extend(le(zero, value) for value in values)
        requirements.extend(le(add(first, second), one) for first, second in combinations(values, 2))
        requirements.extend(disjunction(le(value, x), le(y, value)) for value in values)
        for i, small in enumerate(values):
            big = [values[j] for j in range(3) if j != i]
            cost = add(n(3), scale(-1, add(*big)), scale(-3, y), scale(2, x), scale(-1, small))
            requirements.append(implies(conjunction(le(small, x), *[le(y, value) for value in big]), lt(c, cost)))
        require(label, implies(condition, conjunction(*requirements)))

    def failure(label, rows, point, condition=True):
        require(label, implies(condition, disjunction(*(lt(c, affine(row, point)) for row in rows))))

    def static(label, values, index, condition=True):
        a, b, d = values
        masses = [a, b, d, sub(one, add(b, d)), sub(one, add(a, d)), sub(one, add(a, b))]
        failure(label, cover_rows["static", index], masses, condition)

    def rank_core(label, values, condition=True):
        a, b, d = values
        total = add(*values)
        costs = [total, scale(Q(1, 3), add(one, total)),
                 *[scale(Q(1, 2), add(one, first, second)) for first, second in combinations(values, 2)],
                 scale(Q(1, 4), add(n(2), scale(3, b))),
                 scale(Q(1, 4), add(n(2), scale(3, d))),
                 scale(Q(1, 5), add(n(2), scale(4, a), b, d))]
        require(label, implies(condition, disjunction(*(lt(c, cost) for cost in costs))))

    require("extremal_pair", conjunction(le(zero, x), le(x, n(ALPHA)), le(n(BETA), y), le(y, p),
                                        le(zero, r), le(r, p), le(scale(2, p), sub(n(2 - C), x))))
    require("ordered_minimum_largest_attainer", conjunction(le(w, vv), le(vv, u)))
    good("maximum_small_root", (p, x, r))
    good("minimum_largest_root", (u, vv, w))
    static("root_static_485", (u, vv, w), 485)
    static("root_static_449", (u, vv, w), 449)
    failure("root_adaptive", [[0, 1, 1, 1], [Q(1, 3), Q(2, 3), Q(2, 3), 1],
                               [Q(1, 2), 1, Q(-1, 2), Q(1, 2)],
                               [Q(1, 2), Q(-1, 2), 1, Q(1, 2)]], (one, u, vv, w))
    failure("root_split", [[0, 1, 1, 1], [1, -1, 0, 1], [1, 0, -1, 1],
                            [Q(1, 3), 1, Q(1, 3), Q(1, 3)],
                            [Q(1, 3), Q(1, 3), 1, Q(1, 3)]], (one, u, vv, w))

    queries = [("X", (p, x, r), Q(0), [91], None),
               ("U0", (u, vv, w), Q(0), [2027, 2065, 104], None),
               ("Uq", (u, vv, w), Q(1, 4), [2027, 448], 437),
               ("V0", (vv, u, w), Q(0), [955], 439),
               ("Vh", (vv, u, w), Q(1, 2), [], 439)]
    for name, (first, second, third), fraction, trees, static_index in queries:
        h, a, b, d = [v(name + "_" + suffix) for suffix in "habd"]
        total = add(first, second, third)
        minimum = ["ite", le(total, c), zero, sub(total, c)]
        delta = add(scale(1 - fraction, minimum), scale(fraction, first))
        active = le(add(second, third), c)
        conditions = [*[le(zero, value) for value in (h, a, b, d)], le(h, delta),
                      le(a, sub(add(n(1 - C), first), delta)),
                      le(b, sub(one, add(first, third))), le(d, sub(one, add(first, second))),
                      le(add(h, a, b, d), one)]
        require(name + "_response", implies(active, conjunction(*conditions)))
        good(name + "_left", (third, a, add(h, b)), active)
        good(name + "_right", (second, a, add(h, d)), active)
        masses = (h, second, third, a, sub(one, add(second, third, a)), b, d, sub(first, h))
        for index in trees:
            failure(name + "_tree_" + str(index), cover_rows["tree", index], masses, active)
        if static_index:
            rank_core(name + "_rank_core", (second, a, add(h, d)), active)
            static(name + "_static_" + str(static_index), (second, a, add(h, d)), static_index, active)

    a, b = v("Y_a"), v("Y_b")
    active = le(y, c)
    cap = scale(Q(1, 2), sub(n(2 - C), y))
    require("minimum_large_response", implies(active, conjunction(le(zero, a), le(zero, b),
                                                                 le(a, cap), le(b, cap), le(add(a, b), one))))
    good("minimum_large_good", (y, a, b), active)
    return {"formulas": result, "labels": labels, "support_audit": audit,
            "coefficient": str(C), "gap": [str(ALPHA), str(BETA)]}


if __name__ == "__main__":
    print(json.dumps(formulas(), indent=2))
