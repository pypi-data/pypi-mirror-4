"""
Boolean Logic Expressions

Interface Functions:
    var

    iter_cubes

    factor
    simplify

    Nor, Nand
    OneHot0, OneHot

    f_not
    f_or, f_nor
    f_and, f_nand
    f_xor, f_xnor
    f_equal
    f_implies

Interface Classes:
    Expression
        Literal
            Variable
            Complement
        OrAnd
            Or
            And
        Not
        Exclusive
            Xor
            Xnor
        Equal
        Implies
        ITE
"""

from collections import deque, OrderedDict

from pyeda import boolfunc
from pyeda import sat
from pyeda.common import bit_on, boolify, cached_property

B = {0, 1}

def var(name, indices=None, namespace=None):
    """Return a variable expression.

    Parameters
    ----------

    name : str
        The variable's identifier string.
    indices : int or tuple[int], optional
        One or more integer suffixes for variables that are part of a
        multi-dimensional bit-vector, eg x[1], x[1][2][3]
    namespace : str, optional
        A container for a set of variables. Since a Variable instance is global,
        a namespace can be used for local scoping.
    """
    return Variable(name, indices, namespace)

def iter_cubes(vs):
    for n in range(2 ** len(vs)):
        yield tuple(v if bit_on(n, i) else -v for i, v in enumerate(vs))

def factor(expr):
    """Return a factored expression."""
    if expr in B:
        return expr
    else:
        return expr.factor()

def simplify(expr):
    """Return a simplified expression."""
    if expr in B:
        return expr
    else:
        return expr.simplify()

# convenience functions
def Nor(*args):
    """Alias for Not Or"""
    return Not(Or(*args))

def Nand(*args):
    """Alias for Not And"""
    return Not(And(*args))

def OneHot0(*args):
    """
    Return an expression that means:
        At most one input variable is true.
   """
    nargs = len(args)
    return And(*[Or(Not(args[i]), Not(args[j]))
                 for i in range(nargs-1) for j in range(i+1, nargs)])

def OneHot(*args):
    """
    Return an expression that means:
        Exactly one input variable is true.
    """
    return And(Or(*args), OneHot0(*args))

# factored operators
def f_not(arg):
    """Return factored NOT expression."""
    f = Not(arg).factor()
    return f if f in B else f.factor()

def f_or(*args):
    """Return factored OR expression."""
    f = Or(*args).factor()
    return f if f in B else f.factor()

def f_nor(*args):
    """Return factored NOR expression."""
    f = Nor(*args).factor()
    return f if f in B else f.factor()

def f_and(*args):
    """Return factored AND expression."""
    f = And(*args).factor()
    return f if f in B else f.factor()

def f_nand(*args):
    """Return factored NAND expression."""
    f = Nand(*args).factor()
    return f if f in B else f.factor()

def f_xor(*args):
    """Return factored XOR expression."""
    f = Xor(*args).factor()
    return f if f in B else f.factor()

def f_xnor(*args):
    """Return factored XNOR expression."""
    f = Xnor(*args).factor()
    return f if f in B else f.factor()

def f_equal(*args):
    """Return factored Equal expression."""
    f = Equal(*args).factor()
    return f if f in B else f.factor()

def f_implies(p, q):
    """Return factored Implies expression."""
    f = Implies(p, q).factor()
    return f if f in B else f.factor()

def f_ite(s, a, b):
    """Return factored if-then-else expression."""
    f = ITE(s, a, b).factor()
    return f if f in B else f.factor()


class Expression(boolfunc.Function):
    """Boolean function represented by a logic expression"""

    SOP, POS = range(2)

    # From Function
    @cached_property
    def support(self):
        """Return the support set of an expression."""
        s = set()
        for arg in self._args:
            s |= arg.support
        return s

    @cached_property
    def inputs(self):
        return sorted(self.support)

    def __neg__(self):
        """Boolean negation

        DIMACS SAT format: -f

        +---+----+
        | f | -f |
        +---+----+
        | 0 |  1 |
        | 1 |  0 |
        +---+----+
        """
        return Not(self)

    def __add__(self, arg):
        """Boolean disjunction (addition, OR)

        DIMACS SAT format: +(f1, f2, ..., fn)

        +---+---+-------+
        | f | g | f + g |
        +---+---+-------+
        | 0 | 0 |   0   |
        | 0 | 1 |   1   |
        | 1 | 0 |   1   |
        | 1 | 1 |   1   |
        +---+---+-------+
        """
        return Or(self, arg)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, arg):
        """Alias: a - b = a + -b"""
        return Or(self, Not(arg))

    def __rsub__(self, other):
        return self.__neg__().__add__(other)

    def __mul__(self, arg):
        """Boolean conjunction (multiplication, AND)

        DIMACS SAT format: *(f1, f2, ..., fn)

        +---+---+-------+
        | f | g | f * g |
        +---+---+-------+
        | 0 | 0 |   0   |
        | 0 | 1 |   0   |
        | 1 | 0 |   0   |
        | 1 | 1 |   1   |
        +---+---+-------+
        """
        return And(self, arg)

    def __rmul__(self, other):
        return self.__mul__(other)

    def xor(self, *args):
        """Boolean XOR (odd parity)

        DIMACS SAT format: xor(f1, f2, ..., fn)

        +---+---+----------+
        | f | g | XOR(f,g) |
        +---+---+----------+
        | 0 | 0 |     0    |
        | 0 | 1 |     1    |
        | 1 | 0 |     1    |
        | 1 | 1 |     0    |
        +---+---+----------+
        """
        return Xor(self, *args)

    def equal(self, *args):
        """Boolean equality

        DIMACS SAT format: =(f1, f2, ..., fn)

        +-------+-----------+
        | f g h | EQ(f,g,h) |
        +-------+-----------+
        | 0 0 0 |     1     |
        | 0 0 1 |     0     |
        | 0 1 0 |     0     |
        | 0 1 1 |     0     |
        | 1 0 0 |     0     |
        | 1 0 1 |     0     |
        | 1 1 0 |     0     |
        | 1 1 1 |     1     |
        +-------+-----------+
        """
        return Equal(self, *args)

    def __rshift__(self, arg):
        """Boolean implication

        +---+---+--------+
        | f | g | f -> g |
        +---+---+--------+
        | 0 | 0 |    1   |
        | 0 | 1 |    1   |
        | 1 | 0 |    0   |
        | 1 | 1 |    1   |
        +---+---+--------+
        """
        return Implies(self, arg)

    def __rrshift__(self, arg):
        """Reverse Boolean implication

        +---+---+--------+
        | f | g | f <- g |
        +---+---+--------+
        | 0 | 0 |    1   |
        | 0 | 1 |    0   |
        | 1 | 0 |    1   |
        | 1 | 1 |    1   |
        +---+---+--------+
        """
        return Implies(arg, self)

    def ite(self, a, b):
        """If-then-else operator"""
        return ITE(self, a, b)

    def expand(self, vs=None, dnf=True):
        """Return the Shannon expansion with respect to a list of variables."""
        if vs is None:
            vs = list()
        elif isinstance(vs, Expression):
            vs = [vs]
        if vs:
            if dnf:
                return Or(*[And(self, *cube) for cube in iter_cubes(vs)])
            else:
                return And(*[Or(self, *cube) for cube in iter_cubes(vs)])
        else:
            return self

    def reduce(self, dnf=True):
        if dnf:
            return self.to_cdnf()
        else:
            return self.to_ccnf()

    def satisfy_one(self, algorithm='dpll'):
        if algorithm == 'backtrack':
            return sat.backtrack(self)
        elif algorithm == 'dpll':
            if self.is_cnf():
                return sat.dpll(self)
            else:
                raise TypeError("expression is not a CNF")
        else:
            raise ValueError("invalid algorithm")

    def satisfy_all(self):
        """Iterate through all satisfying input points."""
        for point in self.iter_ones():
            yield point

    def satisfy_count(self):
        return sum(1 for _ in self.satisfy_all())

    def is_neg_unate(self, vs=None):
        """Return whether a function is negative unate."""
        if vs is None:
            vs = self.support
        elif isinstance(vs, boolfunc.Function):
            vs = [vs]
        for v in vs:
            fv0, fv1 = self.cofactors(v)
            if fv0 in B or fv1 in B:
                if not (fv0 == 1 or fv1 == 0):
                    return False
            elif not fv0.min_indices >= fv1.min_indices:
                return False
        return True

    def is_pos_unate(self, vs=None):
        """Return whether a function is positive unate."""
        if vs is None:
            vs = self.support
        elif isinstance(vs, boolfunc.Function):
            vs = [vs]
        for v in vs:
            fv0, fv1 = self.cofactors(v)
            if fv0 in B or fv1 in B:
                if not (fv1 == 1 or fv0 == 0):
                    return False
            elif not fv1.min_indices >= fv0.min_indices:
                return False
        return True

    def smoothing(self, vs=None):
        """Return the smoothing of a function."""
        return Or(*self.cofactors(vs))

    def consensus(self, vs=None):
        """Return the consensus of a function."""
        return And(*self.cofactors(vs))

    def derivative(self, vs=None):
        """Return the derivative of a function."""
        return Xor(*self.cofactors(vs))

    # Specific to Expression
    def __lt__(self, other):
        """Implementing this function makes expressions sortable."""
        return id(self) < id(other)

    def __repr__(self):
        """Return a printable representation."""
        return self.__str__()

    @property
    def args(self):
        """Return the expression argument list."""
        return self._args

    @cached_property
    def arg_set(self):
        """Return the expression arguments as a set."""
        return set(self._args)

    @property
    def depth(self):
        """Return the number of levels in the expression tree."""
        raise NotImplementedError()

    def invert(self):
        """Return an inverted expression."""
        raise NotImplementedError()

    def factor(self):
        """Return a factored expression.

        A factored expression is one and only one of the following:
        * A literal.
        * A disjunction / conjunction of factored expressions.
        """
        raise NotImplementedError()

    def simplify(self):
        """Return a simplified expression."""
        return self

    def iter_minterms(self):
        """Iterate through the sum of products of N literals."""
        for point in self.iter_ones():
            space = [(v if val else -v) for v, val in point.items()]
            yield And(*space)

    @cached_property
    def minterms(self):
        """The sum of products of N literals"""
        return {term for term in self.iter_minterms()}

    def iter_maxterms(self):
        """Iterate through the product of sums of N literals."""
        for point in self.iter_zeros():
            space = [(-v if val else v) for v, val in point.items()]
            yield Or(*space)

    @cached_property
    def maxterms(self):
        """The product of sums of N literals"""
        return {term for term in self.iter_maxterms()}

    def is_dnf(self):
        """Return whether this expression is in disjunctive normal form."""
        return False

    def to_dnf(self):
        """Return the expression in disjunctive normal form.

        >>> a, b, c = map(var, "abc")
        >>> Xor(a, b, c).to_dnf()
        a' * b' * c + a' * b * c' + a * b' * c' + a * b * c
        >>> Xnor(a, b, c).to_dnf()
        a' * b' * c' + a' * b * c + a * b' * c + a * b * c'
        """
        f = self.factor()._flatten(And)
        return f.absorb() if isinstance(f, Expression) else f

    def to_cdnf(self):
        """Return the expression in canonical disjunctive normal form.

        >>> a, b, c = map(var, "abc")
        >>> (a * b + a * c + b * c).to_cdnf()
        a' * b * c + a * b' * c + a * b * c' + a * b * c
        """
        return Or(*[term for term in self.iter_minterms()])

    def is_cnf(self):
        """Return whether this expression is in conjunctive normal form."""
        return False

    def to_cnf(self):
        """Return the expression in conjunctive normal form.

        >>> a, b, c = map(var, "abc")
        >>> Xor(a, b, c).to_cnf()
        (a + b + c) * (a + b' + c') * (a' + b + c') * (a' + b' + c)
        >>> Xnor(a, b, c).to_cnf()
        (a + b + c') * (a + b' + c) * (a' + b + c) * (a' + b' + c')
        """
        f = self.factor()._flatten(Or)
        return f.absorb() if isinstance(f, Expression) else f

    def to_ccnf(self):
        """Return the expression in canonical conjunctive normal form.

        >>> a, b, c = map(var, "abc")
        >>> (a * b + a * c + b * c).to_ccnf()
        (a + b + c) * (a + b + c') * (a + b' + c) * (a' + b + c)
        """
        return And(*[term for term in self.iter_maxterms()])

    @cached_property
    def min_indices(self):
        """Return the minterm indices.

        >>> a, b, c = map(var, "abc")
        >>> (a * b + a * c + b * c).min_indices
        set([3, 5, 6, 7])
        """
        return {term.minterm_index for term in self.iter_minterms()}

    @cached_property
    def max_indices(self):
        """Return the maxterm indices.

        >>> a, b, c = map(var, "abc")
        >>> (a * b + a * c + b * c).max_indices
        set([0, 1, 2, 4])
        """
        return {term.maxterm_index for term in self.iter_maxterms()}

    def equivalent(self, other):
        """Return whether this expression is equivalent to another."""
        f = And(Or(Not(self), Not(other)), Or(self, other))
        if f == 0:
            return True
        elif f == 1:
            return False
        elif f.is_cnf():
            return f.satisfy_one(algorithm='dpll') is None
        else:
            return f.satisfy_one(algorithm='backtrack') is None

    # Convenience methods
    def _get_restrictions(self, mapping):
        restrictions = dict()
        for i, arg in enumerate(self._args):
            new_arg = arg.restrict(mapping)
            if id(new_arg) != id(arg):
                restrictions[i] = new_arg
        return restrictions

    def _get_compositions(self, mapping):
        compositions = dict()
        for i, arg in enumerate(self._args):
            new_arg = arg.compose(mapping)
            if id(new_arg) != id(arg):
                compositions[i] = new_arg
        return compositions

    def _subs(self, idx_arg):
        args = list(self._args)
        for i, arg in idx_arg.items():
            args[i] = arg
        return self.__class__(*args)


class Literal(Expression):
    """An instance of a variable or of its complement"""

    # From Expression
    @property
    def depth(self):
        """Return the number of levels in the expression tree."""
        return 0

    def factor(self):
        return self

    def is_dnf(self):
        return True

    def is_cnf(self):
        return True


class Variable(boolfunc.Variable, Literal):
    """Boolean variable (expression)"""

    _MEM = OrderedDict()

    def __new__(cls, name, indices=None, namespace=None):
        try:
            self = cls._MEM[(namespace, name, indices)]
        except KeyError:
            self = boolfunc.Variable.__new__(cls, name, indices, namespace)
            self._support = {self}
            self._args = (self, )
            cls._MEM[(namespace, name, indices)] = self
        return self

    # From Function
    @property
    def support(self):
        """Return the support set of a variable."""
        return self._support

    def restrict(self, mapping):
        try:
            return boolify(mapping[self])
        except KeyError:
            return self

    def compose(self, mapping):
        try:
            return mapping[self]
        except KeyError:
            return self

    # From Expression
    def __lt__(self, other):
        """Overload the '<' operator."""
        if isinstance(other, Variable):
            return boolfunc.Variable.__lt__(self, other)
        if isinstance(other, Complement):
            return boolfunc.Variable.__lt__(self, other.var)
        if isinstance(other, Expression):
            return True
        return id(self) < id(other)

    def invert(self):
        """Return an inverted variable."""
        return Complement(self)

    # DPLL IF
    def bcp(self):
        return 1, {self: 1}

    def ple(self):
        return 1, {self: 1}

    # Specific to Variable
    @cached_property
    def gnum(self):
        for i, v in enumerate(self._MEM.values(), start=1):
            if v == self:
                return i

    @property
    def minterm_index(self):
        return 1

    @property
    def maxterm_index(self):
        return 0


class Complement(Literal):
    """Boolean complement"""

    _MEM = dict()

    def __new__(cls, v):
        try:
            self = cls._MEM[v]
        except KeyError:
            self = super(Complement, cls).__new__(cls)
            self.var = v
            self._support = {v}
            self._args = (self, )
            cls._MEM[v] = self
        return self

    def __str__(self):
        return str(self.var) + "'"

    # From Function
    @property
    def support(self):
        """Return the support set of a complement."""
        return self._support

    def restrict(self, mapping):
        try:
            return 1 - boolify(mapping[self.var])
        except KeyError:
            return self

    def compose(self, mapping):
        try:
            return Not(mapping[self.var])
        except KeyError:
            return self

    # From Expression
    def __lt__(self, other):
        """Overload the '<' operator."""
        if isinstance(other, Variable):
            return ( self.var.name < other.name or
                         self.var.name == other.name and
                         self.var.indices <= other.indices )
        if isinstance(other, Complement):
            return boolfunc.Variable.__lt__(self.var, other.var)
        if isinstance(other, Expression):
            return True
        return id(self) < id(other)

    def invert(self):
        """Return an inverted complement."""
        return self.var

    # DPLL IF
    def bcp(self):
        return 1, {self.var: 0}

    def ple(self):
        return 1, {self.var: 0}

    # Specific to Complement
    @property
    def gnum(self):
        return -self.var.gnum

    @property
    def minterm_index(self):
        return 0

    @property
    def maxterm_index(self):
        return 1


class OrAnd(Expression):
    """Base class for Boolean OR/AND expressions"""

    def __new__(cls, *args, **kwargs):
        simplify = kwargs.get('simplify', True)
        args = tuple(arg if isinstance(arg, Expression) else boolify(arg)
                     for arg in args)
        if simplify:
            degenerate, args = cls._simplify(args)
            if degenerate:
                return args

        self = super(OrAnd, cls).__new__(cls)
        self._args = args
        self._simplified = simplify
        return self

    @classmethod
    def _simplify(cls, args):
        temps, args = deque(args), list()

        while temps:
            arg = temps.popleft()
            if isinstance(arg, Expression):
                arg = arg.simplify()
            if arg == cls.DOMINATOR:
                return True, cls.DOMINATOR
            elif arg == cls.IDENTITY:
                pass
            # associative
            elif isinstance(arg, cls):
                temps.extendleft(reversed(arg.args))
            # complement
            elif isinstance(arg, Literal) and -arg in args:
                return True, cls.DOMINATOR
            # idempotent
            elif arg not in args:
                args.append(arg)

        # Or() = 0; And() = 1
        if len(args) == 0:
            return True, cls.IDENTITY
        # Or(x) = x; And(x) = x
        if len(args) == 1:
            return True, args[0]

        return False, tuple(args)

    # From Function
    def restrict(self, mapping):
        idx_arg = self._get_restrictions(mapping)
        if idx_arg:
            args = list(self._args)
            for i, arg in idx_arg.items():
                # speed hack
                if arg == self.DOMINATOR:
                    return self.DOMINATOR
                else:
                    args[i] = arg
            return self.__class__(*args)
        else:
            return self

    def compose(self, mapping):
        idx_arg = self._get_compositions(mapping)
        return self._subs(idx_arg) if idx_arg else self

    # From Expression
    def __lt__(self, other):
        """Overload the '<' operator."""
        if isinstance(other, Literal):
            return self.support < other.support
        if isinstance(other, self.__class__) and self.depth == other.depth == 1:
            # min/max term
            if self.support == other.support:
                return self.term_index < other.term_index
            else:
                # support containment
                if self.support < other.support:
                    return True
                if other.support < self.support:
                    return False
                # support disjoint
                v = sorted(self.support ^ other.support)[0]
                if v in self.support:
                    return True
                if v in other.support:
                    return False
        return id(self) < id(other)

    @cached_property
    def depth(self):
        """Return the number of levels in the expression tree.

        >>> a, b, c, d = map(var, "abcd")
        >>> (a + b).depth, (a + (b * c)).depth, (a + (b * (c + d))).depth
        (1, 2, 3)
        >>> (a * b).depth, (a * (b + c)).depth, (a * (b + (c * d))).depth
        (1, 2, 3)
        """
        return max(arg.depth + 1 for arg in self._args)

    def invert(self):
        return self.DUAL(*[Not(arg) for arg in self._args],
                         simplify=self._simplified)

    def factor(self):
        """
        >>> a, b, c = map(var, "abc")
        >>> (a + -(b * c)).factor()
        a + b' + c'
        >>> (a * -(b + c)).factor()
        a * b' * c'
        """
        obj = self if self._simplified else self.simplify()
        if obj in B:
            return obj
        elif isinstance(obj, OrAnd):
            return obj.__class__(*[arg.factor() for arg in obj._args])
        else:
            return obj.factor()

    def simplify(self):
        if self._simplified:
            return self

        degenerate, args = self._simplify(self._args)
        if degenerate:
            return args

        obj = super(OrAnd, self).__new__(self.__class__)
        obj._args = args
        obj._simplified = True
        return obj

    # Specific to OrAnd
    def is_nf(self):
        """Return whether this expression is in normal form."""
        return (
            self.depth <= 2 and
            all(isinstance(arg, Literal) or isinstance(arg, self.DUAL)
                for arg in self._args)
        )

    def absorb(self):
        """Return the OR/AND expression after absorption.

        x + (x * y) = x
        x * (x + y) = x

        The reason this is not included as an automatic simplification is that
        it is too expensive to put into the constructor. We have to check
        whether each term is a subset of another term, which is N^3.
        """
        if not self.is_nf():
            raise TypeError("expression is not in normal form")

        temps, args = list(self._args), list()

        # Drop all terms that are a subset of other terms
        while temps:
            fst, rst, temps = temps[0], temps[1:], list()
            drop_fst = False
            for term in rst:
                drop_term = False
                if fst.arg_set <= term.arg_set:
                    drop_term = True
                elif fst.arg_set > term.arg_set:
                    drop_fst = True
                if not drop_term:
                    temps.append(term)
            if not drop_fst:
                args.append(fst)

        return self.__class__(*args)

    def _flatten(self, op):
        """Return a flattened OR/AND expression.

        Use the distributive law to flatten all nested expressions:
        x + (y * z) = (x + y) * (x + z)
        x * (y + z) = (x * y) + (x * z)

        NOTE: This function assumes the expression is already factored. Do NOT
              call this method directly -- use the "to_dnf" or "to_cnf" methods
              instead.
        """
        if isinstance(self, op):
            for i, arg in enumerate(self._args):
                if isinstance(arg, self.DUAL):
                    others = self._args[:i] + self._args[i+1:]
                    expr = op.DUAL(*[op(a, *others) for a in arg.args])
                    if isinstance(expr, OrAnd):
                        return expr._flatten(op)
                    else:
                        return expr
            else:
                return self
        else:
            nested, others = list(), list()
            for arg in self._args:
                if arg.depth > 1:
                    nested.append(arg)
                else:
                    others.append(arg)
            args = [arg._flatten(op) for arg in nested] + others
            return op.DUAL(*args)


class Or(OrAnd):
    """Boolean OR operator"""

    # Infix symbol used in string representation
    IDENTITY = 0
    DOMINATOR = 1

    def __str__(self):
        try:
            args = sorted(self._args)
        except (AttributeError, TypeError):
            args = list(self._args)
        return " + ".join(str(arg) for arg in args)

    def is_dnf(self):
        """Return whether this expression is in disjunctive normal form.

        >>> a, b, c, d = map(var, "abcd")
        >>> (a + b + c).is_dnf()
        True
        >>> (a + (b * c) + (c * d)).is_dnf()
        True
        >>> ((a * b) + (b * (c + d))).is_dnf()
        False
        """
        return self.is_nf()

    # Specific to Or
    @property
    def term_index(self):
        return self.maxterm_index

    @cached_property
    def maxterm_index(self):
        if self.depth > 1:
            return None
        n = self.degree - 1
        index = 0
        for i, v in enumerate(self.inputs):
            if -v in self._args:
                index |= 1 << (n - i)
        return index


class And(OrAnd):
    """Boolean AND operator"""

    # Infix symbol used in string representation
    IDENTITY = 1
    DOMINATOR = 0

    def __str__(self):
        try:
            args = sorted(self._args)
        except (AttributeError, TypeError):
            args = list(self._args)
        s = list()
        for arg in args:
            if isinstance(arg, Or):
                s.append("(" + str(arg) + ")")
            else:
                s.append(str(arg))
        return " * ".join(s)

    def is_cnf(self):
        """Return whether this expression is in conjunctive normal form.

        >>> a, b, c, d = map(var, "abcd")
        >>> (a * b * c).is_cnf()
        True
        >>> (a * (b + c) * (c + d)).is_cnf()
        True
        >>> ((a + b) * (b + c * d)).is_cnf()
        False
        """
        return self.is_nf()

    # DPLL IF
    def bcp(self):
        return _bcp(self)

    def ple(self):
        counter = dict()
        for clause in self.args:
            for lit in clause.args:
                if lit in counter:
                    counter[lit] += 1
                else:
                    counter[lit] = 0

        point = dict()
        while counter:
            lit, cnt = counter.popitem()
            if -lit in counter:
                counter.pop(-lit)
            elif cnt == 1:
                if isinstance(lit, Complement):
                    point[lit.var] = 0
                else:
                    point[lit] = 1
        if point:
            return self.restrict(point), point
        else:
            return self, {}

    # Specific to And
    @property
    def term_index(self):
        return self.minterm_index

    @cached_property
    def minterm_index(self):
        if self.depth > 1:
            return None
        n = self.degree - 1
        index = 0
        for i, v in enumerate(self.inputs):
            if v in self._args:
                index |= 1 << (n - i)
        return index


Or.DUAL = And
And.DUAL = Or


class Not(Expression):
    """Boolean NOT operator"""
    def __new__(cls, arg, simplify=True):
        arg = arg if isinstance(arg, Expression) else boolify(arg)
        if simplify:
            degenerate, arg = cls._simplify(arg)
            if degenerate:
                return arg

        self = super(Not, cls).__new__(cls)
        self._args = (arg, )
        self._simplified = simplify
        return self

    @classmethod
    def _simplify(cls, arg):
        if isinstance(arg, Expression):
            arg = arg.simplify()
        if arg in B:
            return True, 1 - arg
        elif isinstance(arg, Literal):
            return True, arg.invert()
        else:
            return False, arg

    def __str__(self):
        return "Not(" + str(self.arg) + ")"

    # From Function
    def restrict(self, mapping):
        """
        >>> a, b, c = map(var, "abc")
        >>> Not(-a + b).restrict({a: 0}), Not(-a + b).restrict({a: 1})
        (0, b')
        >>> -(-a + b + c).restrict({a: 1})
        Not(b + c)
        """
        arg = self.arg.restrict(mapping)
        # speed hack
        if arg in B:
            return 1 - arg
        elif id(arg) == id(self.arg):
            return self
        else:
            return self.__class__(arg)

    def compose(self, mapping):
        expr = self.arg.compose(mapping)
        if id(expr) == id(self.arg):
            return self
        else:
            return self.__class__(expr)

    # From Expression
    @cached_property
    def depth(self):
        return self.arg.depth

    def invert(self):
        return self.arg

    def factor(self):
        obj = self if self._simplified else self.simplify()
        if obj in B:
            return obj
        elif isinstance(obj, Not):
            return obj.arg.invert().factor()
        else:
            return obj.factor()

    def simplify(self):
        if self._simplified:
            return self

        degenerate, arg = self._simplify(self.arg)
        if degenerate:
            return arg

        obj = super(Not, self).__new__(self.__class__)
        obj._args = (arg, )
        obj._simplified = True
        return obj

    # Specific to Not
    @property
    def arg(self):
        return self._args[0]


class Exclusive(Expression):
    """Boolean exclusive (XOR, XNOR) operator"""

    def __new__(cls, *args, **kwargs):
        simplify = kwargs.get('simplify', True)
        args = tuple(arg if isinstance(arg, Expression) else boolify(arg)
                     for arg in args)
        if simplify:
            degenerate, args, parity = cls._simplify(args)
            if degenerate:
                return args
        else:
            parity = cls.PARITY

        self = super(Exclusive, cls).__new__(cls)
        self._args = args
        self._simplified = simplify
        self._parity = parity
        return self

    @classmethod
    def _simplify(cls, args):
        parity = cls.PARITY
        temps, args = deque(args), list()

        while temps:
            arg = temps.popleft()
            if isinstance(arg, Expression):
                arg = arg.simplify()
            if arg in B:
                parity ^= arg
            # associative
            elif isinstance(arg, cls):
                temps.extendleft(reversed(arg.args))
            # Xor(x, x') = 1
            elif isinstance(arg, Literal) and -arg in args:
                args.remove(-arg)
                parity ^= 1
            # Xor(x, x) = 0
            elif arg in args:
                args.remove(arg)
            else:
                args.append(arg)

        # Xor() = 0; Xnor() = 1
        if len(args) == 0:
            return True, parity, None
        # Xor(x) = x; Xnor(x) = x'
        if len(args) == 1:
            return True, Not(args[0]) if parity else args[0], None

        return False, tuple(args), parity

    def __str__(self):
        args_str = ", ".join(str(arg) for arg in self._args)
        if self._parity:
            return "Xnor(" + args_str + ")"
        else:
            return "Xor(" + args_str + ")"

    # From Function
    def restrict(self, mapping):
        idx_arg = self._get_restrictions(mapping)
        if idx_arg:
            args = list(self._args)
            for i, arg in idx_arg.items():
                args[i] = arg
            return Xnor(*args) if self._parity else Xor(*args)
        else:
            return self

    def compose(self, mapping):
        idx_arg = self._get_compositions(mapping)
        if idx_arg:
            args = self._args[:]
            for i, arg in idx_arg.items():
                args[i] = arg
            return Xnor(*args) if self._parity else Xor(*args)
        else:
            return self

    # From Expression
    @property
    def depth(self):
        """
        >>> a, b, c, d, e = map(var, "abcde")
        >>> Xor(a, b, c).depth
        2
        >>> Xor(a, b, c + d).depth
        3
        >>> Xor(a, b, c + Xor(d, e)).depth
        5
        """
        return max(arg.depth + 2 for arg in self._args)

    def invert(self):
        if self._parity == Xor.PARITY:
            return Xnor(*self._args, simplify=self._simplified)
        else:
            return Xor(*self._args, simplify=self._simplified)

    def factor(self):
        obj = self if self._simplified else self.simplify()
        if obj in B:
            return obj
        elif isinstance(obj, Exclusive):
            fst, rst = obj._args[0], obj._args[1:]
            if obj._parity == Xor.PARITY:
                return Or(And(Not(fst).factor(), Xor(*rst).factor()),
                          And(fst.factor(), Xnor(*rst).factor()))
            else:
                return Or(And(Not(fst).factor(), Xnor(*rst).factor()),
                          And(fst.factor(), Xor(*rst).factor()))
        else:
            return obj.factor()

    def simplify(self):
        if self._simplified:
            return self

        degenerate, args, parity = self._simplify(self._args)
        if degenerate:
            return args

        obj = super(Exclusive, self).__new__(self.__class__)
        obj._args = args
        obj._simplified = True
        obj._parity = parity
        return obj


class Xor(Exclusive):
    """Boolean Exclusive OR (XOR) operator"""
    PARITY = 0

class Xnor(Exclusive):
    """Boolean Exclusive NOR (XNOR) operator"""
    PARITY = 1


class Equal(Expression):
    """Boolean EQUAL operator"""

    def __new__(cls, *args, **kwargs):
        simplify = kwargs.get('simplify', True)
        args = tuple(arg if isinstance(arg, Expression) else boolify(arg)
                     for arg in args)
        if simplify:
            degenerate, args = cls._simplify(args)
            if degenerate:
                return args

        self = super(Equal, cls).__new__(cls)
        self._args = args
        self._simplified = simplify
        return self

    @classmethod
    def _simplify(cls, args):
        if 0 in args:
            # Equal(0, 1, ...) = 0
            if 1 in args:
                return True, 0
            # Equal(0, x0, x1, ...) = Nor(x0, x1, ...)
            else:
                return True, Not(Or(*args))
        # Equal(1, x0, x1, ...)
        if 1 in args:
            return True, And(*args)

        temps, args = deque(args), list()
        while temps:
            arg = temps.popleft()
            # Equal(x, -x) = 0
            if isinstance(arg, Literal) and -arg in args:
                return True, 0
            # Equal(x, x, ...) = Equal(x, ...)
            elif arg not in args:
                args.append(arg)

        # Equal(x) = Equal() = 1
        if len(args) <= 1:
            return True, 1

        return False, tuple(args)

    def __str__(self):
        args_str = ", ".join(str(arg) for arg in self._args)
        return "Equal(" + args_str + ")"

    # From Function
    def restrict(self, mapping):
        idx_arg = self._get_restrictions(mapping)
        return self._subs(idx_arg) if idx_arg else self

    def compose(self, mapping):
        idx_arg = self._get_compositions(mapping)
        return self._subs(idx_arg) if idx_arg else self

    # From Expression
    @property
    def depth(self):
        return max(arg.depth + 2 for arg in self._args)

    def invert(self):
        return And(Or(*self._args), Not(And(*self._args)))

    def factor(self):
        obj = self if self._simplified else self.simplify()
        if obj in B:
            return obj
        elif isinstance(obj, Equal):
            return Or(And(*[Not(arg).factor() for arg in obj._args]),
                      And(*[arg.factor() for arg in obj._args]))
        else:
            return obj.factor()

    def simplify(self):
        if self._simplified:
            return self

        degenerate, args = self._simplify(self._args)
        if degenerate:
            return args

        obj = super(Equal, self).__new__(self.__class__)
        obj._args = args
        obj._simplified = True
        return obj


class Implies(Expression):
    """Boolean implication operator"""

    def __new__(cls, p, q, simplify=True):
        args = tuple(arg if isinstance(arg, Expression) else boolify(arg)
                     for arg in (p, q))
        if simplify:
            degenerate, args = cls._simplify(args)
            if degenerate:
                return args
        else:
            args = (p, q)

        self = super(Implies, cls).__new__(cls)
        self._args = args
        self._simplified = simplify
        return self

    @classmethod
    def _simplify(cls, args):
        p, q = (arg.simplify() if isinstance(arg, Expression) else arg
                for arg in args)

        # 0 => q = 1; p => 1 = 1
        if p == 0 or q == 1:
            return True, 1
        # 1 => q = q
        elif p == 1:
            return True, q
        # p => 0 = p'
        elif q == 0:
            return True, Not(p)
        # p -> p = 1
        elif p == q:
            return True, 1
        # -p -> p = p
        elif isinstance(p, Literal) and -p == q:
            return True, q

        return False, (p, q)

    def __str__(self):
        s = list()
        for arg in self._args:
            if arg in B or isinstance(arg, Literal):
                s.append(str(arg))
            else:
                s.append("(" + str(arg) + ")")
        return " => ".join(s)

    # From Function
    def restrict(self, mapping):
        idx_arg = self._get_restrictions(mapping)
        return self._subs(idx_arg) if idx_arg else self

    def compose(self, mapping):
        idx_arg = self._get_compositions(mapping)
        return self._subs(idx_arg) if idx_arg else self

    # From Expression
    @property
    def depth(self):
        return max(arg.depth + 1 for arg in self._args)

    def invert(self):
        p, q = self._args
        return And(p, Not(q))

    def factor(self):
        obj = self if self._simplified else self.simplify()
        if obj in B:
            return obj
        elif isinstance(obj, Implies):
            a, b = obj._args
            return Or(Not(a).factor(), b.factor())
        else:
            return obj.factor()

    def simplify(self):
        if self._simplified:
            return self

        degenerate, args = self._simplify(self._args)
        if degenerate:
            return args

        obj = super(Implies, self).__new__(self.__class__)
        obj._args = args
        obj._simplified = True
        return obj


class ITE(Expression):
    """Boolean if-then-else ternary operator"""

    def __new__(cls, s, a, b, simplify=True):
        args = (arg if isinstance(arg, Expression) else boolify(arg)
                for arg in (s, a, b))
        if simplify:
            degenerate, args = cls._simplify(args)
            if degenerate:
                return args
        else:
            args = (s, a, b)

        self = super(ITE, cls).__new__(cls)
        self._args = args
        self._simplified = simplify
        return self

    @classmethod
    def _simplify(cls, args):
        s, a, b = (arg.simplify() if isinstance(arg, Expression) else arg
                   for arg in args)

        # 0 ? a : b = b
        if s == 0:
            return True, b
        # 1 ? a : b = a
        elif s == 1:
            return True, a
        elif a == 0:
            # s ? 0 : 0 = 0
            if b == 0:
                return True, 0
            # s ? 0 : 1 = s'
            elif b == 1:
                return True, Not(s)
            # s ? 0 : b = s' * b
            else:
                return True, And(Not(s), b)
        elif a == 1:
            # s ? 1 : 0 = s
            if b == 0:
                return True, s
            # s ? 1 : 1 = 1
            elif b == 1:
                return True, 1
            # s ? 1 : b = s + b
            else:
                return True, Or(s, b)
        # s ? a : 0 = s * a
        elif b == 0:
            return True, And(s, a)
        # s ? a : 1 = s' + a
        elif b == 1:
            return True, Or(Not(s), a)
        # s ? a : a = a
        elif a == b:
            return True, a

        return False, (s, a, b)

    def __str__(self):
        s = list()
        for arg in self._args:
            if arg in B or isinstance(arg, Literal):
                s.append(str(arg))
            else:
                s.append("(" + str(arg) + ")")
        return "{} ? {} : {}".format(*s)

    # From Function
    def restrict(self, mapping):
        idx_arg = self._get_restrictions(mapping)
        return self._subs(idx_arg) if idx_arg else self

    def compose(self, mapping):
        idx_arg = self._get_compositions(mapping)
        return self._subs(idx_arg) if idx_arg else self

    # From Expression
    @cached_property
    def depth(self):
        return max(arg.depth + 2 for arg in self._args)

    def invert(self):
        s, a, b = self._args
        return ITE(s, Not(a), Not(b), simplify=self._simplified)

    def factor(self):
        obj = self if self._simplified else self.simplify()
        if obj in B:
            return obj
        elif isinstance(obj, ITE):
            s, a, b = obj._args
            return Or(And(s, a), And(Not(s).factor(), b))
        else:
            return obj.factor()

    def simplify(self):
        if self._simplified:
            return self

        degenerate, args = self._simplify(self._args)
        if degenerate:
            return args

        obj = super(ITE, self).__new__(self.__class__)
        obj._args = args
        obj._simplified = True
        return obj


def _bcp(cnf):
    """Boolean Constraint Propagation"""
    if cnf in B:
        return cnf, {}
    else:
        point = dict()
        for clause in cnf.args:
            if len(clause.args) == 1:
                lit = clause.args[0]
                if isinstance(lit, Complement):
                    point[lit.var] = 0
                else:
                    point[lit] = 1
        if point:
            _cnf, _point = _bcp(cnf.restrict(point))
            point.update(_point)
            return _cnf, point
        else:
            return cnf, point
