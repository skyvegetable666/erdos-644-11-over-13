"""Small exact arithmetic/CNF layer for independently checked refutations.

No SMT, SAT, numerical optimizer, or discovery module is imported here.
Atoms mean an integer affine expression is nonpositive.
"""

from fractions import Fraction as Q
from functools import reduce
from math import gcd, lcm


def plus(*rows):
    result = {}
    for row in rows:
        for variable, value in row.items():
            result[variable] = result.get(variable, Q(0)) + value
    return {key: value for key, value in result.items() if value}


def times(coefficient, row):
    return {key: coefficient * value for key, value in row.items() if coefficient * value}


def negate(literal):
    return not literal if isinstance(literal, bool) else -literal


class Compiler:
    def __init__(self):
        self.count = 0
        self.atoms = {}
        self.atom_indices = {}
        self.clauses = []
        self.connectives = {}
        self.ites = {}

    def fresh(self):
        self.count += 1
        return self.count

    def clause(self, literals):
        if any(literal is True for literal in literals):
            return
        values = {literal for literal in literals if literal is not False}
        if any(-literal in values for literal in values):
            return
        self.clauses.append(sorted(values, key=lambda value: (abs(value), value)))

    def combine(self, kind, literals):
        literals = list(literals)
        absorbing = kind == "or"
        if any(value is absorbing for value in literals):
            return absorbing
        values = {value for value in literals if value is not (not absorbing)}
        if any(negate(value) in values for value in values):
            return absorbing
        if not values:
            return not absorbing
        if len(values) == 1:
            return next(iter(values))
        key = (kind, tuple(sorted(values)))
        if key in self.connectives:
            return self.connectives[key]
        result = self.fresh()
        self.connectives[key] = result
        if kind == "and":
            for value in values:
                self.clause([-result, value])
            self.clause([result, *[-value for value in values]])
        else:
            for value in values:
                self.clause([result, -value])
            self.clause([-result, *values])
        return result

    def atom(self, row):
        if not any(variable for variable in row):
            return row.get("", Q(0)) <= 0
        denominator = lcm(*(value.denominator for value in row.values()))
        integers = {variable: int(value * denominator) for variable, value in row.items() if value}
        divisor = reduce(gcd, (abs(value) for value in integers.values()))
        key = tuple(sorted((variable, value // divisor) for variable, value in integers.items()))
        if key not in self.atom_indices:
            index = self.fresh()
            self.atom_indices[key] = index
            self.atoms[index] = dict(key)
        return self.atom_indices[key]

    def linear(self, expression):
        kind, *children = expression
        if kind == "num":
            return plus({"": Q(children[0])})
        if kind == "var":
            return {children[0]: Q(1)}
        if kind == "add":
            return plus(*(self.linear(child) for child in children))
        if kind == "mul":
            return times(Q(children[0]), self.linear(children[1]))
        if kind == "ite":
            key = repr(expression)
            if key not in self.ites:
                name = "__piecewise_" + str(len(self.ites))
                self.ites[key] = name
                guard = self.boolean(children[0])
                for condition, branch in ((guard, children[1]), (negate(guard), children[2])):
                    difference = plus({name: Q(1)}, times(Q(-1), self.linear(branch)))
                    self.clause([negate(condition), self.atom(difference)])
                    self.clause([negate(condition), self.atom(times(Q(-1), difference))])
            return {self.ites[key]: Q(1)}
        raise ValueError(("nonlinear or unsupported expression", expression))

    def boolean(self, expression):
        if isinstance(expression, bool):
            return expression
        kind, *children = expression
        if kind == "not":
            return negate(self.boolean(children[0]))
        if kind in ("and", "or"):
            return self.combine(kind, [self.boolean(child) for child in children])
        if kind == "implies":
            return self.combine("or", [negate(self.boolean(children[0])), self.boolean(children[1])])
        if kind in ("le", "lt", "eq"):
            difference = plus(self.linear(children[0]), times(Q(-1), self.linear(children[1])))
            if kind == "le":
                return self.atom(difference)
            if kind == "lt":
                return negate(self.atom(times(Q(-1), difference)))
            return self.combine("and", [self.atom(difference), self.atom(times(Q(-1), difference))])
        raise ValueError(("unsupported Boolean expression", expression))

    def require(self, expression):
        self.clause([self.boolean(expression)])


def contradiction(atoms, weighted_literals):
    """Check a Farkas certificate for the negation of a clause."""
    total, strict = {}, False
    assert weighted_literals
    for literal, raw_weight in weighted_literals:
        assert isinstance(literal, int) and literal and abs(literal) in atoms
        weight = Q(raw_weight)
        assert weight > 0
        # Negating a positive clause literal makes a strict reversed row.
        total = plus(total, times(-weight if literal > 0 else weight, atoms[abs(literal)]))
        strict |= literal > 0
    assert all(not value for variable, value in total.items() if variable)
    constant = total.get("", Q(0))
    assert constant > 0 or (constant == 0 and strict)


def check_rup(clauses, proof):
    """Check additions by reverse unit propagation; deletions are optional."""
    database = [set(clause) for clause in clauses]
    assert all(all(isinstance(literal, int) and literal for literal in clause) for clause in database)
    checked = 0
    has_empty = any(not clause for clause in database)
    for line in proof:
        if isinstance(line, str):
            pieces = line.split()
            if pieces and pieces[0] == "d":
                continue
            assert pieces and pieces[-1] == "0"
            clause = {int(value) for value in pieces[:-1]}
        else:
            clause = set(line)
        assert all(type(literal) is int and literal for literal in clause)
        assigned = {-literal for literal in clause}
        conflict = any(-literal in assigned for literal in assigned)
        while not conflict:
            changed = False
            for old in database:
                if old & assigned:
                    continue
                remaining = old - {-literal for literal in assigned}
                if not remaining:
                    conflict = True
                    break
                if len(remaining) == 1:
                    literal = next(iter(remaining))
                    if -literal in assigned:
                        conflict = True
                        break
                    if literal not in assigned:
                        assigned.add(literal)
                        changed = True
            if not changed:
                break
        assert conflict, ("non-RUP proof addition", checked, sorted(clause))
        database.append(clause)
        has_empty |= not clause
        checked += 1
    assert has_empty, "The proof must derive the empty clause"
    return checked
