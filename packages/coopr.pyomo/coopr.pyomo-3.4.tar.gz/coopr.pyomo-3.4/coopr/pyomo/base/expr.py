#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

from __future__ import division

__all__ = [ 'Expression' ]

import copy
import logging
import sys

logger = logging.getLogger('coopr.pyomo')

try:
    from sys import getrefcount
    _getrefcount_available = True
except ImportError:
    logger.warning(
        "This python interpreter does not support sys.getrefcount()\n"
        "Pyomo cannot automatically guarantee that expressions do not become\n"
        "entangled (multiple expressions that share common subexpressions).\n")
    _getrefcount_available = False

from six import StringIO, next
from six.moves import xrange

from pyutilib.component.core import *

from coopr.pyomo.base.plugin import *
from coopr.pyomo.base.numvalue import *
from coopr.pyomo.base.numvalue import ZeroConstant, native_numeric_types
from coopr.pyomo.base.var import _VarData



def clone_expression(exp):
    if exp.is_expression():
        return copy.copy(exp)
    else:
        return exp

def chainedInequalityErrorMessage(msg=None):
    if msg is None:
        msg = "Nonconstant relational expression used in an "\
              "unexpected Boolean context."
    buf = StringIO()
    generate_relational_expression.chainedInequality.pprint(buf)
    # We are about to raise an exception, so it's OK to reset chainedInequality
    generate_relational_expression.chainedInequality = None
    msg += """
The inequality expression:
    %s
contains non-constant terms (variables) appearing in a Boolean context, e.g.:
    if expression <= 5:
This is generally invalid.  If you want to obtain the Boolean value of
the expression based on the current variable values, explicitly evaluate
the expression, e.g.:
    if value(expression) <= 5:
or
    if value(expression <= 5):
""" % ( buf.getvalue().strip(), )
    return msg


def identify_variables(expr, include_fixed=True):
    if expr.is_expression():
        if type(expr) is _ProductExpression:
            for arg in expr._numerator:
                for var in identify_variables(arg, include_fixed):
                    yield var
            for arg in expr._denominator:
                for var in identify_variables(arg, include_fixed):
                    yield var
        elif type(expr) is _ExternalFunctionExpression:
            for arg in expr._args:
                if isinstance(arg, basestring):
                    continue
                for var in identify_variables(arg, include_fixed):
                    yield var
        else:
            for arg in expr._args:
                for var in identify_variables(arg, include_fixed):
                    yield var
    elif include_fixed or not expr.is_fixed():
        if isinstance(expr, _VarData):
            yield expr


class Expression(NumericValue):
    """An object that defines a mathematical expression that can be evaluated"""

    __slots__ = ('_args', )

    def __init__(self, args):
        """Construct an expression with an operation and a set of arguments"""
        self._args=args

    def __getstate__(self):
        result = NumericValue.__getstate__(self)
        for i in Expression.__slots__:
            result[i] = getattr(self, i)
        return result

    def pprint(self, ostream=None, nested=True, eol_flag=True, verbose=False):
        """Print this expression"""
        if ostream is None:
            ostream = sys.stdout
        if nested:
            ostream.write(self.cname() + "( ")
            first=True
            for arg in self._args:
                if first==False:
                    ostream.write(", ")
                if arg.is_expression():
                    arg.pprint(ostream=ostream, nested=nested, eol_flag=False, verbose=verbose)
                else:
                    ostream.write(str(arg)+' ')
                first=False
            if eol_flag==True:
                ostream.write(")\n")
            else:
                ostream.write(") ")

    def clone(self):
        return copy.copy(self)

    def __copy__(self):
        """Clone this object using the specified arguments"""
        raise NotImplementedError("Derived expression (%s) failed to "\
            "implement __copy__()" % ( str(self.__class__), ))

    def simplify(self, model): #pragma:nocover
        print("""
WARNING: Expression.simplify() has been deprecated and removed from
     Pyomo Expressions.  Please remove references to simplify() from your
     code.
""")
        return self

    #
    # this method contrast with the is_fixed() method.
    # the is_fixed() method returns true iff the value is
    # an atomic constant.
    # this method returns true iff all composite arguments
    # in this sum expression are constant, i.e., numeric
    # constants or parametrs. the parameter values can of
    # course change over time, but at any point in time,
    # they are constant. hence, the name.
    #
    def is_constant(self):
        for arg in self._args:
            if not arg.is_constant():
                return False
        return True

    def is_fixed(self):
        for arg in self._args:
            if not arg.is_fixed():
                return False
        return True

    def is_expression(self):
        return True

    def polynomial_degree(self):
        return None

    def __nonzero__(self):
        return bool(self())

    __bool__ = __nonzero__

    def __call__(self, exception=True):
        """Evaluate the expression"""
        try:
            return self._apply_operation(self._evaluate_arglist(self._args))
        except (ValueError, TypeError):
            if exception:
                raise
            return None

    def _evaluate_arglist(self, arglist):
        for arg in arglist:
            try:
                yield value(arg)
            except Exception:
                e = sys.exc_info()[1]
                buffer = StringIO()
                self.pprint(buffer)
                logger.error("evaluating expression: %s\n    (expression: %s)",
                             str(e), buffer.getvalue())
                raise

    def _apply_operation(self, values):
        """Method that can be overwritten to define the operation in
        this expression"""
        raise NotImplementedError("Derived expression (%s) failed to "\
            "implement _apply_operation()" % ( str(self.__class__), ))

    def __str__(self):
        return str(self.cname())


class _ExternalFunctionExpression(Expression):
    __slots__ = ('_fcn')

    def __init__(self, fcn, args):
        """Construct a call to an external function"""
        Expression.__init__(self, args)
        self._fcn = fcn

    def __getstate__(self):
        result = Expression.__getstate__(self)
        for i in _ExternalFunctionExpression.__slots__:
            result[i] = getattr(self, i)
        return result

    def __copy__(self):
        return self.__class__( self._fcn,
                               tuple(clone_expression(x) for x in self._args) )

    def cname(self):
        return self._fcn.cname()

    def polynomial_degree(self):
        return None

    def is_constant(self):
        for arg in self._args:
            if isinstance(arg, basestring):
                continue
            if not arg.is_constant():
                return False
        return True

    def is_fixed(self):
        for arg in self._args:
            if isinstance(arg, basestring):
                continue
            if not arg.is_fixed():
                return False
        return True

    def _apply_operation(self, values):
        return self._fcn.evaluate(values)


class _IntrinsicFunctionExpression(Expression):
    __slots__ = ('_operator', '_name')

    def __init__(self, name, nargs, args, operator):
        """Construct an expression with an operation and a set of arguments"""
        if nargs and nargs != len(args):
            raise ValueError("%s() takes exactly %d arguments (%d given)" % \
                ( self.cname(), nargs, len(args) ))
        Expression.__init__(self, args)
        self._operator = operator
        self._name = name

    def __getstate__(self):
        result = Expression.__getstate__(self)
        for i in _IntrinsicFunctionExpression.__slots__:
            result[i] = getattr(self, i)
        return result

    def __copy__(self):
        return self.__class__( self._name,
                               None,
                               tuple(clone_expression(x) for x in self._args),
                               self._operator )

    def _apply_operation(self, values):
        return self._operator(*tuple(values))

    def cname(self):
        return self._name

    def polynomial_degree(self):
        if self.is_fixed():
            return 0
        return None


# Should this actually be a special class, or just an instance of
# _IntrinsicFunctionExpression (like sin, cos, etc)?
class _AbsExpression(_IntrinsicFunctionExpression):

    __slots__ = ()

    def __init__(self, args):
        _IntrinsicFunctionExpression.__init__(self, 'abs', 1, args, abs)

    def __getstate__(self):
        return _IntrinsicFunctionExpression.__getstate__(self)

    def __copy__(self):
        return self.__class__( tuple(clone_expression(x) for x in self._args) )

# Should this actually be a special class, or just an instance of
# _IntrinsicFunctionExpression (like sin, cos, etc)?
class _PowExpression(_IntrinsicFunctionExpression):

    __slots__ = ()

    def __init__(self, args):
        _IntrinsicFunctionExpression.__init__(self, 'pow', 2, args, pow)

    def __getstate__(self):
        return _IntrinsicFunctionExpression.__getstate__(self)

    def __copy__(self):
        return self.__class__( tuple(clone_expression(x) for x in self._args) )

    def polynomial_degree(self):
        # _PowExpression is a tricky thing.  In general, a**b is
        # nonpolynomial, however, if b == 0, it is a constant
        # expression, and if a is polynomial and b is a positive
        # integer, it is also polynomial.  While we would like to just
        # call this a non-polynomial expression, these exceptions occur
        # too frequently (and in particular, a**2)
        if self._args[1].is_fixed():
            if self._args[0].is_fixed():
                return 0
            try:
                exp = int(self._args[1])
                if exp == value(self._args[1]):
                    base = self._args[0].polynomial_degree()
                    if base is not None and exp > 0:
                        return base * exp
                    elif exp == 0:
                        return 0
            except:
                pass
        return None

    def is_fixed(self):
        if self._args[1].is_fixed():
            return self._args[0].is_fixed() or bool(self._args[1] == 0)
        return False

class _LinearExpression(Expression):

    __slots__ = ()

     # the constructor for a _LinearExpression does nothing, as there are
     # no class-specific slots. thus, one is not provided - providing one
     # simply incurs overhead. the original constructor is commented out
     # below, to provide documentation as to how arguments are munged.

    def polynomial_degree(self):
        # NB: We can't use max() here because None (non-polynomial)
        # overrides a numeric value (and max() just ignores it)
        degree = 0
        for x in self._args:
            x_degree = x.polynomial_degree()
            if x_degree is None:
                return None
            if x_degree > degree:
               degree = x_degree
        return degree


class _InequalityExpression(_LinearExpression):
    """An object that defines a series of less-than or
    less-than-or-equal expressions"""

    __slots__ = ('_strict', '_cloned_from')

    def __init__(self, args, strict, cloned_from):
        """Constructor"""
        _LinearExpression.__init__(self, args)
        self._strict = strict
        self._cloned_from = cloned_from
        if len(self._args)-1 != len(self._strict):
            raise ValueError("_InequalityExpression(): len(args)-1 != " \
                  "len(strict)(%d and %d given)" % (len(args), len(strict)))

    def __getstate__(self):
        result = _LinearExpression.__getstate__(self)
        for i in _InequalityExpression.__slots__:
            result[i] = getattr(self, i)
        return result

    def __nonzero__(self):
        if generate_relational_expression.chainedInequality is not None:
            raise TypeError(chainedInequalityErrorMessage())
        if not self.is_constant():
            generate_relational_expression.chainedInequality = self
            return True

        return bool(self())

    __bool__ = __nonzero__

    def is_relational(self):
        return True

    def __copy__(self):
        return self.__class__( [clone_expression(x) for x in self._args],
                               copy.copy(self._strict),
                               copy.copy(self._cloned_from) )

    def _apply_operation(self, values):
        """Method that defines the less-than-or-equal operation"""
        arg1 = next(values)
        for strict in self._strict:
            arg2 = next(values)
            if strict:
                if not (arg1 < arg2):
                    return False
            else:
                if not (arg1 <= arg2):
                    return False
            arg1 = arg2
        return True

    def pprint(self, ostream=None, nested=True, eol_flag=True, verbose=False):
        """Print this expression"""
        if ostream is None:
            ostream = sys.stdout
        if nested:
            first=True
            for i, strict in enumerate(self._strict):
                arg = self._args[i]
                if arg.is_expression():
                    arg.pprint(ostream=ostream, nested=nested, eol_flag=False, verbose=verbose)
                else:
                    ostream.write(str(arg)+' ')
                if strict:
                    ostream.write(" <  ")
                else:
                    ostream.write(" <=  ")
            arg = self._args[-1]
            if arg.is_expression():
                arg.pprint(ostream=ostream, nested=nested, eol_flag=False, verbose=verbose)
            else:
                ostream.write(str(arg)+' ')
            if eol_flag==True:
                ostream.write("\n")


class _EqualityExpression(_LinearExpression):
    """An object that defines a equal-to expression"""

    __slots__ = ()

    def __init__(self, args):
        """Constructor"""
        if 2 != len(args):
            raise ValueError("%s() takes exactly 2 arguments (%d given)" % \
                ( self.cname(), len(args) ))
        _LinearExpression.__init__(self, args)

    def __copy__(self):
        return self.__class__( tuple(clone_expression(x) for x in self._args) )

    def __nonzero__(self):
        if generate_relational_expression.chainedInequality is not None:
            raise TypeError(chainedInequalityErrorMessage())
        return bool(self())

    __bool__ = __nonzero__

    def is_relational(self):
        return True

    def _apply_operation(self, values):
        """Method that defines the equal-to operation"""
        return next(values) == next(values)

    def pprint(self, ostream=None, nested=True, eol_flag=True, verbose=False):
        """Print this expression"""
        if ostream is None:
            ostream = sys.stdout
        if nested:
            first = True
            for arg in self._args:
                if not first:
                    ostream.write(" ==  ")
                first = False
                if arg.is_expression():
                    arg.pprint(ostream=ostream, nested=nested, eol_flag=False, verbose=verbose)
                else:
                    ostream.write(str(arg)+' ')
            if eol_flag==True:
                ostream.write("\n")


# It is common to generate sums of const*var (which immediately get
# thrown away by the simplifications in generate_expression): this gives
# us a pool for re-using the temporary _ProductExpression objects.
_ProdExpression_Pool = []

class _ProductExpression(Expression):
    """An object that defines a product expression"""

    __slots__ = ('_denominator','_numerator','_coef')

    def __init__(self):
        """Constructor"""
        Expression.__init__(self, None)
        
        # generate_expression will create these for us.  Creating them
        # here is significantly wasteful as they would just end up being
        # thrown away.
        #self._denominator = []
        #self._numerator = []
        self._coef = 1

    def __getstate__(self):
        result = Expression.__getstate__(self)
        for i in _ProductExpression.__slots__:
            result[i] = getattr(self, i)
        return result

    def is_constant(self):
        for arg in self._numerator:
            if not arg.is_constant():
                return False
        for arg in self._denominator:
            if not arg.is_constant():
                return False
        return True

    def is_fixed(self):
        for arg in self._numerator:
            if not arg.is_fixed():
                return False
        for arg in self._denominator:
            if not arg.is_fixed():
                return False
        return True

    def polynomial_degree(self):
        for x in self._denominator:
            if x.polynomial_degree() != 0:
                return None
        try:
            return sum(x.polynomial_degree() for x in self._numerator)
        except TypeError:
            return None
        except ValueError:
            return None

    def invert(self):
        tmp = self._denominator
        self._denominator = self._numerator
        self._numerator = tmp
        self._coef = 1.0/self._coef

    def pprint(self, ostream=None, nested=True, eol_flag=True, verbose=False):
        """Print this expression"""
        if ostream is None:
            ostream = sys.stdout
        if nested:
            ostream.write("prod( num=( ")
            first=True
            if self._coef != 1:
                ostream.write(str(self._coef)+' ')
                first=False
            for arg in self._numerator:
                if first==False:
                    ostream.write(", ")
                if arg.is_expression():
                    arg.pprint(ostream=ostream, nested=nested, eol_flag=False, verbose=verbose)
                else:
                    ostream.write(str(arg)+' ')
                first=False
            if first is True:
                ostream.write('1 ')
            ostream.write(") ")
            if len(self._denominator) > 0:
                ostream.write(", denom=( ")
                first=True
                for arg in self._denominator:
                    if first==False:
                        ostream.write(", ")
                    if arg.is_expression():
                        arg.pprint(ostream=ostream, nested=nested, eol_flag=False, verbose=verbose)
                    else:
                        ostream.write(str(arg)+' ')
                    first=False
                ostream.write(") ")
            ostream.write(") ")
            if eol_flag==True:
                ostream.write("\n")

    def __copy__(self):
        """Clone this object using the specified arguments"""
        tmp = self.__class__()
        tmp._numerator = [clone_expression(x) for x in self._numerator]
        tmp._denominator = [clone_expression(x) for x in self._denominator]
        tmp._coef = self._coef
        return tmp

    def __call__(self, exception=True):
        """Evaluate the expression"""
        try:
            ans = self._coef
            for n in self._evaluate_arglist(self._numerator):
                ans *= n
            for n in self._evaluate_arglist(self._denominator):
                ans /= n
            return ans
        except (TypeError, ValueError):
            if exception:
                raise
            return None


class _IdentityExpression(_LinearExpression):
    """An object that defines a identity expression"""

    __slots__ = ()

    def __init__(self, args):
        """Constructor"""
        arg_type = type(args)
        if arg_type is list or arg_type is tuple:
            Expression.__init__(self, tuple(args))
        else:
            Expression.__init__(self, (args,))

    def __copy__(self):
        return self.__class__( tuple(clone_expression(x) for x in self._args) )

    def _apply_operation(self, values):
        """Method that defines the identity operation"""
        return next(values)


# It is common to generate sums of sums (which immediately get
# thrown away by the simplifications in generate_expression): this gives
# us a pool for re-using the temporary _SumExpression objects.
_SumExpression_Pool = []

class _SumExpression(_LinearExpression):
    """An object that defines a weighted summation of expressions"""

    __slots__ = ('_coef','_const')

    def __init__(self):
        """Constructor"""
        _LinearExpression.__init__(self, [])

        self._const = 0
        # generate_expression will create this for us.  Creating it
        # here is significantly wasteful as they would just end up being
        # thrown away.  
        #self._coef = []
        # TODO: determine if we can do something similar with _args for
        # all _LinearExpressions

    def __getstate__(self):
        result = _LinearExpression.__getstate__(self)
        for i in _SumExpression.__slots__:
            result[i] = getattr(self, i)
        return result

    def __copy__(self):
        """Clone this object using the specified arguments"""
        tmp = self.__class__()
        tmp._args = [clone_expression(x) for x in self._args]
        tmp._coef = copy.copy(self._coef)
        tmp._const = self._const
        return tmp

    def scale(self, val):
        for i in xrange(len(self._coef)):
            self._coef[i] *= val
        self._const *= val

    def negate(self):
        self.scale(-1)

    def pprint(self, ostream=None, nested=True, eol_flag=True, verbose=False):
        """Print this expression"""
        if ostream is None:
            ostream = sys.stdout
        if nested:
            ostream.write("sum( ")
            first=True
            if self._const != 0:
                ostream.write(str(self._const)+' ')
                first=False
            for i, arg in enumerate(self._args):
                if first==False:
                    ostream.write(", ")
                if self._coef[i] != 1:
                    ostream.write(str(self._coef[i])+" *  ")
                if arg.is_expression():
                    arg.pprint(ostream=ostream, nested=nested, eol_flag=False, verbose=verbose)
                else:
                    ostream.write(str(arg)+' ')
                first=False
            ostream.write(") ")
            if eol_flag==True:
                ostream.write("\n")

    def _apply_operation(self, values):
        """Evaluate the expression"""
        return sum(c*next(values) for c in self._coef) + self._const


class Expr_if(Expression):
    """An object that defines a dynamic if-then-else expression"""

    __slots__ = ('_if','_then','_else')

    def __init__(self, IF=None, THEN=None, ELSE=None):
        """Constructor"""
        Expression.__init__(self, None)
        
        self._if = as_numeric(IF)
        self._then = as_numeric(THEN)
        self._else = as_numeric(ELSE)

    def __getstate__(self):
        result = Expression.__getstate__(self)
        for i in Expr_if.__slots__:
            result[i] = getattr(self, i)
        return result

    def cname(self):
        return "Expr_if"

    def is_constant(self):
        if self._if.is_constant():
            if bool(self._if) is True:
                return self._then.is_constant()
            else:
                return self._else.is_constant()
        else:
            # Even if the branching point is not constant, if both
            # branches are constant and equal then this expression
            # is constant
            if self._then.is_constant() and self._else.is_constant():
                return value(self._then) == value(self._else)

    def is_fixed(self):
        if self._if.is_fixed():
            if bool(self._if) is True:
                return self._then.is_fixed() 
            else:
                return self._else.is_fixed()
        else:
            # Even if the branching point is not fixed, if both
            # branches are fixed and equal then this expression
            # is fixed
            if self._then.is_fixed() and self._else.is_fixed():
                return value(self._then) == value(self._else)

    def polynomial_degree(self):
        if self._if.is_fixed():
            if bool(self._if) is True:
                return self._then.polynomial_degree()
            else:
                return self._else.polynomial_degree()

    def pprint(self, ostream=None, nested=True, eol_flag=True, verbose=False):
        """Print this expression"""
        if ostream is None:
            ostream = sys.stdout
        if nested:
            ostream.write("Expr_if( if=( ")
            if self._if.is_expression():
                self._if.pprint(ostream=ostream, nested=nested, eol_flag=False, verbose=verbose)
            else:
                ostream.write(str(self._if)+' ')
            ostream.write(") ")
            ostream.write(", then=( ")
            if self._then.is_expression():
                self._then.pprint(ostream=ostream, nested=nested, eol_flag=False, verbose=verbose)
            else:
                ostream.write(str(self._then)+' ')
            ostream.write(") ")
            ostream.write(", else=( ")
            if self._else.is_expression():
                self._else.pprint(ostream=ostream, nested=nested, eol_flag=False, verbose=verbose)
            else:
                ostream.write(str(self._else)+' ')
            ostream.write(") ")
            if eol_flag==True:
                ostream.write("\n")

    def __copy__(self):
        """Clone this object using the specified arguments"""
        tmp = self.__class__()
        tmp._if = clone_expression(self._if)
        tmp._then = clone_expression(self._then)
        tmp._else = clone_expression(self._else)
        return tmp

    def __call__(self, exception=True):
        """Evaluate the expression"""
        if bool(self._if) is True:
            return value(self._then)
        else:
            return value(self._else)


def _generate_expression__clone_if_needed(obj, target):
    if getrefcount(obj) - UNREFERENCED_EXPR_COUNT == target:
        return obj
    elif getrefcount(obj) - UNREFERENCED_EXPR_COUNT > target:
        generate_expression.clone_counter += 1
        return obj.clone()
    else: #pragma:nocover
        raise RuntimeError("Expression entered generate_expression() " \
              "with too few references (%s<0); this is indicative of a " \
              "SERIOUS ERROR in the expression reuse detection scheme." \
              % ( getrefcount(obj) - UNREFERENCED_EXPR_COUNT, ))

def _generate_expression__noCloneCheck(obj, target):
    return obj

def generate_expression_bypassCloneCheck(etype, _self, other):
    global _generate_expression__noCloneCheck
    global _generate_expression__clone_if_needed
    _generate_expression__noCloneCheck, _generate_expression__clone_if_needed=\
    _generate_expression__clone_if_needed, _generate_expression__noCloneCheck

    ans = generate_expression(etype, _self, other)

    _generate_expression__noCloneCheck, _generate_expression__clone_if_needed=\
    _generate_expression__clone_if_needed, _generate_expression__noCloneCheck
    return ans



_add = 1
_sub = 2
_mul = 3
_div = 4
_pow = 5
_neg = 6
_abs = 7
_inplace = 10
_unary = _neg

_radd =         -_add
_iadd = _inplace+_add
_rsub =         -_sub
_isub = _inplace+_sub
_rmul =         -_mul
_imul = _inplace+_mul
_rdiv =         -_div
_idiv = _inplace+_div
_rpow =         -_pow
_ipow = _inplace+_pow

_old_etype_strings = {
    'add'  :          _add,
    'radd' :         -_add,
    'iadd' : _inplace+_add,
    'sub'  :          _sub,
    'rsub' :         -_sub,
    'isub' : _inplace+_sub,
    'mul'  :          _mul,
    'rmul' :         -_mul,
    'imul' : _inplace+_mul,
    'div'  :          _div,
    'rdiv' :         -_div,
    'idiv' : _inplace+_div,
    'pow'  :          _pow,
    'rpow' :         -_pow,
    'ipow' : _inplace+_pow,
    'neg'  :          _neg,
    'abs'  :          _abs,
    }
          

def generate_expression(etype, _self, other):
    if _self.is_indexed():
        raise TypeError("Argument for expression '%s' is an indexed "\
              "numeric value specified without an index: %s\n    Is "\
              "variable or parameter '%s' defined over an index that "\
              "you did not specify?" % (etype, _self.cname(), _self.cname()))

    self_type = _self.__class__
    
    # In-place operators should only clone `self` if someone else (other
    # than the self) holds a reference to it.  This also enforces that
    # there MUST be an external `self` reference for in-place operators.
    if etype > _inplace: #and etype < 2*_inplace:#etype[0] == 'i':
        #etype = etype[1:]
        etype -= _inplace
        if _self.is_expression():
            _self = _generate_expression__clone_if_needed(_self, 1)
    else:
        if _self.is_expression():
            _self = _generate_expression__clone_if_needed(_self, 0)
        elif _self.is_constant():
            _self = _self()
            self_type = None

    #
    # First, handle the special cases of unary operators and
    # "degenerate" binary operators (subtraction)
    #
    #if etype in _generate_expression__specialCases:
    #    if etype[-1] == 'b': # This covers sub and rsub
    #        etype = etype[:-3] + 'add'
    #        multiplier = -1
    if etype >= _unary:
        if etype == _neg:
            if self_type is _SumExpression:
                _self.negate()
                return _self
            elif self_type is _ProductExpression:
                _self._coef *= -1
                return _self
            else:
                etype = _rmul#'rmul'
                other = -1
        elif etype == _abs:
            if self_type is None:
                return abs(_self)
            else:
                return _AbsExpression([_self])
    
    if other.__class__ in native_numeric_types:
        other_type = None
    else:
        try:
            other = other.as_numeric()
        except AttributeError:
            other = as_numeric(other)
        other_type = other.__class__
        if other.is_indexed():
            raise TypeError(
                "Argument for expression '%s' is an indexed numeric "
                "value\nspecified without an index:\n\t%s\nIs this "
                "value defined over an index that you did not specify?" 
                % (etype, other.cname(), ) )
        if other.is_expression():
            other = _generate_expression__clone_if_needed(other, 0)
        elif other.is_constant():
            other = other()
            other_type = None

    #
    # Binary operators can either be "normal" or "reversed"; reverse all
    # "reversed" opertors
    #
    if etype < 0:
        #
        # This may seem obvious, but if we are performing an
        # "R"-operation (i.e. reverse operation), then simply reverse
        # self and other.  This is legitimate as we are generating a
        # completely new expression here, and the _clone_if_needed logic
        # above will make sure that we don't accidentally clobber
        # someone else's expression (fragment).
        #
        etype *= -1
        _self, other = other, _self
        self_type, other_type = other_type, self_type

    if etype == _sub:
        multiplier = -1
        etype = _add
    else:
        multiplier = 1

    #
    # Now, handle all binary operators
    #
    if etype == _add:
        #
        # self + other
        #
        if self_type is _SumExpression:
            if other_type is _ProductExpression \
                     and len(other._numerator) == 1 \
                     and not other._denominator:
                _self._args += other._numerator
                _self._coef.append(multiplier*other._coef)
                _ProdExpression_Pool.append(other)
            elif other_type is _SumExpression:
                if multiplier < 0:
                    other.negate()
                _self._args += other._args
                _self._coef += other._coef
                _self._const += other._const
                _SumExpression_Pool.append(other)
            elif other_type is None: #NumericConstant:
                _self._const += multiplier * other
                if _self._const==0 and len(_self._coef)==1 and _self._coef[0]==1:
                    _SumExpression_Pool.append(_self)
                    return _self._args.pop()
            else:
                _self._args.append(other)
                _self._coef.append(multiplier)
            return _self
        elif other_type is _SumExpression:
            if multiplier < 0:
                other.negate()
            if self_type is _ProductExpression and \
                   len(_self._numerator) == 1 and \
                   not _self._denominator:
                _self._numerator += other._args
                other._args = _self._numerator
                other._coef.insert(0,_self._coef)
                _ProdExpression_Pool.append(_self)
            elif self_type is None: #NumericConstant:
                other._const += _self
                if other._const==0 and len(other._coef)==1 and other._coef[0]==1:
                    _SumExpression_Pool.append(other)
                    return other._args.pop()
            else:
                other._args.insert(0,_self)
                other._coef.insert(0,1)
            return other
        else:
            if other_type is None:
                if self_type is None:
                    return _self + multiplier * other
                elif other == 0: #NB: multiplier doesn't matter (this is x-0)!
                    return _self
                elif _SumExpression_Pool:
                    ans = _SumExpression_Pool.pop()
                else:
                    ans = _SumExpression()
                ans._const = multiplier * other
                if self_type is _ProductExpression and \
                       len(_self._numerator) == 1 and \
                       not _self._denominator:
                    ans._coef = [ _self._coef ]
                    ans._args = _self._numerator
                    _ProdExpression_Pool.append(_self)
                else:
                    ans._coef = [ 1 ]
                    ans._args = [ _self ]
            elif self_type is None:
                if _self == 0 and multiplier == 1:
                    return other
                elif _SumExpression_Pool:
                    ans = _SumExpression_Pool.pop()
                else:
                    ans = _SumExpression()
                ans._const = _self
                if other_type is _ProductExpression and \
                       len(other._numerator) == 1 and \
                       not other._denominator:
                    ans._coef = [ multiplier * other._coef ]
                    ans._args = other._numerator
                    _ProdExpression_Pool.append(other)
                else:
                    ans._coef = [ multiplier ]
                    ans._args = [ other ]
            else:
                if _SumExpression_Pool:
                    ans = _SumExpression_Pool.pop()
                else:
                    ans = _SumExpression()
                ans._const = 0
                if self_type is _ProductExpression and \
                       len(_self._numerator) == 1 and \
                       not _self._denominator:
                    ans._coef = [ _self._coef ]
                    ans._args = _self._numerator
                    _ProdExpression_Pool.append(_self)
                else:
                    ans._coef = [ 1 ]
                    ans._args = [ _self ]
                if other_type is _ProductExpression and \
                       len(other._numerator) == 1 and \
                       not other._denominator:
                    ans._coef.append( multiplier * other._coef )
                    ans._args += other._numerator
                    _ProdExpression_Pool.append(other)
                else:
                    ans._coef.append( multiplier )
                    ans._args.append( other )
            return ans

    elif etype == _mul:#'mul':
        #
        # self * other
        #
        if self_type is _ProductExpression:
            if other_type is None: #NumericConstant:
                _self._coef *= other
            elif other_type is _ProductExpression:
                _self._numerator += other._numerator
                _self._denominator += other._denominator
                _self._coef *= other._coef
                _ProdExpression_Pool.append(other)
            else:
                _self._numerator.append(other)
            ans = _self
        elif other_type is _ProductExpression:
            if self_type is None: #NumericConstant:
                other._coef *= _self
            else:
                other._numerator.insert(0,_self)
            ans = other
        else:
            if other_type is None:
                if self_type is None:
                    return _self * other
                elif other == 1:
                    return _self
                elif _ProdExpression_Pool:
                    ans = _ProdExpression_Pool.pop()
                else:
                    ans = _ProductExpression()
                ans._coef = other
                ans._numerator = [ _self ]
                ans._denominator = []
            elif self_type is None:
                if _self == 1:
                    return other
                elif _ProdExpression_Pool:
                    ans = _ProdExpression_Pool.pop()
                else:
                    ans = _ProductExpression()
                ans._coef = _self
                ans._numerator = [ other ]
                ans._denominator = []
            else:
                if _ProdExpression_Pool:
                    ans = _ProdExpression_Pool.pop()
                else:
                    ans = _ProductExpression()
                ans._coef = 1
                ans._numerator = [ _self, other ]
                ans._denominator = []

        # Special cases for simplifying expressions
        if ans._coef == 0:
            _ProdExpression_Pool.append(ans)
            return 0 #ZeroConstant
        return ans

    elif etype == _div:#'div':
        #
        # self / other
        #
        if self_type is _ProductExpression:
            if other_type is None: #NumericConstant:
                _self._coef /= other
            elif other_type is _ProductExpression:
                _self._numerator += other._denominator
                _self._denominator += other._numerator
                _self._coef /= other._coef
                _ProdExpression_Pool.append(other)
            else:
                _self._denominator.append(other)
            return _self
        elif other_type is _ProductExpression:
            other.invert()
            if self_type is None: #NumericConstant:
                if _self == 0:
                    return 0
                else:
                    other._coef *= _self
                if len(other._denominator) == 0 and len(other._numerator) == 1\
                       and other._coef == 1:
                    _ProdExpression_Pool.append(other)
                    return other._numerator.pop()
            else:
                other._numerator.insert(0,_self)
            return other
        else:
            if other_type is None: #NumericConstant
                if self_type is None:
                    return _self / other
                elif other == 1:
                    return _self
                elif _ProdExpression_Pool:
                    ans = _ProdExpression_Pool.pop()
                else:
                    ans = _ProductExpression()
                ans._coef = 1/other
                ans._numerator = [ _self ]
                ans._denominator = []
            elif self_type is None:
                if _self == 0:
                    return 0
                elif _ProdExpression_Pool:
                    ans = _ProdExpression_Pool.pop()
                else:
                    ans = _ProductExpression()
                ans._coef = _self
                ans._numerator = []
                ans._denominator = [ other ]
            else:
                if _ProdExpression_Pool:
                    ans = _ProdExpression_Pool.pop()
                else:
                    ans = _ProductExpression()
                ans._coef = 1
                ans._numerator = [ _self ]
                ans._denominator = [ other ]
            return ans    

    elif etype == _pow:#'pow':
        #
        # self ** other
        #
        if other_type is None: #NumericConstant:
            if self_type is None: #NumericConstant:
                # Special case: constant expressions should be
                # immediately reduced
                return _self ** other
            if other == 1:
                return _self
            if other == 0:
                return 1
            other = as_numeric(other)
        elif self_type is None: #NumericConstant:
            if _self == 0:
                return 0
            _self = as_numeric(_self)
        return _PowExpression((_self, other))

    else:
        if etype in _old_etype_strings:
            return generate_expression( _old_etype_strings[etype],
                                        as_numeric(_self), other )
        else:
            raise RuntimeError("Unknown expression type '%s'" % etype)

##
## "static" variables within the generate_expression function
##

# [debugging] clone_counter is a count of the number of calls to
# expr.clone() made during expression generation.
generate_expression.clone_counter = 0

# [configuration] UNREFERENCED_EXPR_COUNT is a "magic number" that
# indicates the stack depth between "normal" modeling and
# _clone_if_needed().  If an expression enters _clone_if_needed() with
# UNREFERENCED_EXPR_COUNT references, then there are no other variables
# that hold a reference to the expression and cloning is not necessary.
# If there are more references than UNREFERENCED_EXPR_COUNT, then we
# must clone the expression before operating on it.  It should be an
# error to hit _clone_if_needed() with fewer than
# UNREFERENCED_EXPR_COUNT references.
UNREFERENCED_EXPR_COUNT = 9


def _generate_relational_expression__clone_if_needed(obj):
    count = getrefcount(obj) - UNREFERENCED_RELATIONAL_EXPR_COUNT
    if count == 0 or count == CHAINED_EXPR_COUNT:
        return obj
    elif count > 0:
        generate_relational_expression.clone_counter += 1
        return obj.clone()
    else:
        raise RuntimeError("Expression entered " \
              "generate_relational_expression() " \
              "with too few references (%s<0); this is indicative of a " \
              "SERIOUS ERROR in the expression reuse detection scheme." \
              % ( count, ))

def _generate_relational_expression__noCloneCheck(obj):
    return obj


def generate_relational_expression(etype, lhs, rhs):
    cloned_from = (id(lhs), id(rhs))
    if generate_relational_expression.chainedInequality is not None:
        prevExpr = generate_relational_expression.chainedInequality
        for arg in prevExpr._cloned_from:
            if arg == id(lhs):
                lhs = prevExpr
                prevExpr = None
                cloned_from = lhs._cloned_from + (cloned_from[1],)
                break
            if arg == id(rhs):
                rhs = prevExpr
                prevExpr = None
                cloned_from = (cloned_from[0],) + rhs._cloned_from
                break
        if prevExpr is not None:
            raise TypeError(chainedInequalityErrorMessage())
        generate_relational_expression.chainedInequality = None

    if lhs.is_expression():
        lhs = _generate_relational_expression__clone_if_needed(lhs)
    elif lhs.is_indexed():
        raise TypeError("Argument for expression '%s' is an indexed "\
              "numeric value specified without an index: %s\n    Is "\
              "variable or parameter '%s' defined over an index that "\
              "you did not specify?" % (etype, lhs.cname(), lhs.cname()))

    if rhs.is_expression():
        rhs = _generate_relational_expression__clone_if_needed(rhs)
    elif rhs.is_indexed():
        raise TypeError("Argument for expression '%s' is an indexed "\
              "numeric value specified without an index: %s\n    Is "\
              "variable or parameter '%s' defined over an index that "\
              "you did not specify?" % (etype, rhs.cname(), rhs.cname()))

    if etype == '==':
        if lhs.is_relational() or rhs.is_relational():
            buf = StringIO()
            if lhs.is_relational():
                lhs.pprint(buf)
            else:
                rhs.pprint(buf)
            raise TypeError("Cannot create an EqualityExpression where "\
                  "one of the sub-expressions is a relational expression:\n"\
                  "    " + buf.getvalue().strip())
        return _EqualityExpression((lhs,rhs))
    else:
        if etype == '<=':
            strict = False
        elif etype == '<':
            strict = True
        else:
            raise ValueError("Unknown relational expression type '%s'" % etype)
        if lhs.is_relational():
            if lhs.__class__ is _InequalityExpression:
                if rhs.is_relational():
                    raise TypeError("Cannot create an InequalityExpression "\
                          "where both sub-expressions are also relational "\
                          "expressions (we support no more than 3 terms "\
                          "in an inequality expression).")
                if len(lhs._args) > 2:
                    raise ValueError("Cannot create an InequalityExpression "\
                          "with more than 3 terms.")
                lhs._args.append(rhs)
                lhs._strict.append(strict)
                lhs._cloned_from = cloned_from
                return lhs
            else:
                buf = StringIO()
                lhs.pprint(buf)
                raise TypeError("Cannot create an InequalityExpression "\
                      "where one of the sub-expressions is an equality "\
                      "expression:\n    " + buf.getvalue().strip())
        elif rhs.is_relational():
            if rhs.__class__ is _InequalityExpression:
                if len(rhs._args) > 2:
                    raise ValueError("Cannot create an InequalityExpression "\
                          "with more than 3 terms.")
                rhs._args.insert(0, lhs)
                rhs._strict.insert(0, strict)
                rhs._cloned_from = cloned_from
                return rhs
            else:
                buf = StringIO()
                rhs.pprint(buf)
                raise TypeError("Cannot create an InequalityExpression "\
                      "where one of the sub-expressions is an equality "\
                      "expression:\n    " + buf.getvalue().strip())
        else:
            return _InequalityExpression([lhs,rhs], [strict], cloned_from)


##
## "static" variables within the generate_relational_expression function
##

# [functionality] chainedInequality allows us to generate symbolic
# expressions of the type "a < b < c".  This provides a buffer to hold
# the first inequality so the second inequality can access it later.
generate_relational_expression.chainedInequality = None

# [debugging] clone_counter is a count of the number of calls to
# expr.clone() made during expression generation.
generate_relational_expression.clone_counter = 0

# [configuration] UNREFERENCED_EXPR_COUNT is a "magic number" that
# indicates the stack depth between "normal" modeling and
# _clone_if_needed().  If an expression enters _clone_if_needed() with
# UNREFERENCED_EXPR_COUNT references, then there are no other variables
# that hold a reference to the expression and cloning is not necessary.
# If there are more references than UNREFERENCED_EXPR_COUNT, then we
# must clone the expression before operating on it.  It should be an
# error to hit _clone_if_needed() with fewer than
# UNREFERENCED_EXPR_COUNT references.
UNREFERENCED_RELATIONAL_EXPR_COUNT = 9

# [configuration] CHAINED_EXPR_COUNT is a "magic number" that indicates
# the relative stack depth for compound inequality expressions of the
# type "a < b < c".  Since Python creates the first inequality as
# temporary, and releases it after evaluating __nonzero__(), that
# expression's refcount will be CHAINED_EXPR_COUNT less than the normal
# UNREFERENCED_EXPR_COUNT.
CHAINED_EXPR_COUNT = -5


#
# If you want to completely disable clone checking (e.g., for
# line-profiling this file), set the following to "if True".
#
if not _getrefcount_available:
    _generate_relational_expression__clone_if_needed = \
        _generate_relational_expression__noCloneCheck
    _generate_expression__clone_if_needed = \
        _generate_expression__noCloneCheck


if False: #pragma:nocover
    ExpressionRegistration('<', _InequalityExpression)
    ExpressionRegistration('lt', _InequalityExpression)
    ExpressionRegistration('>', _InequalityExpression, True)
    ExpressionRegistration('gt', _InequalityExpression, True)
    ExpressionRegistration('<=', _InequalityExpression)
    ExpressionRegistration('lte', _InequalityExpression)
    ExpressionRegistration('>=', _InequalityExpression, True)
    ExpressionRegistration('gte', _InequalityExpression, True)
    ExpressionRegistration('=', _EqualityExpression)
    ExpressionRegistration('eq', _EqualityExpression)

if False: #pragma:nocover
    ExpressionRegistration('+', _SumExpression)
    ExpressionRegistration('sum', _SumExpression)
    ExpressionRegistration('*', _ProductExpression)
    ExpressionRegistration('prod', _ProductExpression)
    #ExpressionRegistration('-', _MinusExpression)
    #ExpressionRegistration('minus', _MinusExpression)
    #ExpressionRegistration('/', _DivisionExpression)
    #ExpressionRegistration('divide', _DivisionExpression)
    #ExpressionRegistration('-', _NegateExpression)
    #ExpressionRegistration('negate', _NegateExpression)
    ExpressionRegistration('abs', _AbsExpression)
    ExpressionRegistration('pow', _PowExpression)
