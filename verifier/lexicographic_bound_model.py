"""Exact necessary model with a lexicographically minimum good triple.

The selected cover list is data; every support and every corresponding
candidate graph is checked independently of the exploration catalogue.
"""

from fractions import Fraction as Q
from itertools import combinations, permutations
import json
from pathlib import Path

from three_extrema_086_model import (
    add, affine, audit_supports, conjunction, disjunction, implies,
    le, lt, n, scale, sub, v,
)


ROOT = Path(__file__).resolve().parent


def eq(first, second):
    return ["eq", first, second]


def extrema(values, largest):
    first, second, third = values
    pair = ["ite", le(first, second), second if largest else first, first if largest else second]
    return ["ite", le(pair, third), third if largest else pair, pair if largest else third]


def formulas(configuration):
    c0, alpha, beta = map(Q, (configuration["coefficient"], *configuration["gap"]))
    cover_rows, audit = audit_supports(ROOT / configuration["support_file"])
    response_graph_supports = []
    if configuration.get('four_row_three_query_support_file'):
        from four_row_complete_supports import audit as audit_response_supports
        response_graph_supports, response_audit = audit_response_supports(
            ROOT / configuration['four_row_three_query_support_file'])
        audit['four_row_response_supports'] = response_audit
    x, y, p, r, u, vv, w = map(v, ("x", "Y", "p", "r", "u", "v", "w"))
    zero, one, c = n(0), n(1), n(c0)
    strict_extrema = configuration.get("strict_extremal_bounds", False)
    assert not strict_extrema or alpha == beta
    pair_gap = configuration.get("minimum_largest_pair_gap", False)
    assert not pair_gap or (configuration.get("minimum_largest_balanced", False) and c0 >= Q(2, 3))
    result, labels = [], []

    def require(label, formula):
        labels.append(label)
        result.append(formula)

    def good(label, values, condition=True, root=False):
        terms = [(lt if strict_extrema else le)(add(*values), n(3 - 2 * c0))]
        terms.extend(le(zero, value) for value in values)
        terms.extend(le(add(first, second), one) for first, second in combinations(values, 2))
        terms.extend(disjunction(le(value, x), le(y, value)) for value in values)
        if pair_gap:
            terms.extend(disjunction(le(u, value), lt(add(scale(2, u), value), n(2-c0)))
                         for value in values)
        if not root:
            big, small = extrema(values, True), extrema(values, False)
            middle = sub(sub(add(*values), big), small)
            terms.extend([le(u, big), implies(eq(big, u), le(vv, middle)),
                          implies(conjunction(eq(big, u), eq(middle, vv)), le(w, small))])
        if configuration.get('asymmetric_triple_bound', False):
            big, small = extrema(values, True), extrema(values, False)
            middle = sub(sub(add(*values), big), small)
            terms.append(disjunction(lt(small, n(1-c0)),
                                     lt(n(c0-Q(1, 2)), middle),
                                     lt(n(2*c0-Q(3, 2)), sub(big, small))))
        for i, small in enumerate(values):
            large = [values[j] for j in range(3) if j != i]
            cost = add(n(3), scale(-1, add(*large)), scale(-3, y), scale(2, x), scale(-1, small))
            terms.append(implies(conjunction(le(small, x), *[le(y, value) for value in large]), lt(c, cost)))
        if configuration.get("split_kernel_bound", False):
            for i, third in enumerate(values):
                first, second = [values[j] for j in range(3) if j != i]
                a_split = add(n(c0-1), first, scale(-1, second), third)
                b_split = add(n(c0-1), scale(-1, first), second, third)
                guard = conjunction(le(zero, a_split), le(a_split, first),
                                    le(zero, b_split), le(b_split, second),
                                    le(add(one, third, scale(-1, first), scale(-1, second),
                                           a_split, b_split), c))
                bound = add(first, second, scale(-1, third), n(2-2*c0))
                terms.append(implies(guard, lt(c, bound)))
        require(label, implies(condition, conjunction(*terms)))
        if configuration.get("rank_kernel_response_bounds", False):
            a, b, d = values
            kernel_rank_rows(label, {6: a, 5: b, 3: d,
                                    1: sub(one, add(b, d)), 2: sub(one, add(a, d)),
                                    4: sub(one, add(a, b))}, 3, condition)

    def costs_fail(label, costs, condition=True):
        require(label, implies(condition, disjunction(*(lt(c, cost) for cost in costs))))

    def kernel_rank_rows(label, masses, rows, condition):
        assert c0 >= Q(4, 5) and rows in (3, 4)
        full = (1 << rows)-1
        guard = conjunction(condition, eq(masses.get(full, zero), zero))
        contributions = {mask: ['ite', disjunction(*[lt(zero, other_mass)
                                                    for other, other_mass in masses.items()
                                                    if mask | other == full]), mass, zero]
                         for mask, mass in masses.items()}
        total = add(*contributions.values())
        lower = {5: Q(5, 13)*(1+2*c0)}
        lower[4] = Q(2, 5)*(lower[5]+c0+1)
        lower[3] = Q(3, 7)*(lower[4]+c0+1)
        quantitative = configuration.get('quantitative_kernel_hierarchy', False)
        saturated = configuration.get('saturated_kernel_hierarchy', False)
        assert not saturated or quantitative
        if saturated:
            lower = {6: c0}
            for size in (5, 4, 3):
                lower[size] = Q(size, 2*size-2)*min(lower[size+1]+c0, Q(2))
        rank_bound = (le(n(lower[rows]), total) if saturated else
                      lt(n(lower[rows]), total) if quantitative else le(one, total))
        require(label+'_kernel_rank', implies(guard, rank_bound))
        for row in range(rows):
            inside = add(*[mass for mask, mass in contributions.items() if mask >> row & 1])
            next_lower = n(lower[rows+1]) if quantitative else one
            require(label+'_kernel_row_'+str(row), implies(guard, lt(add(next_lower, c), add(total, inside))))

    def opposite_pair_covers(label, masses, condition):
        for rows in permutations(range(4)):
            groups = {mask: zero for mask in range(16)}
            for mask, mass in masses.items():
                image = sum(1 << i for i, row in enumerate(rows) if mask >> row & 1)
                groups[image] = mass
            guard = conjunction(condition, *[eq(groups[mask], zero) for mask in (7, 14, 15)])
            first = add(*[groups[mask] for mask in (2, 3, 4, 6, 9, 11, 12, 13)])
            second = add(groups[10], groups[11])
            near, total = add(second, groups[13]), add(groups[5], second)
            costs_fail(label+'_opposite_'+''.join(map(str, rows)),
                       [first, near, scale(Q(1, 2), add(near, total))], guard)

    def matching_four_covers(label, masses, condition):
        guard = conjunction(condition, *[eq(masses.get(mask, zero), zero)
                                         for mask in range(16) if mask.bit_count() >= 3])
        components = [(masses.get(mask, zero), masses.get(15 ^ mask, zero)) for mask in (3, 5, 6)]
        total = add(*[add(a, b) for a, b in components])
        costs_fail(label+'_matching_whole', [add(a, b) for a, b in components], guard)
        for index, (a, b) in enumerate(components):
            other = sub(total, add(a, b))
            costs_fail(label+'_matching_split_a_'+str(index), [other, add(a, scale(Q(1, 2), b))], guard)
            costs_fail(label+'_matching_split_b_'+str(index), [other, add(b, scale(Q(1, 2), a))], guard)

    def direct_three_query_covers(label, masses, condition):
        from four_row_three_query_cover import FIXED, SPLIT, ZERO, verify_graph
        verify_graph()
        for rows in permutations(range(4)):
            groups = {mask: zero for mask in range(16)}
            for mask, mass in masses.items():
                image = sum(1 << i for i, row in enumerate(rows) if mask >> row & 1)
                groups[image] = mass
            guard = conjunction(condition, *[eq(groups[mask], zero) for mask in ZERO])
            fixed = [add(*[groups[mask] for mask in query]) for query in FIXED]
            balanced = scale(Q(1, 2), add(fixed[0], fixed[1], groups[SPLIT]))
            costs_fail(label+'_three_query_'+''.join(map(str, rows)), [*fixed, balanced], guard)

    def two_split_three_query_covers(label, masses, condition):
        from four_row_two_split_three_query_cover import FIXED, SPLIT, ZERO, verify_graph
        verify_graph()
        for rows in permutations(range(4)):
            groups = {mask: zero for mask in range(16)}
            for mask, mass in masses.items():
                image = sum(1 << i for i, row in enumerate(rows) if mask >> row & 1)
                groups[image] = mass
            guard = conjunction(condition, *[eq(groups[mask], zero) for mask in ZERO])
            first, second, third = [add(*[groups[mask] for mask in query]) for query in FIXED]
            p_split, q_split = [groups[mask] for mask in SPLIT]
            costs = [first, second, third,
                     scale(Q(1, 2), add(first, second, p_split)),
                     scale(Q(1, 2), add(first, third, q_split)),
                     scale(Q(1, 3), add(first, second, third, p_split, q_split))]
            costs_fail(label+'_two_split_three_query_'+''.join(map(str, rows)), costs, guard)

    def replicated_pair_three_query_covers(label, masses, condition):
        from four_row_replicated_pair_three_query_cover import FIXED, SPLIT, ZERO
        for rows in permutations(range(4)):
            groups = {mask: zero for mask in range(16)}
            for mask, mass in masses.items():
                image = sum(1 << i for i, row in enumerate(rows) if mask >> row & 1)
                groups[image] = mass
            guard = conjunction(condition, *[eq(groups[mask], zero) for mask in ZERO])
            first, second, third = [add(*[groups[mask] for mask in query]) for query in FIXED]
            pair = groups[SPLIT]
            costs = [first, second, third, scale(Q(1, 2), add(first, second, pair)),
                     scale(Q(1, 2), add(first, third, pair))]
            costs_fail(label+'_replicated_pair_three_query_'+''.join(map(str, rows)), costs, guard)

    def catalogue_three_query_covers(label, masses, condition):
        orders = (permutations(range(4)) if configuration.get('four_row_support_all_orientations', False)
                  else [tuple(range(4))])
        for order in orders:
            groups = {mask: zero for mask in range(16)}
            for mask, mass in masses.items():
                image = sum(1 << i for i, row in enumerate(order) if mask >> row & 1)
                groups[image] = mass
            for template in response_graph_supports:
                guard = conjunction(condition, *[eq(groups[mask], zero) for mask in template['zeros']])
                point = [groups[mask] for mask in template['active']]
                costs_fail(label+'_support_'+template['name']+'_'+''.join(map(str, order)),
                           [affine(row, point) for row in template['rows']], guard)

    def complementary_split_three_query_covers(label, masses, condition):
        from four_row_complementary_split_three_query_cover import FIXED, SPLIT, ZERO
        for rows in permutations(range(4)):
            groups = {mask: zero for mask in range(16)}
            for mask, mass in masses.items():
                image = sum(1 << i for i, row in enumerate(rows) if mask >> row & 1)
                groups[image] = mass
            guard = conjunction(condition, *[eq(groups[mask], zero) for mask in ZERO])
            first, second, third = [add(*[groups[mask] for mask in query]) for query in FIXED]
            a, b = [groups[mask] for mask in SPLIT]
            costs = [add(first, a), second, third,
                     scale(Q(1, 2), add(second, third, a)),
                     scale(Q(1, 2), add(first, second, a, b)),
                     scale(Q(1, 2), add(first, third, a, b)),
                     scale(Q(1, 4), add(scale(2, first), second, third, scale(3, a), scale(2, b)))]
            costs_fail(label+'_complementary_split_three_query_'+''.join(map(str, rows)), costs, guard)

    def triple_covers(label, values, selected, condition=True):
        a, b, d = values
        masses = (a, b, d, sub(one, add(b, d)), sub(one, add(a, d)), sub(one, add(a, b)))
        for index in selected.get("static", []):
            costs_fail(label + "_static_" + str(index),
                       [affine(row, masses) for row in cover_rows["static", index]], condition)
        for kind in ("adaptive", "split", "rank_core"):
            for order in selected.get(kind, []):
                assert sorted(order) == [0, 1, 2]
                a, b, d = [values[i] for i in order]
                total = add(a, b, d)
                if kind == "adaptive":
                    costs = [total, scale(Q(1, 3), add(one, scale(2, a), scale(2, b), scale(3, d))),
                             scale(Q(1, 2), add(one, scale(2, a), scale(-1, b), d)),
                             scale(Q(1, 2), add(one, scale(2, b), scale(-1, a), d))]
                elif kind == "split":
                    costs = [total, add(one, scale(-1, a), d), add(one, scale(-1, b), d),
                             scale(Q(1, 3), add(one, scale(3, a), b, d)),
                             scale(Q(1, 3), add(one, a, scale(3, b), d))]
                else:
                    costs = [total, scale(Q(1, 3), add(one, total)),
                             *[scale(Q(1, 2), add(one, first, second))
                               for first, second in combinations((a, b, d), 2)],
                             scale(Q(1, 4), add(n(2), scale(3, b))),
                             scale(Q(1, 4), add(n(2), scale(3, d))),
                             scale(Q(1, 5), add(n(2), scale(4, a), b, d))]
                costs_fail(label + "_" + kind + "_" + "".join(map(str, order)), costs, condition)

    require("partition_extrema", conjunction(le(zero, x), le(x, n(alpha)),
                                            (lt if strict_extrema else le)(n(beta), y),
                                            le(y, p), le(r, p),
                                            (lt if strict_extrema else le)(add(scale(2, p), x), n(2 - c0))))
    require("lexicographic_attainer", conjunction(le(w, vv), le(vv, u), lt(n(c0 - Q(1, 2)), u)))
    if configuration.get("minimum_largest_balanced", False):
        require("balanced_middle_pair_query", lt(add(scale(2, u), vv), n(2-c0)))
    if configuration.get("attained_pair_gap", False):
        assert pair_gap
        require("attained_pair_gap", conjunction(*[
            disjunction(le(u, value), lt(add(scale(2, u), value), n(2-c0)))
            for value in (x, y)]))
    good("root", (u, vv, w), root=True)
    triple_covers("root", (u, vv, w), configuration["root_covers"])
    good("maximum_small_root", (p, x, r))
    triple_covers("maximum_small_root", (p, x, r), configuration.get("maximum_small_covers", {}))

    names = set()
    for query in configuration["queries"]:
        name, pivot, fraction = query["name"], query["pivot"], Q(query["fraction"])
        assert name.isalnum() and name[0].isalpha()
        assert name not in names and pivot in (0, 1, 2) and 0 <= fraction <= 1
        names.add(name)
        anchor_name = query.get("anchor", "minimum_largest")
        assert anchor_name in ("minimum_largest", "maximum_small")
        anchor = (u, vv, w) if anchor_name == "minimum_largest" else (p, x, r)
        first = anchor[pivot]
        second, third = [anchor[i] for i in range(3) if i != pivot]
        h, a, b, d = [v(name + "_" + suffix) for suffix in "habd"]
        total = add(first, second, third)
        minimum = ["ite", le(total, c), zero, sub(total, c)]
        delta = add(scale(1 - fraction, minimum), scale(fraction, first))
        active = le(add(second, third), c)
        spare = Q(query.get("singleton_spare", "0"))
        assert spare >= 0
        cap_a = sub(add(n(1 - c0), first), delta)
        cap_b, cap_d = sub(one, add(first, third)), sub(one, add(first, second))
        if spare:
            active = conjunction(active, le(n(2*spare), add(sub(c, total), delta)),
                                 le(n(spare), cap_b), le(n(spare), cap_d))
            cap_a, cap_b, cap_d = add(cap_a, n(2*spare)), sub(cap_b, n(spare)), sub(cap_d, n(spare))
        strict_side = query.get("strict_side")
        if strict_side is not None:
            assert not spare and strict_side in ("b", "d")
            assert configuration.get("strict_response_atoms", False)
            strict_level = query.get("strict_level", "largest")
            assert strict_level in ("largest", "middle")
            limit = u if strict_level == "largest" else vv
            old_cap = cap_b if strict_side == "b" else cap_d
            spend = sub(add(delta, old_cap), limit)
            budget = add(sub(c, total), delta)
            active = conjunction(active, le(zero, spend), le(spend, budget), le(spend, old_cap))
            cap_a = add(cap_a, spend)
            if strict_side == "b":
                cap_b = sub(cap_b, spend)
            else:
                cap_d = sub(cap_d, spend)
        conditions = [*[le(zero, value) for value in (h, a, b, d)], le(h, delta),
                      le(a, cap_a), le(b, cap_b), le(d, cap_d),
                      le(add(h, a, b, d), one)]
        if configuration.get("strict_response_atoms", False):
            conditions.extend(implies(lt(zero, cap), lt(value, cap))
                              for value, cap in zip((h, a, b, d), (delta, cap_a, cap_b, cap_d)))
        if strict_side is not None:
            conditions.append(implies(lt(zero, limit), lt(add(h, b if strict_side == "b" else d), limit)))
        require(name + "_response", implies(active, conjunction(*conditions)))
        left, right = (third, a, add(h, b)), (second, a, add(h, d))
        good(name + "_left", left, active)
        good(name + "_right", right, active)
        if query.get("third_good", False):
            third_active = conjunction(active, eq(h, zero))
            good(name + "_third", (first, b, d), third_active)
            triple_covers(name + "_third", (first, b, d), query.get("third_covers", {}), third_active)
        triple_covers(name + "_left", left, query.get("left_covers", {}), active)
        triple_covers(name + "_right", right, query.get("right_covers", {}), active)
        masses = (h, second, third, a, sub(one, add(second, third, a)), b, d, sub(first, h))
        for index in query.get("tree", []):
            costs_fail(name + "_tree_" + str(index),
                       [affine(row, masses) for row in cover_rows["tree", index]], active)
        for index in query.get("biclique", []):
            costs_fail(name + "_zero_core_" + str(index),
                       [affine(row, (first, second, third, a, b, d))
                        for row in cover_rows["biclique", index]], conjunction(active, eq(h, zero)))
        if configuration.get("opposite_pair_response_bound", False):
            opposite_pair_covers(name, {
                1: sub(one, add(second, third, a)),
                2: sub(one, add(first, third, b)),
                3: third, 4: sub(one, add(first, second, d)),
                5: second, 6: sub(first, h), 8: sub(one, add(h, a, b, d)),
                9: a, 10: b, 12: d, 14: h,
            }, active)
        if configuration.get("rank_kernel_response_bounds", False):
            kernel_rank_rows(name, {
                1: sub(one, add(second, third, a)),
                2: sub(one, add(first, third, b)),
                3: third, 4: sub(one, add(first, second, d)),
                5: second, 6: sub(first, h), 8: sub(one, add(h, a, b, d)),
                9: a, 10: b, 12: d, 14: h,
            }, 4, active)
        if configuration.get("matching_four_response_bounds", False):
            matching_four_covers(name, {
                1: sub(one, add(second, third, a)),
                2: sub(one, add(first, third, b)),
                3: third, 4: sub(one, add(first, second, d)),
                5: second, 6: sub(first, h), 8: sub(one, add(h, a, b, d)),
                9: a, 10: b, 12: d, 14: h,
            }, active)
        if configuration.get("direct_three_query_response_bounds", False):
            direct_three_query_covers(name, {
                1: sub(one, add(second, third, a)),
                2: sub(one, add(first, third, b)),
                3: third, 4: sub(one, add(first, second, d)),
                5: second, 6: sub(first, h), 8: sub(one, add(h, a, b, d)),
                9: a, 10: b, 12: d, 14: h,
            }, active)
        if configuration.get("two_split_three_query_response_bounds", False):
            two_split_three_query_covers(name, {
                1: sub(one, add(second, third, a)),
                2: sub(one, add(first, third, b)),
                3: third, 4: sub(one, add(first, second, d)),
                5: second, 6: sub(first, h), 8: sub(one, add(h, a, b, d)),
                9: a, 10: b, 12: d, 14: h,
            }, active)
        if configuration.get('replicated_pair_three_query_response_bounds', False):
            replicated_pair_three_query_covers(name, {
                1: sub(one, add(second, third, a)),
                2: sub(one, add(first, third, b)),
                3: third, 4: sub(one, add(first, second, d)),
                5: second, 6: sub(first, h), 8: sub(one, add(h, a, b, d)),
                9: a, 10: b, 12: d, 14: h,
            }, active)
        if configuration.get('complementary_split_three_query_response_bounds', False):
            complementary_split_three_query_covers(name, {
                1: sub(one, add(second, third, a)),
                2: sub(one, add(first, third, b)),
                3: third, 4: sub(one, add(first, second, d)),
                5: second, 6: sub(first, h), 8: sub(one, add(h, a, b, d)),
                9: a, 10: b, 12: d, 14: h,
            }, active)

    two_pair_data = {}
    for query in configuration.get('two_pair_queries', []):
        name, order, theta = query['name'], query['order'], Q(query['fraction'])
        assert name.isalnum() and name not in names and sorted(order) == [0, 1, 2]
        assert 0 <= theta <= 1 and configuration.get('strict_response_atoms', False)
        names.add(name)
        pp, qq, rr = [(u, vv, w)[i] for i in order]
        aa, bb, dd = sub(one, add(pp, qq)), sub(one, add(qq, rr)), sub(one, add(pp, rr))
        spare = sub(c, add(aa, rr))
        available_p, available_q, replacement_trace = pp, qq, None
        replacement_index = query.get('cyclic_replacement_index')
        selection_active = True
        if replacement_index is not None:
            assert replacement_index in range(3) and order[2] == replacement_index
            assert not query.get('base_only', False)
            assert configuration.get('joint_cyclic_minimum_pair_union', False)
            assert configuration.get('joint_cyclic_minimum_total_trace', False)
            assert configuration.get('large_rank_additive', 0) >= 8
            selected_names = configuration['joint_two_pair_queries']
            assert len(selected_names) == 3 and all(name in two_pair_data for name in selected_names)
            selection_active = conjunction(*[two_pair_data[name][1] for name in selected_names])
            prefix = configuration.get('joint_atom_prefix', 'joint_tp_atom_')
            selected_atoms = {mask: v(prefix+str(mask)) for mask in range(1, 64) if mask & 7 != 7}
            available_p, available_q = [add(*[
                mass for mask, mass in selected_atoms.items()
                if mask & 7 == 7 ^ (1 << index) and mask >> 3]) for index in order[:2]]
            replacement_trace = add(*[mass for mask, mass in selected_atoms.items()
                                     if (mask & 7).bit_count() == 2 and mask >> (3+replacement_index) & 1])
            spare = sub(c, add(aa, rr, sub(pp, available_p), sub(qq, available_q)))
        if query.get('base_only', False):
            active = le(zero, spare)
            spend_b = spend_p = zero
        else:
            active = conjunction(le(zero, spare), le(spare, add(available_p, bb)))
            if replacement_index is not None:
                active = conjunction(selection_active, active)
            lo = ['ite', le(zero, sub(spare, available_p)), sub(spare, available_p), zero]
            hi = ['ite', le(bb, spare), bb, spare]
            spend_b = add(scale(1-theta, lo), scale(theta, hi))
            spend_p = sub(spare, spend_b)
        h, g, b, d = [v(name+'_'+suffix) for suffix in 'hgbd']
        caps = (available_q, sub(available_p, spend_p), sub(bb, spend_b), dd)
        conditions = [*[le(zero, value) for value in (h, g, b, d)], le(add(h, g, b, d), one)]
        if replacement_trace is not None:
            conditions.append(le(replacement_trace, add(h, g)))
        conditions.extend(le(value, cap) for value, cap in zip((h, g, b, d), caps))
        conditions.extend(implies(lt(zero, cap), lt(value, cap))
                          for value, cap in zip((h, g, b, d), caps))
        actual = (add(h, g), add(h, b), add(g, d))
        conditions.extend(disjunction(le(value, x), le(y, value)) for value in actual)
        if pair_gap:
            conditions.extend(disjunction(le(u, value), lt(add(scale(2, u), value), n(2-c0)))
                              for value in actual)
        require(name+'_response', implies(active, conjunction(*conditions)))
        good_values = ((rr, actual[1], actual[2]), (qq, g, b), (pp, h, d))
        guards = (active, conjunction(active, eq(h, zero)), conjunction(active, eq(g, zero)))
        for index, (values, guard) in enumerate(zip(good_values, guards)):
            label = name+'_good_'+str(index)
            good(label, values, guard)
            triple_covers(label, values, query.get('good_covers', {'static': [439, 449]}), guard)
        from global_structural_templates import common_core_rows
        for index, point in enumerate(((one, h, sub(qq, h), g, b, n(3-2*c0)),
                                       (one, g, sub(pp, g), h, d, n(3-2*c0)))):
            for template, rows in enumerate(common_core_rows(distributed=False)):
                costs_fail(name+'_core_'+str(index)+'_'+str(template),
                           [affine(row, point) for row in rows], active)
        masses = {1: aa, 2: sub(bb, b), 3: sub(qq, h), 4: sub(dd, d),
                  5: sub(pp, g), 6: rr, 8: sub(one, add(h, g, b, d)),
                  10: b, 11: h, 12: d, 13: g}
        two_pair_data[name] = (order, active, masses)
        if configuration.get('direct_three_query_response_bounds', False):
            direct_three_query_covers(name, masses, active)
        if configuration.get('two_split_three_query_response_bounds', False):
            two_split_three_query_covers(name, masses, active)
        if configuration.get('replicated_pair_three_query_response_bounds', False):
            replicated_pair_three_query_covers(name, masses, active)
        if configuration.get('complementary_split_three_query_response_bounds', False):
            complementary_split_three_query_covers(name, masses, active)
        if response_graph_supports:
            catalogue_three_query_covers(name, masses, active)
        if configuration.get('opposite_pair_response_bound', False):
            opposite_pair_covers(name, masses, active)
        if configuration.get('rank_kernel_response_bounds', False):
            kernel_rank_rows(name, masses, 4, active)

    joint_names = configuration.get('joint_two_pair_queries', [])
    if joint_names:
        assert len(joint_names) == len(set(joint_names)) and 1 <= len(joint_names) <= 4
        assert all(name in two_pair_data for name in joint_names)
        count = 3+len(joint_names)
        atom_prefix = configuration.get('joint_atom_prefix', 'joint_tp_atom_')
        assert isinstance(atom_prefix, str) and atom_prefix.isidentifier() and atom_prefix.endswith('_')
        atoms = {mask: v(atom_prefix+str(mask)) for mask in range(1, 1 << count)
                 if mask & 7 != 7}
        require('joint_tp_nonnegative', conjunction(*[le(zero, value) for value in atoms.values()]))
        for row in range(count):
            require('joint_tp_rank_'+str(row),
                    eq(add(*[value for mask, value in atoms.items() if mask >> row & 1]), one))

        def marginal(rows):
            groups = {mask: [] for mask in range(1, 1 << len(rows))}
            for mask, value in atoms.items():
                image = sum(1 << i for i, row in enumerate(rows) if mask >> row & 1)
                if image:
                    groups[image].append(value)
            return {mask: add(*values) if values else zero for mask, values in groups.items()}

        root = marginal((0, 1, 2))
        for mask, value in zip((6, 5, 3), (u, vv, w)):
            require('joint_tp_root_'+str(mask), eq(root[mask], value))
        for index, name in enumerate(joint_names):
            order, active, masses = two_pair_data[name]
            # Pair index i is the root row missing from that pair.
            groups = marginal((order[2], order[0], order[1], 3+index))
            for mask in range(1, 16):
                require('joint_tp_'+name+'_marginal_'+str(mask),
                        implies(active, eq(groups[mask], masses.get(mask, zero))))
        if configuration.get('joint_cyclic_minimum_pair_union', False):
            assert len(joint_names) == 3
            query_by_name = {query['name']: query for query in configuration['two_pair_queries']}
            assert all(query_by_name[name].get('base_only', False)
                       and two_pair_data[name][0][2] == i for i, name in enumerate(joint_names))
            eligible = conjunction(*[two_pair_data[name][1] for name in joint_names])
            available_union, thresholds = [], []
            for i in range(3):
                private = add(*[mass for mask, mass in atoms.items()
                                if (mask & 7).bit_count() == 2 and mask >> 3 == 1 << i])
                touched = []
                for j in range(3):
                    if i == j:
                        continue
                    other = 3-i-j
                    touched.extend(mass for mask, mass in atoms.items()
                                   if mask & 7 == 7 ^ (1 << j) and mask >> (3+other) & 1)
                require('joint_tp_cyclic_minimum_'+str(i), implies(eligible, disjunction(
                    eq(private, zero), lt(add(*touched), add(n(1-c0), (u, vv, w)[i])))))
                threshold = add(n(1-c0), (u, vv, w)[i])
                available_union.append(add(private, *touched))
                thresholds.append(threshold)
                if configuration.get('joint_cyclic_single_point_exchange', False):
                    require('joint_tp_cyclic_single_point_'+str(i), implies(eligible, disjunction(
                        eq(private, zero), lt(add(private, *touched), threshold))))
                if configuration.get('joint_cyclic_minimum_total_trace', False):
                    assert 0 < c0 < 1
                    trace = add(*[mass for mask, mass in atoms.items()
                                  if (mask & 7).bit_count() == 2 and mask >> (3+i) & 1])
                    require('joint_tp_cyclic_trace_'+str(i), implies(eligible, lt(trace, threshold)))
            if configuration.get('joint_cyclic_simultaneous_exchange', False):
                for i in range(3):
                    center = atoms[(7 ^ (1 << i)) | ((7 ^ (1 << i)) << 3)]
                    require('joint_tp_cyclic_simultaneous_'+str(i), implies(eligible, disjunction(
                        eq(center, zero), *[lt(available_union[j], thresholds[j])
                                           for j in range(3) if j != i])))
        else:
            assert not configuration.get('joint_cyclic_single_point_exchange', False)
            assert not configuration.get('joint_cyclic_minimum_total_trace', False)
            assert not configuration.get('joint_cyclic_simultaneous_exchange', False)
        full = (1 << count)-1
        require('joint_tp_two_transversal', disjunction(*[
            conjunction(lt(zero, atoms[first]), lt(zero, atoms[second]))
            for first, second in combinations(atoms, 2) if first | second == full]))
        for rows in combinations(range(count), 2):
            pair = marginal(rows)[3]
            conditions = [disjunction(le(pair, x), le(y, pair))]
            if pair_gap:
                conditions.append(disjunction(le(u, pair), lt(add(scale(2, u), pair), n(2-c0))))
            require('joint_tp_pair_'+''.join(map(str, rows)), conjunction(*conditions))
        from global_structural_templates import common_core_rows
        core_templates = common_core_rows(distributed=False)
        for rows in combinations(range(count), 3):
            groups = marginal(rows)
            core = groups[7]
            values = tuple(groups[mask] for mask in (6, 5, 3))
            label = 'joint_tp_triple_'+''.join(map(str, rows))
            active = eq(core, zero)
            good(label, values, active)
            triple_covers(label, values, {'static': [439, 449]}, active)
            point = (one, core, *values, n(3-2*c0))
            for index, costs in enumerate(core_templates):
                costs_fail(label+'_core_'+str(index), [affine(row, point) for row in costs])
        for rows in combinations(range(count), 4):
            groups = marginal(rows)
            label = 'joint_tp_four_'+''.join(map(str, rows))
            if configuration.get('direct_three_query_response_bounds', False):
                direct_three_query_covers(label, groups, True)
            if configuration.get('two_split_three_query_response_bounds', False):
                two_split_three_query_covers(label, groups, True)
            if configuration.get('replicated_pair_three_query_response_bounds', False):
                replicated_pair_three_query_covers(label, groups, True)
            if configuration.get('complementary_split_three_query_response_bounds', False):
                complementary_split_three_query_covers(label, groups, True)
            if response_graph_supports:
                catalogue_three_query_covers(label, groups, True)

        if configuration.get('joint_kernel_hierarchy', False):
            lower = {6: c0}
            for size in (5, 4, 3):
                lower[size] = Q(size, 2*size-2)*min(lower[size+1]+c0, Q(2))
            for size in range(3, min(count, 6)+1):
                full = (1 << size)-1
                for rows in combinations(range(count), size):
                    groups = marginal(rows)
                    active = eq(groups[full], zero)
                    endpoint = {mask: ['ite', disjunction(*[
                        lt(zero, other_mass) for other, other_mass in groups.items()
                        if mask | other == full]), mass, zero] for mask, mass in groups.items()}
                    total = add(*endpoint.values())
                    label = 'joint_tp_kernel_'+''.join(map(str, rows))
                    require(label+'_mass', implies(active, (lt if size == 6 else le)(n(lower[size]), total)))
                    if size == 6:
                        continue
                    for row in range(size):
                        inside = add(*[mass for mask, mass in endpoint.items() if mask >> row & 1])
                        require(label+'_row_'+str(row), implies(active,
                                lt(n(lower[size+1]+c0), add(total, inside))))
                    if configuration.get('joint_independent_kernel_inequalities', False):
                        from incidence_independent_sets import catalogue
                        for index, selected in enumerate(catalogue(size)):
                            independent = add(*[endpoint[mask] for mask in selected])
                            require(label+'_independent_'+str(index), implies(active,
                                    lt(n(lower[size+1]+c0), sub(scale(2, total), independent))))

        if configuration.get('joint_two_pair_affine_cover_file'):
            from verify_affine_partial_endpoint_cover import verify as verify_basis
            saved = json.loads((ROOT / configuration['joint_two_pair_affine_cover_file']).read_text())
            basis_audits = []
            for index, record in enumerate(saved['checks']):
                if 'basis_certificate' not in record:
                    continue
                certificate = record['basis_certificate']
                rows = record['rows']
                assert len(rows) == len(set(rows)) and all(0 <= row < count for row in rows)
                assert len(rows)+certificate['blocks'] == 7 and certificate['complete_graph_cover']
                full = (1 << len(rows))-1
                zeros = set(record['zero_masks'])
                assert full in zeros and zeros <= set(range(full+1))
                permitted = sorted(set(range(full+1))-zeros)
                edges = [(a, b) for a, b in combinations(permitted, 2) if a | b == full]
                active_masks = sorted({mask for edge in edges for mask in edge})
                assert active_masks == record['active_masks']
                lookup = {mask: i for i, mask in enumerate(active_masks)}
                assert certificate['adjacent'] == [[lookup[a], lookup[b]] for a, b in edges]
                basis_audits.append(verify_basis(certificate))
                groups = {0: zero, **marginal(rows)}
                point = [groups[mask] for mask in active_masks]+[c]*certificate['blocks']
                guard = conjunction(*[eq(groups[mask], zero) for mask in sorted(zeros)])
                require('joint_tp_affine_cover_'+str(index), implies(guard, disjunction(*[
                    lt(affine(row, point), zero) for row in certificate['inverse_rows']])))
            audit['joint_complete_cover_certificates'] = {
                'certificates': len(basis_audits),
                'inverse_equalities': sum(item['matrix_inverse_equalities'] for item in basis_audits),
                'integer_constructions': sum(item['integer_constructions'] for item in basis_audits)}

        if configuration.get('joint_lift_source_configuration'):
            previous_config = json.loads((ROOT/configuration['joint_lift_source_configuration']).read_text())
            assert Q(previous_config['coefficient']) == c0 and previous_config['gap'] == configuration['gap']
            assert previous_config['two_pair_queries'] == configuration['two_pair_queries']
            previous_names = previous_config['joint_two_pair_queries']
            assert joint_names[:len(previous_names)] == previous_names and len(previous_names) < len(joint_names)
            previous_count = 3+len(previous_names)
            previous_prefix = previous_config.get('joint_atom_prefix', 'joint_tp_atom_')
            assert previous_prefix != atom_prefix
            previous_model = formulas(previous_config)
            for label, formula in zip(previous_model['labels'], previous_model['formulas']):
                require('retained_'+label, formula)
            groups = marginal(tuple(range(previous_count)))
            linked = 0
            for mask in range(1, 1 << previous_count):
                if mask & 7 != 7:
                    require('joint_tp_lift_'+str(mask), eq(v(previous_prefix+str(mask)), groups[mask]))
                    linked += 1
            audit['joint_lift'] = {'retained_formula_groups': len(previous_model['formulas']),
                                   'old_rows': previous_count, 'marginal_equalities': linked}

    for fraction in map(Q, configuration["minimum_large_fractions"]):
        name = "Y_" + str(fraction.numerator) + "_" + str(fraction.denominator)
        a, b = v(name + "_a"), v(name + "_b")
        active = le(y, c)
        cap_a = add(n(1 - c0), scale(fraction, sub(c, y)))
        cap_b = sub(sub(n(2 - c0), y), cap_a)
        require(name + "_response", implies(active, conjunction(le(zero, a), le(zero, b),
                                                                 le(a, cap_a), le(b, cap_b), le(add(a, b), one))))
        if configuration.get("strict_response_atoms", False):
            require(name + "_strict_atoms", implies(active, conjunction(
                implies(lt(zero, cap_a), lt(a, cap_a)), implies(lt(zero, cap_b), lt(b, cap_b)))))
        good(name + "_good", (y, a, b), active)
        triple_covers(name, (y, a, b), configuration.get("minimum_large_covers", {}), active)
    return {"formulas": result, "labels": labels, "support_audit": audit,
            "coefficient": str(c0), "gap": [str(alpha), str(beta)]}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("configuration", type=Path)
    args = parser.parse_args()
    print(json.dumps(formulas(json.loads(args.configuration.read_text())), indent=2))
