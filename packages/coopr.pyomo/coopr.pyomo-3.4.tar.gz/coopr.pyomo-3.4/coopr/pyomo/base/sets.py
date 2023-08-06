#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

# TODO
# . rename 'filter' to something else
# . confirm that filtering is efficient

__all__ = ['Set', '_SetContainer', '_SetArray', 'set_options', 'simple_set_rule', 'SetOf']

import logging
import sys
import types
import copy
import itertools
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
try:
    import bidict
    using_bidict=True
except:
    using_bidict=False

import pyutilib.misc

from coopr.pyomo.base.misc import apply_indexed_rule, apply_parameterized_indexed_rule
from coopr.pyomo.base.component import Component, register_component

try:
    long
    intlist = [int, long, float]
except:
    intlist = [int, float]
    xrange = range

logger = logging.getLogger('coopr.pyomo')


def set_options(**kwds):
    """
    This is a decorator for set initializer functions.  This
    decorator allows an arbitrary dictionary of values to passed
    through to the set constructor.

    Example:
    TODO
    """
    def decorator(func):
        func.set_options = kwds
        return func
    return decorator


def simple_set_rule( fn ):
    """This is a decorator that translates None into Set.End.
    This supports a simpler syntax in set rules, though these can be
    more difficult to debug when errors occur.

    Example:

    @simple_set_rule
    def A_rule(model, i, j):
        ...
    """

    def wrapper_function ( *args, **kwargs ):
        value = fn( *args, **kwargs )
        if value is None:
            return Set.End
        return value
    return wrapper_function


class Set(Component):
    """Set objects that are used to index other Pyomo objects

       This class has a similar look-and-feel as a built-in set class.  However,
       the set operations defined in this class return another abstract
       Set object.  This class contains a concrete set, which can be
       initialized by the load() method.
    
    Constructor
        Arguments:
           name          The name of the set
           within        A set that defines the type of values that can
                          be contained in this set
           rule
           initialize    Default set members, which may be overriden
                          when setting up this set
           validate      Define a function for validating membership in a
                          set.  This has the functional form:
                          f: data -> bool
                          and returns true if the data belongs in the set
           dimen         Specify the set's arity.
           doc           Documentation for this object
           virtual       Indicate that this is a virtual set that does not
                            have concrete members.
    """

    End             = (1003,)

    def __new__(cls, *args, **kwds):
        if cls != Set:
            return super(Set, cls).__new__(cls)
        if args == ():
            return _SetContainer.__new__(_SetContainer)
        else:
            return _SetArray.__new__(_SetArray)

    def __init__(self, **kwds):
        self.order=[]
        # IMPT: order_dict keys are 1-based.
        if using_bidict:
            self.order_dict = bidict.bidict()
        else:
            self.order_dict = {}
            self.order_dict_inv = {}

        # 'rule' and 'initialize' are mutually exclusive options
        if "rule" in kwds and "initialize" in kwds:
            raise TypeError("Cannot specify both 'rule' and 'initialize' " + \
                  "keywords in '%s'" % str(self))

        # Get keyword arguments
        kwds.setdefault("name", "_unknown_")
        self.initialize = kwds.pop("rule", None)
        self.initialize = kwds.pop("initialize", self.initialize)
        self.validate   = kwds.pop("validate", None)
        self.ordered    = kwds.pop("ordered", False)
        self.virtual    = kwds.pop("virtual", False)
        self.concrete   = not self.virtual
        self._bounds    = kwds.pop("bounds", None)
        self.filter     = kwds.pop("filter", None)

        # We can't access self.dimen after its been written, so we use
        # tmp_dimen until the end of __init__
        tmp_dimen = None

        # Get dimen from within, if possible
        self.domain = kwds.pop("within", None)
        if self.domain is not None:
            tmp_dimen = self.domain.dimen
        if self._bounds is None and not self.domain is None:
            self._bounds = copy.copy(self.domain._bounds)

        # Make sure dimen and implied dimensions don't conflict
        kwd_dimen = kwds.pop("dimen", None)
        if kwd_dimen is not None:
            if self.domain is not None and tmp_dimen != kwd_dimen:
                raise ValueError(\
                      ("Value of keyword 'dimen', %s, differs from the " + \
                       "dimension of the superset '%s', %s") % \
                       (str(kwd_dimen), str(self.domain.name), str(tmp_dimen)))
            else:
                tmp_dimen = kwd_dimen

        kwds.setdefault('ctype', Set)
        Component.__init__(self, **kwds)

        if tmp_dimen is None:
            # We set the default to 1
            tmp_dimen = 1
        if self.initialize is not None:
            #
            # Convert generators to lists, since a generator is not copyable
            #
            if type(self.initialize) is types.GeneratorType:
                self.initialize = list(self.initialize)
            #
            # Try to guess dimen from the initialize list
            #
            tmp=None
            if type(self.initialize) is tuple:
                tmp = len(self.initialize)
            elif type(self.initialize) is list and len(self.initialize) > 0 \
                     and type(self.initialize[0]) is tuple:
                tmp = len(self.initialize[0])
            else:
                tmp = getattr(self.initialize, 'dimen', tmp)
            if tmp is not None:
                if kwd_dimen is not None and tmp != kwd_dimen:
                    raise ValueError("Dimension argument differs from the data in the initialize list")
                else:
                    tmp_dimen = tmp

        self.dimen = tmp_dimen

    def valid_model_component(self):
        if self.virtual and not self.concrete:
            return False
        return True

    def reset(self):
        pass

    def dim(self):
        return self._ndim

    def display(self, ostream=None, verbose=False):
        self.pprint(ostream=ostream, verbose=verbose)

    def _verify(self, element, use_exception=True):
        # A utility routine that is used to verify if the element
        # is valid for this set.
        if self.domain is not None and element not in self.domain:
            if use_exception:
                raise ValueError("The value="+str(element)+" is not valid for set="+self.name+", because it is not within the domain="+self.domain.name)
            return False
        if self.validate is not None:
            flag = False
            try:
                if self._parent is not None:
                    flag = apply_indexed_rule(self, self.validate, self._parent(), element)
                else:
                    flag = apply_indexed_rule(self, self.validate, None, element)
            except:
                pass
            if not flag:
                if use_exception:
                    raise ValueError("The value="+str(element)+" violates the validation rule of set="+self.name)
                return False
        if self.dimen > 1 and type(element) is not tuple:
            if use_exception:
                raise ValueError("The value="+str(element)+" is not a tuple for set="+self.name+", which has dimen="+str(self.dimen))
            return False
        elif self.dimen == 1 and type(element) is tuple:
            if use_exception:
                raise ValueError("The value="+str(element)+" is a tuple for set="+self.name+", which has dimen="+str(self.dimen))
            return False
        elif type(element) is tuple and len(element) != self.dimen:
            if use_exception:
                raise ValueError("The value="+str(element)+" does not have dimension="+str(self.dimen)+", which is needed for set="+self.name)
            return False
        return True

    def bounds(self):
        """Return bounds information.  The default value is 'None', which
        indicates that this set does not contain bounds."""
        return self._bounds



class _SetContainer(Set):
    """A derived Set object that contains a single set."""

    def __init__(self, *args, **kwds):
        """ Constructor """
        if args != ():
            raise TypeError("A _SetContainer expects no arguments")
        self._index_set=None
        self._index=[None]
        self._ndim=0
        self.value=set()
        Set.__init__(self, **kwds)

    def construct(self, values=None):
        """ Apply the rule to construct values in this set """
        if __debug__:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Constructing _SetContainer, name="+self.name+", from data="+repr(values))
        if self._constructed:
            return
        self._constructed=True

        if self.initialize is None:
            self.initialize = getattr(self,'rule',None)
        #
        # Construct using the input values list
        #
        if values is not None:
            if type(self._bounds) is tuple:
                first=self._bounds[0]
                last=self._bounds[1]
            else:
                first=None
                last=None
            all_numeric=True
            for val in values[None]:
                # Skip the value if it is filtered
                if not self.filter is None and \
                   not apply_indexed_rule(self, self.filter, self._parent(), val):
                    continue
                if type(val) in intlist:
                    if first is None or val<first:
                        first=val
                    if last is None or val>last:
                        last=val
                else:
                    all_numeric=False
                self.add(val)
            if all_numeric:
                self._bounds = (first, last)
        #
        # Construct using the rule
        #
        elif type(self.initialize) is types.FunctionType:
            if self._parent is None:
                raise ValueError("Must pass the parent block in to initialize with a function")
            if self.initialize.__code__.co_argcount == 1:
                #
                # Using a rule of the form f(model) -> iterator
                #
                tmp = self.initialize(self._parent())
                for val in tmp:
                    if self.dimen is None:
                        if type(val) in [tuple,list]:
                            self.dimen=len(val)
                        else:
                            self.dimen=1
                    if not self.filter is None and \
                       not apply_indexed_rule(self, self.filter, self._parent(), val):
                        continue
                    self.add(val)
            else:
                #
                # Using a rule of the form f(model, z) -> element
                #
                ctr=1
                val = apply_indexed_rule(self, self.initialize, self._parent(), ctr)
                if val is None:
                    raise ValueError("Set rule returned None instead of Set.Skip")
                if self.dimen is None:
                    if type(val) in [tuple,list] and not val == Set.End:
                        self.dimen=len(val)
                    else:
                        self.dimen=1
                while not (val.__class__ is tuple and val == Set.End):
                    # Add the value if the filter is None or the filter return value is True
                    if self.filter is None or \
                       apply_indexed_rule(self, self.filter, self._parent(), val):
                       self.add(val)
                    ctr += 1
                    val = apply_indexed_rule(self, self.initialize, self._parent(), ctr)
                    if val is None:
                        raise ValueError("Set rule returned None instead of Set.Skip")
        
            # Update the bounds if after using the rule, the set is 
            # a one dimensional list of all numeric values
            if self.dimen == 1:
                if type(self._bounds) is tuple:
                    first=self._bounds[0]
                    last=self._bounds[1]
                else:
                    first=None
                    last=None
                all_numeric=True
                for val in self.value:
                    if type(val) in intlist:
                        if first is None or val<first:
                            first=val
                        if last is None or val>last:
                            last=val
                    else:
                        all_numeric=False
                        break
                if all_numeric:
                    self._bounds = (first, last)

        #
        # Construct using the default values
        #
        elif self.initialize is not None:
            if type(self.initialize) is dict:
                raise ValueError("Cannot initialize set "+self.name+" with dictionary data")
            if type(self._bounds) is tuple:
                first=self._bounds[0]
                last=self._bounds[1]
            else:
                first=None
                last=None
            all_numeric=True
            for val in self.initialize:
                # Skip the value if it is filtered
                if not self.filter is None and \
                   not apply_indexed_rule(self, self.filter, self._parent(), val):
                    continue
                if type(val) in intlist:
                    if first is None or val<first:
                        first=val
                    if last is None or val>last:
                        last=val
                else:
                    all_numeric=False
                self.add(val)
            if all_numeric:
                self._bounds = (first,last)

    def data(self):
        """The underlying set data."""
        if not self.concrete:
            raise TypeError("Cannot access underlying set data for a non-concrete set "+self.name)
        return self.value

    def clear(self):
        """Remove all elements from the set."""
        if self.virtual:
            raise TypeError("Cannot clear virtual Set object `"+self.name+"'")
        self.value.clear()
        if using_bidict:
            self.order_dict = bidict.bidict()
        else:
            self.order_dict = {}
            self.order_dict_inv = {}

    def check_values(self):
        """ Verify that the values in this set are valid.
        """
        if self.virtual:
            return
        for val in self.value:
            self._verify(val)

    def add(self, *args):
        """Add one or more elements to a set."""
        if self.virtual:
            raise TypeError("Cannot add elements to virtual set `"+self.name+"'")

        for val in args:
            tmp = pyutilib.misc.flatten_tuple(val)
            self._verify(tmp)
            try:
                if tmp in self.value:
                    # because this is a set, this isn't technically a problem. but based on experience, 
                    # in 90% of the cases (statistic made up on the spot) the user probably didn't intend
                    # for this, and would like to know about a potential issue in their input data.
                    print("***WARNING: Element "+str(tmp)+" already exists in set "+self.name+"; no action taken.")
                    continue
                self.value.add(tmp)
                if self.ordered:
                    if tmp in self.order_dict:
                        raise ValueError("Element "+str(tmp)+" already exists in ordered set "+self.name)
                    self.order.append(tmp)
                    if using_bidict:
                        self.order_dict[tmp:] = len(self.order)
                    else:
                        self.order_dict[tmp] = len(self.order)
                        self.order_dict_inv[len(self.order)] = tmp


            except TypeError:
                raise TypeError("Problem inserting "+str(tmp)+" into set "+self.name)

    def remove(self, element):
        """Remove an element from the set.
           If the element is not a member, raise an error.
        """
        if self.virtual:
            raise KeyError("Cannot remove element `"+str(element)+"' from virtual set "+str(self.name))
        if element not in self.value:
            raise KeyError("Cannot remove element `"+str(element)+"' from set "+str(self.name))
        self.value.remove(element)
        if self.ordered:
            id = self.order_dict[element]-1
            for i in xrange(id+1,len(self.order)):
                if using_bidict:
                    self.order_dict[self.order[i]] = i
                else:
                    self.order_dict[self.order[i]] = i
                    self.order_dict_inv[i] = self.order[i]
            del self.order[id]

    def discard(self, element):
        """Remove an element from the set.
           If the element is not a member, do nothing.
        """
        if self.virtual:
            raise KeyError("Cannot discard element `"+str(element)+"' from virtual set "+str(self.name))
        if self.ordered and element in self.value:
            self.order.remove(element)
        self.value.discard(element)

    def first(self):
        if not self.concrete:
            raise TypeError("Cannot access the first element of a non-concrete set `"+self.name+"'")
        return self.member(1)

    def last(self):
        if self.virtual:
            raise TypeError("Cannot access the last element of a non-concrete set `"+self.name+"'")
        return self.member(len(self.value))

    def __getitem__(self, key):
        return self.member(key)

    def member(self, key):
        if not self.concrete:
            raise TypeError("Cannot access a specific element of a non-concrete set `"+self.name+"'")
        if self.ordered:
            if using_bidict:
                return self.order_dict.inv[key]
            else:
                return self.order_dict_inv[key]
        #
        # If the set is not ordered, then we use the intrinsic ordering imposed by the set.
        # We convert the set to a list and return the specified value.
        #
        if key >= 1:
            return list(self.value)[key-1]
        elif key < 0:
            return list(self.value)[key]
        else:
            raise IndexError("Valid index values for sets are 1 ... len(set) or -1 ... -len(set)")

    def ord(self, match_element):
        """ For ordered sets, return the position index (1-based)
            of the input element.
        """
        if self.ordered is False:
            raise AttributeError("Cannot invoke ord() method for unordered set="+str(self.name))
        try:
            return self.order_dict[match_element]
        except IndexError:
            raise IndexError("Unknown input element="+str(match_element)+" provided as input to ord() method for set="+str(self.name))

    def next(self, match_element, k=1):
        # NOTE: we currently aren't consist (and don't actually deal with) w.r.t. unordered sets - see the implementation of member() above.
        try:
            element_position = self.order_dict[match_element]
        except KeyError:
            raise KeyError("Cannot obtain next() member of set="+self.name+"; input element="+str(match_element)+" is not a member of the set!")

        try:
            return self.order[element_position+k-1] # "order" is a list, accessed 0-based.
        except KeyError:
            raise KeyError("Cannot obtain next() member of set="+self.name+"; failed to access item in position="+str(element_position+k-1))

    def nextw(self, match_element, k=1):
        ndx = self.order_dict[match_element]+k
        total = len(self.order)
        if ndx > total:
            ndx -= total
        if ndx <= 0:
            ndx += total
        return self.order_dict.inv[ndx]

    def prev(self, match_element, k=1):
        return self.next(match_element, k=-k)

    def prevw(self, match_element, k=1):
        return self.nextw(match_element, k=-k)

    def pprint(self, ostream=None, verbose=False):
        if ostream is None:
            ostream = sys.stdout
        ostream.write("   "+self.name+" : ")
        if not self.doc is None:
            ostream.write(self.doc+'\n')
            ostream.write("  ")
        ostream.write("\tDim="+str(self.dim())+' ')
        ostream.write("\tDimen="+str(self.dimen)+' ')
        ostream.write("\tSize="+str(len(self))+' ')
        if self.domain is not None:
            ostream.write("\tDomain="+str(self.domain.name)+' ')
        else:
            ostream.write("\tDomain="+str(None)+' ')
        ostream.write("\tOrdered="+str(self.ordered)+' ')
        ostream.write("\tBounds="+str(self._bounds)+'\n')
        if self.model() is None:
            ostream.write("\t Model=unknown\n")
        else:
            ostream.write("\t Model="+str(self.model().name)+'\n')
        if not self.concrete or (self.virtual and not verbose):
            ostream.write("\t  Virtual\n")
        else:
            if self.ordered:
                tmp = copy.copy(self.order)
            else:
                tmp = copy.copy(list(self.data()))
                tmp.sort()
            ostream.write("\t   "+str(tmp)+'\n')

    def __len__(self):
        """ The number of items in the set.
            The set is empty until a concrete instance has been setup.
        """
        if not self.concrete:
            raise ValueError("The size of a non-concrete set is unknown")
        return len(self.data())

    def __iter__(self):
        """Return an iterator for the underlying set"""
        if self.virtual:
            raise TypeError("Cannot iterate over Set object `"+self.name+"', which is a virtual set")
        if self.ordered:
            return self.order.__iter__()
        return self.value.__iter__()

    def __reversed__(self):
        return reversed(self.__iter__())

    def __hash__(self):
        """Hash this object"""
        return Set.__hash__(self)

    def __eq__(self,other):
        """ Equality comparison """
        if id(self) == id(other):
            return True
        if other is None:
            return False
        try:
            tmp = self._set_repn(other)
        except:
            return False
        if self.virtual:
            if tmp.virtual:
                return hash(self) == hash(tmp)
            return False
        if tmp.virtual:
            return False
        if self.dimen != tmp.dimen:
            return False
        return self.value.__eq__( tmp.data() )

    def __ne__(self,other):
        return not self.__eq__(other)

    def __contains__(self, element):
        """Report whether an element is a member of this set.
        (Called in response to the expression 'element in self'.)
        """
        #
        # If the element is a set, then see if this is a subset
        #
        # NB: since 95+% of all sets are indexed by int's (or tuples of
        # ints) this is a quick test that can avoid (expensive)
        # isinstance calls that usually return "False".
        #
        element_t = type(element)
        if element_t is not int and element_t is not tuple and \
               isinstance(element,_SetContainer):
            return element.issubset(self)
        # 
        # When dealing with a concrete set, just check if the element is
        # in the set. there is no need for extra validation.
        #        
        if self._constructed and self.concrete is True:
           return self._set_contains(element)
        #
        # If this is not a valid element, then return False
        #
        if not self._verify(element,False):
            return False
        #
        # If the restriction rule is used then we do not actually
        # check whether the data is in the set self.value.
        #
        if self.validate is not None and not self.concrete:
            return True
        #
        # The final check: return true if self.concrete is False, since we should
        # have already validated this value.  The following, or at least one of
        # the execution paths - is probably redundant with the above.
        #
        return not self.concrete or self._set_contains(element)

    def _set_contains(self, element):
        return element in self.value

    def isdisjoint(self, other):
        """Return True if the set has no elements in common with other. Sets are disjoint if and only if their intersection is the empty set."""
        other = self._set_repn(other)
        tmp = self & other
        for elt in tmp:
            return False
        return True
        
    def issubset(self,other):
        """Report whether another set contains this set"""
        other = self._set_repn(other)
        if self.dimen != other.dimen:
            raise ValueError("Cannot perform set operation with sets "+self.name+" and "+other.name+" that have different element dimensions: "+str(self.dimen)+" "+str(other.dimen))
        if not self.concrete:
            raise TypeError("ERROR: cannot perform \"issubset\" test because the current set is not a concrete set.")
        for val in self:
            if val not in other:
                return False
        return True

    def __lt__(self,other):
        return self <= other and not self == other

    def issuperset(self, other):
        """Report this set contains another set"""
        other = self._set_repn(other)
        if self.dimen != other.dimen:
            raise ValueError("Cannot perform set operation with sets "+self.name+" and "+other.name+" that have different element dimensions: "+str(self.dimen)+" "+str(other.dimen))
        if not other.concrete:
            raise TypeError("ERROR: cannot perform \"issuperset\" test because the target set is not a concrete set.")
        for val in other:
            if val not in self:
                return False
        return True

    def __gt__(self,other):
        return self >= other and not self == other

    __le__ = issubset
    __ge__ = issuperset

    def _set_repn(self, other):
        if isinstance(other,_SetContainer):
            return other
        return SetOf(other)

    def union(self, *args):
        """Return the union of this set with one or more sets"""
        tmp = self
        for arg in args:
            tmp = _SetUnion(tmp, arg)
        return tmp

    def __or__(self,other):
        """Return the union of this set with another set"""
        return self.union(other)

    def intersection(self, *args):
        """Return the intersection of this set with one or more sets"""
        tmp = self
        for arg in args:
            tmp = _SetIntersection(tmp, arg)
        return tmp

    def __and__(self,other):
        """Return the intersection of this set with another set"""
        return self.intersection(other)

    def difference(self, *args):
        """Return the difference between this set with one or more sets"""
        tmp = self
        for arg in args:
            tmp = _SetDifference(tmp, arg)
        return tmp

    def __sub__(self,other):
        """Return the difference between this set and another set"""
        return self.difference(other)

    def symmetric_difference(self, *args):
        """Return the symmetric difference of this set with one or more sets"""
        tmp = self
        for arg in args:
            tmp = _SetSymmetricDifference(tmp, arg)
        return tmp

    def __xor__(self,other):
        """Return the symmetric difference of this set with another set"""
        return self.symmetric_difference(other)

    def cross(self, *args):
        """Return a cross-product between this set and one or more sets"""
        tmp = self
        for arg in args:
            tmp = _SetProduct(tmp, arg)
        return tmp

    def __mul__(self,other):
        """Return a cross-product between this set and another set"""
        return self.cross(other)


class SetOf(_SetContainer):
    """A derived _SetContainer object that creates a set from external data without duplicating it."""

    def __init__(self, *args, **kwds):
        if len(args) != 1:
            raise TypeError("Only one set data argument can be specified")
        _SetContainer.__init__(self,**kwds)
        self.value = None
        self._constructed = True
        self.virtual = False
        self.concrete = True
        #
        self._data = args[0]
        try:
            self.dimen = 0
            for i in self._data:
                if type(i) is tuple:
                    self.dimen = len(i)
                else:
                    self.dimen = 1
                break
        except TypeError:
            e = sys.exc_info()[1]
            raise TypeError("Cannot create a Pyomo set: "+e)

    def construct(self, values=None):
        """Disabled construction method"""
        pass

    def __len__(self):
        """The number of items in the set."""
        try:
            return len(self._data)
        except:
            pass
        ctr = 0
        for i in self:
            ctr += 1
        return ctr

    def __iter__(self):
        """Return an iterator for the underlying set"""
        for i in self._data:
            yield i

    def _set_contains(self, element):
        return element in self._data
        
    def data(self):
        """The underlying set data."""
        return set(self)

    def __eq__(self, other):
        """ Equality comparison """
        if other is None:
            return False
        other = self._set_repn(other)
        if self.dimen != other.dimen:
            return False
        ctr = 0
        for i in self:
            if not i in other:
                return False
            ctr += 1
        return ctr == len(other)
            

class _SetOperator(_SetContainer):
    """A derived _SetContainer object that contains a concrete virtual single set."""

    def __init__(self, *args, **kwds):
        if len(args) != 2:
            raise TypeError("Two arguments required for a binary set operator")
        dimen_test = kwds.get('dimen_test',True)
        if 'dimen_test' in kwds:
            del kwds['dimen_test']
        _SetContainer.__init__(self,**kwds)
        self.value = None
        self._constructed = True
        self.virtual = True
        self.concrete = True
        #
        self._setA = args[0]
        if not self._setA.concrete:
            raise TypeError("Cannot perform set operations with non-concrete set '"+self._setA.name+"'")
        if isinstance(args[1],_SetContainer):
            self._setB = args[1]
        else:
            self._setB = SetOf(args[1])
        if not self._setB.concrete:
            raise TypeError("Cannot perform set operations with non-concrete set '"+self._setB.name+"'")
        if dimen_test and self._setA.dimen != self._setB.dimen:
            raise ValueError("Cannot perform set operation with sets "+self._setA.name+" and "+self._setB.name+" that have different element dimensions: "+str(self._setA.dimen)+" "+str(self._setB.dimen))
        self.dimen = self._setA.dimen
        #
        self.ordered = self._setA.ordered and self._setB.ordered

    def construct(self, values=None):
        """ Disabled construction method """
        pass

    def __len__(self):
        """The number of items in the set."""
        ctr = 0
        for i in self:
            ctr += 1
        return ctr

    def __iter__(self):
        """Return an iterator for the underlying set"""
        raise IOError("Undefined set iterator")

    def _set_contains(self, element):
        raise IOError("Undefined set operation")
        
    def data(self):
        """The underlying set data."""
        return set(self)

    def __eq__(self, other):
        """ Equality comparison """
        if other is None:
            return False
        other = self._set_repn(other)
        if self.dimen != other.dimen:
            return False
        ctr = 0
        for i in self:
            if not i in other:
                return False
            ctr += 1
        return ctr == len(other)
            

class _SetUnion(_SetOperator):

    def __init__(self, *args, **kwds):
        _SetOperator.__init__(self, *args, **kwds)

    def __iter__(self):
        for elt in self._setA:
            yield elt
        for elt in self._setB:
            if not elt in self._setA:
                yield elt

    def _set_contains(self, elt):
        return elt in self._setA or elt in self._setB
    

class _SetIntersection(_SetOperator):

    def __init__(self, *args, **kwds):
        _SetOperator.__init__(self, *args, **kwds)

    def __iter__(self):
        for elt in self._setA:
            if elt in self._setB:
                yield elt

    def _set_contains(self, elt):
        return elt in self._setA and elt in self._setB
    

class _SetDifference(_SetOperator):

    def __init__(self, *args, **kwds):
        _SetOperator.__init__(self, *args, **kwds)

    def __iter__(self):
        for elt in self._setA:
            if not elt in self._setB:
                yield elt

    def _set_contains(self, elt):
        return elt in self._setA and not elt in self._setB
    

class _SetSymmetricDifference(_SetOperator):

    def __init__(self, *args, **kwds):
        _SetOperator.__init__(self, *args, **kwds)

    def __iter__(self):
        for elt in self._setA:
            if not elt in self._setB:
                yield elt
        for elt in self._setB:
            if not elt in self._setA:
                yield elt

    def _set_contains(self, elt):
        return elt in self._setA ^ elt in self._setB
    

class _SetProduct(_SetOperator):

    def __init__(self, *args, **kwd):
        kwd['dimen_test'] = False
        _SetOperator.__init__(self, *args, **kwd)
        # the individual index sets definining the product set.
        if isinstance(self._setA,_SetProduct):
            self.set_tuple = self._setA.set_tuple
        else:
            self.set_tuple = [self._setA]
        if isinstance(self._setB,_SetProduct):
            self.set_tuple += self._setB.set_tuple
        else:
            self.set_tuple.append(self._setB)
        # set the "dimen" instance attribute.
        self._compute_dimen()

    def __iter__(self):
        if self.is_flat_product():
            for i in itertools.product(*self.set_tuple):
                yield i
        else:
            for i in itertools.product(*self.set_tuple):
                yield pyutilib.misc.flatten_tuple(i)

    def _set_contains(self, element):
        # Do we really need to check if element is a tuple???
        # if type(element) is not tuple:
        #    return False
        try:
            ctr = 0
            for subset in self.set_tuple:
                d = subset.dimen
                if d == 1:
                    if not subset._set_contains(element[ctr]):
                        return False
                else:
                    # cast to tuple is not needed: slices of tuples
                    # return tuples!
                    if not subset._set_contains(element[ctr:ctr+d]):
                        return False

                ctr += d
            return ctr == len(element)
        except:
            return False
        
    def __len__(self):
        ans = 1
        for _set in self.set_tuple:
            ans *= len(_set)
        return ans

    def _compute_dimen(self):
        ans=0
        for _set in self.set_tuple:
            if _set.dimen is None:
                self.dimen=None
                return
            else:
                ans += _set.dimen
        self.dimen = ans

    def is_flat_product(self):
        """
        a simple utility to determine if each of the composite sets is
        of dimension one. knowing this can significantly reduce the
        cost of iteration, as you don't have to call flatten_tuple.
        """

        for s in self.set_tuple:
            if s.dimen != 1:
                return False
        return True

    def _verify(self, element, use_exception=True):
        """
        If this set is virtual, then an additional check is made
        to ensure that the element is in each of the underlying sets.
        """
        tmp = _SetContainer._verify(self, element, use_exception)
        return tmp

        # WEH - when is this needed?
        if not tmp or not self.virtual:
            return tmp

        next_tuple_index = 0
        member_set_index = 0
        for member_set in self.set_tuple:
            tuple_slice = element[next_tuple_index:next_tuple_index + member_set.dimen]
            if member_set.dimen == 1:
                tuple_slice = tuple_slice[0]
            if tuple_slice not in member_set:
                return False
            member_set_index += 1
            next_tuple_index += member_set.dimen
        return True


class _SetArray(Set):
    """An array of sets, which are indexed by other sets"""

    def __init__(self, *args, **kwds):      #pragma:nocover
        """ Constructor """
        self._index_set=None
        self.value=OrderedDict()
        self._ndim=len(args)
        if len(args) == 1:
            if isinstance(args[0],Set):
                self._index=args[0]
            else:
                try:
                    options = getattr(args[0],'set_options')
                    options['initialize'] = args[0]
                    self._index=Set(**options)
                except:
                    self._index=Set(initialize=args[0])
        else:
            self._index=None
            tmp = []
            for arg in args:
                if isinstance(arg,Set):
                    tmp.append(arg)
                else:
                    try:
                        options = getattr(arg,'set_options')
                        options['initialize'] = arg
                        tmp.append( Set(**options) )
                    except:
                        tmp.append( Set(initialize=arg) )
            self._index_set=tuple(tmp)
        Set.__init__(self, **kwds)
        self.value=OrderedDict()

    def keys(self):
        return self.value.keys()

    def __contains__(self, element):
        return element in self.value.keys()

    def clear(self):
        """Remove all elements from the set."""
        for key in self.value:
            self.value[key].clear()

    def data(self):
        """The underlying set data."""
        raise TypeError("Cannot access underlying set data for array set "+self.name)

    def __getitem__(self, key):
        if key not in self.value:
            if (key in self._index) and (self.initialize is not None) and (type(self.initialize) in [tuple,list]):
                return self.initialize
            raise KeyError("Cannot access index "+str(key)+" in array set "+self.name)
        return self.value[key]

    def __setitem__(self, key, val):
        if key not in self._index:
            raise KeyError("Cannot set index "+str(key)+" in array set "+self.name)
        if key in self.value:
            self.value[key].clear()
            for elt in val:
                self.value[key].add(elt)
        else:
            self.value[key] = Set(initialize=val,within=self.domain,validate=self.validate,ordered=self.ordered,name=self.name+"["+str(key)+"]",dimen=self.dimen)
            self.value[key].construct()

    def __len__(self):
        result = 0
        for val in self.value.values():
            result += len(val)
        return result

    def __iter__(self):
        """Return an iterator for the set array"""
        return self.value.__iter__()

    def check_values(self):
        for key in self.value:
            for val in self.value[key]:
                self._verify(val,True)

    def pprint(self, ostream=None, verbose=False):
        if ostream is None:
            ostream = sys.stdout
        ostream.write("   "+self.name+" : ")
        if not self.doc is None:
            ostream.write(self.doc+'\n')
            ostream.write("  ")
        ostream.write("\tDim="+str(self.dim())+' ')
        ostream.write("\tDimen="+str(self.dimen)+' ')
        if self.domain is None:
            ostream.write("\tDomain="+str(self.domain)+' ')
        else:
            ostream.write("\tDomain="+str(self.domain.name)+' ')
        ostream.write("\tArraySize="+str(len(self.value.keys()))+' ')
        ostream.write("\tOrdered="+str(self.ordered)+'\n')
        if self.model() is None:
            ostream.write("\t Model=None\n")
        else:
            ostream.write("\t Model="+str(self.model().name)+'\n')
        tmp=list(self.value.keys())
        if tmp is not None:
            tmp.sort()
        else:
            tmp=[]
        for val in tmp:
            if self.ordered:
                ttmp = copy.copy(self.value[val].order)
            else:
                ttmp = copy.copy(list(self.value[val].value))
                ttmp.sort()
            ostream.write("\t"+self.name+"["+str(val)+"]\t"+str(ttmp)+'\n')

    def construct(self, values=None):
        """ Apply the rule to construct values in each set"""
        if __debug__:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Constructing _SetArray, name="+self.name+", from data="+repr(values))
        if self._constructed:
            return
        self._constructed=True
        if self.virtual:                                #pragma:nocover
            raise TypeError("It doesn't make sense to create a virtual set array")

        if self.initialize is None:
            self.initialize = getattr(self,'rule',None)

        #
        # Construct using the values list
        #
        if values is not None:
            for key in values:
                if type(key) is tuple and len(key)==1:
                    tmpkey=key[0]
                else:
                    tmpkey=key
                if tmpkey not in self._index:
                    raise KeyError("Cannot set index "+str(tmpkey)+" in array set "+self.name)
                self.value[tmpkey] = Set(initialize=values[key],within=self.domain,validate=self.validate,ordered=self.ordered,name=self.name+"["+str(tmpkey)+"]",dimen=self.dimen)
                self.value[tmpkey]._parent = self._parent
                self.value[tmpkey].construct()
        #
        # Construct using the rule
        #
        elif type(self.initialize) is types.FunctionType:
            if self._parent is None:
                raise ValueError("Need parent block to construct a set array with a function")
            if self._index is None:
                raise ValueError("No index for set "+self.name)
            for key in self._index:
                self.value[key] = Set(within=self.domain,validate=self.validate,ordered=self.ordered,name=self.name+"["+str(key)+"]",dimen=self.dimen)
                self.value[key]._parent = self._parent
                self.value[key].construct()
                #
                if isinstance(key,tuple):
                    tmp = key
                else:
                    tmp = (key,)
                if self.initialize.__code__.co_argcount == len(tmp)+1:
                    rule_list = apply_indexed_rule(self, self.initialize, self._parent(), tmp)
                    for val in rule_list:
                        self.value[key].add( val )
                else:
                    ctr=1
                    val = apply_parameterized_indexed_rule(self, self.initialize, self._parent(), ctr, tmp)
                    if val is None:
                        raise ValueError("Set rule returned None instead of Set.Skip")
                    while not (val.__class__ is tuple and val == Set.End):
                        self.value[key].add( val )
                        ctr += 1
                        val = apply_parameterized_indexed_rule(self, self.initialize, self._parent(), ctr, tmp)
                        if val is None:
                            raise ValueError("Set rule returned None instead of Set.Skip")
        #
        # Construct using the default values
        #
        else:
            if self.initialize is not None:
                if type(self.initialize) is not dict:
                    for key in self._index:
                        self.value[key] = Set(initialize=self.initialize,within=self.domain,validate=self.validate,ordered=self.ordered,name=self.name+"["+str(key)+"]",dimen=self.dimen)
                        self.value[key]._parent = self._parent
                        self.value[key].construct()
                else:
                    for key in self.initialize:
                        self.value[key] = Set(initialize=self.initialize[key],within=self.domain,validate=self.validate,ordered=self.ordered,name=self.name+"["+str(key)+"]",dimen=self.dimen)
                        self.value[key]._parent = self._parent
                        self.value[key].construct()


register_component(SetOf, "Define a Pyomo Set component using an iterable data object.")
register_component(Set, "Set data that is used to define a model instance.")

