#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['Param']

import sys
import types
import logging
import weakref
import six
from six import iteritems, iterkeys

import pyutilib.math

from coopr.pyomo.base.component import Component, ComponentData, register_component
from coopr.pyomo.base.sparse_indexed_component import SparseIndexedComponent
from coopr.pyomo.base.indexed_component import IndexedComponent
from coopr.pyomo.base.misc import apply_indexed_rule, apply_parameterized_indexed_rule, \
     create_name
from coopr.pyomo.base.numvalue import NumericConstant, NumericValue, native_types, value
from coopr.pyomo.base.set_types import Any, Reals

logger = logging.getLogger('coopr.pyomo')


class _ParamData(ComponentData, NumericValue):
    """Holds the numeric value of a mutable parameter"""

    __slots__ = ('domain', 'value')

    def __init__(self, owner, domain, value):
        """Constructor"""
        ComponentData.__init__(self, owner)
        if domain is None:
            self.domain = Reals
        else:
            self.domain = domain
        if pyutilib.math.is_nan(value):
            self.value = pyutilib.math.nan
        else:
            self.value = value

    def __getstate__(self):
        state = super(_ParamData, self).__getstate__()
        for i in _ParamData.__slots__:
            state[i] = getattr(self, i)
        return state

    # Note: because NONE of the slots on this class need to be edited,
    # we don't need to implement a specialized __setstate__ method, and
    # can quietly rely on the super() class's implementation.
    # def __setstate__(self, state):
    #     pass

    def is_constant(self):
        return False

    def is_fixed(self):
        return True

    def clear(self):
        self.value = None

    def __nonzero__(self):
        """Return True if the value is defined and non-zero."""
        if self.value:
            return True
        if self.value is None:
            raise ValueError("Numeric Constant: value is undefined")
        return False

    __bool__ = __nonzero__

    def __call__(self, exception=True):
        """Return the value of this object."""
        return self.value

    def pprint(self, ostream=None, verbose=False):
        if ostream is None:         #pragma:nocover
            ostream = sys.stdout
        print >>ostream, str(self),


class Param(SparseIndexedComponent):
    """A parameter value, which may be defined over a index"""

    """ Constructor
        Arguments:
           name        The name of this parameter
           index       The index set that defines the distinct parameters.
                         By default, this is None, indicating that there
                         is a single parameter.
           within      A set that defines the type of values that
                         each parameter must be.
           validate    A rule for validating this parameter w.r.t. data
                         that exists in the model
           default     A scalar, rule, or dictionary that defines default 
                         values for this parameter
           initialize  A dictionary or rule for setting up this parameter 
                         with existing model data
           nochecking  If true, various checks regarding valid domain and index
                         values are skipped. Only intended for use by algorithm
                         developers - not modelers!
    """

    DefaultMutable = False

    def __new__(cls, *args, **kwds):
        if cls != Param:
            return super(Param, cls).__new__(cls)
        if args == ():
            return _ParamElement.__new__(_ParamElement)
        else:
            return _ParamArray.__new__(_ParamArray)

    def __init__(self, *args, **kwd):
        self._rule       = kwd.pop('initialize', None )
        self._validate   = kwd.pop('validate', None )
        self.domain      = kwd.pop('within', Any )
        self.nochecking  = kwd.pop('nochecking',False)
        self._mutable    = kwd.pop('mutable', Param.DefaultMutable )

        if 'repn' in kwd:
            logger.warning(
                "DEPRECATED: The use of the 'repn' keyword when constructing "
                "Params has been deprecated and will be removed in Coopr 4.0.")
            kwd.pop('repn')
        if 'rule' in kwd:
            logger.warning(
                "DEPRECATED: The use of the 'rule' keyword when constructing "
                "Params has been deprecated and will be removed in Coopr 4.0."
                "\n\tPlease use 'initialize'")
            if self._rule is not None:
                raise ValueError(
                    "Cannot specify both initialize and rule parameters when "
                    "constructing a Param object")
            self._rule = self._rule = kwd.pop('rule')

        # Use set_default() so that we vaidate the value against the domain
        self._default_val = None
        default = kwd.pop('default', None )
        
        #
        kwd.setdefault('ctype', Param)
        SparseIndexedComponent.__init__(self, *args, **kwd)

        self.set_default(default)

        # Because we want to defer the check for defined values until
        # runtime, we will undo the weakref to ourselves
        if not self.is_indexed():
            del self._data[None]

    def pprint(self, ostream=None, verbose=False):
        if ostream is None:
            ostream = sys.stdout
        ostream.write("   %s : " % (self.name,))
        if self.doc is not None:
            ostream.write(" %s\n   " % (self.doc,))
        ostream.write("\tSize=%s \tDomain=%s\n"
                       % (len(self), self.domain.name) )
        if not self._constructed:
            ostream.write("\tNot constructed\n")
        elif None in self.keys():
            if None in self._data:
                ostream.write("\t%s\n" % ( value(self[None]), ))
            else:
                ostream.write("\tUndefined\n")
        else:
            for key, val in sorted(self.sparse_iteritems()):
                ostream.write("\t%s : %s\n" % (key, value(val)))
        if self._default_val is not None:
            ostream.write("\tdefault: ")
            if type(self._default_val) is types.FunctionType:
                ostream.write("(function)\n")
            else:
                ostream.write("%s\n" % self._default_val)

    def __len__(self):
        if self._default_val is None:
            return len(self._data)
        return len(self._index)

    def __contains__(self, ndx):
        if self._default_val is None:
            return ndx in self._data
        return ndx in self._index

    def __iter__(self):
        if self._default_val is None:
            return self._data.__iter__()
        return self._index.__iter__()

    #
    # NB: These are "sparse equivalent" access / iteration methods that
    # only loop over the defined data.
    #

    def sparse_keys(self):
        return list(iterkeys(self._data))

    def sparse_values(self):
        return [ self[x] for x in self._data ]

    def sparse_items(self):
        return [ (x, self[x]) for x in self._data ]

    def sparse_iterkeys(self):
        return iterkeys(self._data)

    def sparse_itervalues(self):
        for key in self._data:
            yield self[key]

    def sparse_iteritems(self):
        for key in self._data:
            yield (key, self[key])

    # TODO: Not sure what "reset" really means in this context...
    def reset(self):
        pass

    #
    # A utility to extract all index-value pairs defining this
    # parameter, returned as a dictionary. useful in many
    # contexts, in which key iteration and repeated __getitem__
    # calls are too expensive to extract the contents of a parameter.
    # NOTE: We are presently not careful if an index has not been
    #       explicitly defined - issues around defaults are bound
    #       to crop up.
    #
    def extract_values(self):
        # avoid the use of value() for performance reasons - it is painfully slow in this context.
        if self._mutable:
            return dict((key,val.value) for key,val in iteritems(self))
        else:
            return dict((key,value(val)) for key,val in iteritems(self))

    def _default(self, idx):
        # FIXME: Ideally, we should test for using an unconstructed
        # Param; however, actually enforcing this breaks lots & lots of
        # tests...
        #        
        #if not self._constructed:
        #    if idx is None:
        #        idx_str = '%s' % (self.name,)
        #    else:
        #        idx_str = '%s[%s]' % (self.name, idx,)
        #    raise ValueError(
        #        "Error retrieving Param value (%s): The Param value has "
        #        "not been constructed" % ( idx_str,) )                
        #
        # FIXME: Ideally, a key miss should raise a KeyError; however,
        # for mostly historical reasons, Pyomo has raised a ValueError
        # (the logic being that all indices used to be defined at
        # construction, so a key miss was the result of a bad value).
        # Changing this to a KeyError generates numerous test failures, so
        # when someone has time to track down and fix those errors, we
        # SHOULD change the exception to KeyError.
        if self._default_val is None:
            if idx is None:
                idx_str = '%s' % (self.name,)
            else:
                idx_str = '%s[%s]' % (self.name, idx,)
            raise ValueError(
                "Error retrieving Param value (%s): The Param value is "
                "undefined and no default value is specified"
                % ( idx_str,) )

        _default_type = type(self._default_val)
        if _default_type in native_types:
            val = self._default_val
        elif _default_type is types.FunctionType:
            val = apply_indexed_rule(
                self, self._default_val, self.parent(), idx )
        elif hasattr(self, '__getitem__'):
            try:
                val = self._default_val[idx]
            except IndexError:
                val = self._default_val
        else:
            val = self._default_val

        if self._mutable:
            # While slightly less efficient, calling __setitem__ ensures
            # that the parameter validation routine gets called in a
            # consistent manner.
            self[idx] = val
            return self[idx]
            #if self.is_indexed():
            #    return self._data.setdefault(
            #        idx, _ParamData( self, self.domain, val ) )
            #else:
            #    self.value = val
            #    self._data[None] = None
            #    return self
        else:
            return val

    def set_default(self, val):
        if self._constructed and not val is None and not type(val) is types.FunctionType and \
                val not in self.domain:
            raise ValueError(
                "Default value (%s) is not valid for Param domain %s" %
                ( str(val), self.domain.name ) )
        self._default_val = val

    def __setitem__(self, ndx, val):
        if self._constructed and not self._mutable:
            raise TypeError(
"""Attempting to set the value of the immutable parameter %s after the
parameter has been constructed.  If you intend to change the value of
this parameter dynamically, please declare the parameter as mutable
[i.e., Param(mutable=True)]""" % (self.name,))

        # Params should contain *values*.  Normally, I would just call
        # value(), but that forces the value to be a /numeric value/,
        # which for historical reasons, we have not forced.  Notably, we
        # have allowed Params with domain==Any to hold strings, tuples,
        # etc.  The following lets us use NumericValues to initialize
        # Params, but is optimized to check for "known" native types to
        # bypass a potentially expensive isinstance()==False call. 
        #
        if val.__class__ not in native_types:
            if isinstance(val, NumericValue):
                val = val()

        #
        # Validate the index
        #

        if self.nochecking:
            # Ironically, if we are *not* checking index values, then we
            # *must* flatten the incoming index tuple
            ndx = self.normalize_index(ndx)

        #
        # TBD: Potential optimization: if we find that updating a Param is
        # more common than setting it in the first place, then first
        # checking the _data and then falling back on the _index *might*
        # be more efficient.
        #
        elif ndx not in self._index:

            # We rely (for performance purposes) on "most" people doing things 
            # correctly; that is, they send us either a scalar or a valid tuple.  
            # So, for efficiency, we will check the index *first*, and only go
            # through the hassle of flattening things if the ndx is not found.
            ndx = self.normalize_index(ndx)
            if ndx not in self._index:
                if not self.is_indexed():
                    msg = "Error setting parameter value: " \
                          "Cannot treat the scalar Param '%s' as an array" \
                          % ( self.name, )
                else:
                    msg = "Error setting parameter value: " \
                          "Index '%s' is not valid for array Param '%s'" \
                          % ( ndx, self.name, )
                raise KeyError(msg)

        if ndx is None:
            self.value = val
            self._data[ndx] = None
        elif self._mutable:
            if ndx in self._data:
                self._data[ndx].value = val
            else:
                self._data[ndx] = _ParamData(self, self.domain, val)
        else:
            self._data[ndx] = val
        #
        # This is at the end, so the user can write their validation
        # tests as if the data was already added.
        #
        if self.nochecking:
            return
        if val not in self.domain:
            raise ValueError(
                "Invalid parameter value: %s[%s] = '%s', value type=%s.\n"
                "\tValue not in parameter domain %s" %
                ( self.name, ndx, val, type(val), self.domain.name ) )
        if self._validate is not None:
            if self.is_indexed():
                if type(ndx) is tuple:
                    tmp = ndx
                else:
                    tmp = (ndx,)
            else:
                tmp = ()
            if not apply_parameterized_indexed_rule(
                self, self._validate, self.parent(), val, tmp ):
                raise ValueError(
                    "Invalid parameter value: %s[%s] = '%s', value type=%s.\n"
                    "\tValue failed parameter validation rule" %
                    ( self.name, ndx, val, type(val) ) )

    def construct(self, data=None):
        """ Apply the rule to construct values in this set """

        if __debug__:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Constructing Param, name=%s, from data=%s"
                             % ( self.name, str(data) ))

        if self._constructed:
            raise IOError(
                "Cannot reconstruct parameter '%s' (already constructed)"
                % self.name )
            return

        self.clear()

        #
        # Construct using the initial data or the data loaded from an
        # external source. Data values will be queried in to following
        # order:
        #   1) the 'data' dictionary
        #   2) the self._rule dictionary or rule
        #   3) [implicit: fall back on the default value]
        #
        # To accomplish this, we will first set all the values based on
        # self._rule, and then allow the data dictionary to
        # overwrite anything.
        #
        # NB: Singleton Params can always be treated as "normal" indexed
        # params, indexed by a set {None}.
        #

        #
        # NB: Previously, we would raise an exception for constructing
        # scalar parameters with no defined data.  As that was a special
        # case (i.e. didn't apply to arrays) and was frustrating for
        # Concrete folks who were going to initialize the value later,
        # we will allow an undefined Param to be constructed and will
        # instead throw an exception later if the user tries to *use* the
        # Param before it is initialized.
        #
        _init = self._rule
        if _init is not None:
            _init_type = type(_init)
            if _init_type is dict:
                for key, val in iteritems(_init):
                    self[key] = val
            elif _init_type is types.FunctionType:
                if self.is_indexed():
                    # a situation can arise in which the parameter is indexed by
                    # an empty set, or an empty set tuple. rare, but it has happened.
                    if len(self._index) != 0: 
                        _iter = self._index.__iter__()
                        idx = six.next(_iter)
                        val = apply_indexed_rule(self, _init, self.parent(), idx)
                        if type(val) is dict:
                            for key, v in iteritems(val):
                                self[key] = v
                        else:
                            # IMPORTANT: Do *not* call self.__setitem__ here
                            #    - we already know the index is valid (and
                            #    flattened), and validating indices is far too
                            #    expensive to waste time doing it
                            #    again. however, we still need to validate the
                            #    value generated by the rule, relative to the
                            #    parameter domain.
                            # REVISION: given the rewrite of __setitem__,
                            #    the index is not validated unless it is not
                            #    found in the corresponding data / index.  We
                            #    *could* reimplement the optimization metioned
                            #    above if it proves necessary, but until then,
                            #    the DRY principle dictates that we use
                            #    __setitem__.
                            self[idx] = val
                            for idx in _iter:
                                self[idx] = apply_indexed_rule(
                                    self, _init, self.parent(), idx )
                else:
                    self[None] = _init(self.parent())
            else:
                if isinstance(_init, NumericValue):
                    # Reduce NumericValues to scalars
                    _init = _init()
                elif isinstance(_init, SparseIndexedComponent):
                    # Ideally, we want to reduce SparseIndexedComponents
                    # to a dict, but without "densifying" it.  However,
                    # since there is no way to (easily) get the default
                    # value, we will take the "less surprising" route of
                    # letting the source become dense, so that we get
                    # the expected copy.
                    sparse_src = len(_init) != len(_init.keys())
                    tmp = {}
                    for key in _init.keys():
                        try:
                            val = _init[key]
                        except ValueError:
                            continue
                        tmp[key] = value(val)
                    tmp = dict(iteritems(_init))
                    if sparse_src and len(_init) == len(_init.keys()):
                        logger.warning("""
Initializing Param %s using a sparse mutable indexed component (%s).
    This has resulted in the conversion of the source to dense form.
""" % ( self.name, _init.name ) )
                    _init = tmp
                elif isinstance(_init, IndexedComponent):
                    # FIXME: is there a general form for
                    # IndexedComponent, or should we just wait until
                    # everything moves over to SparseIndexedComponents?
                    pass
                # if things looks like a dictionary, then we will treat
                # it as such
                _isDict = hasattr(_init, '__getitem__')
                if _isDict:
                    try:
                        for x in _init:
                            _init.__getitem__(x)
                    except:
                        _isDict = False
                if _isDict:
                    for key in _init:
                        self[key] = _init[key]
                else:
                    for key in self._index:
                        self[key] = _init
                
        if data is not None:
            try:
                for key, val in iteritems(data):
                    self[key] = val
            except Exception:
                msg = sys.exc_info()[1]
                if type(data) not in [dict]:
                   raise ValueError("Attempting to initialize parameter="+self.name+" with data="+str(data)+". Data type is not a dictionary, and a dictionary is expected. Did you create a dictionary with a \"None\" index?")
                else:
                    raise RuntimeError("Failed to set value for param="+str(self.name)+", index="+str(key)+", value="+str(val)+"; source error message="+str(msg))

        self._constructed = True
        self.set_default(self._default_val)


class _ParamElement(_ParamData, Param):

    def __init__(self, *args, **kwds):
        Param.__init__(self, *args, **kwds)
        _ParamData.__init__(self, self, self.domain, kwds.get('default',None))

    # Since this class derives from Component and Component.__getstate__
    # just packs up the entire __dict__ into the state dict, there s
    # nothng special that we need to do here.  We will just defer to the
    # super() get/set state.  Since all of our get/set state methods
    # rely on super() to traverse the MRO, this will automatically pick
    # up both the Component and Data base classes.
    #
    #def __getstate__(self):
    #    pass
    #
    #def __setstate__(self, state):
    #    pass

    def pprint(self, ostream=None, verbose=False):
        # Needed so that users find Param.pprint and not _ParamData.pprint
        Param.pprint(self, ostream=ostream, verbose=verbose)

    def __call__(self, *args, **kwds):
        # Needed because we rely on self[None] to know if this parameter
        # is valid.  In particular, if we are getting data from the
        # default value, calling self[None] will actually inject the
        # [None] entry into _data.
        ans = self[None]
        if None in self._data:
            return _ParamData.__call__(ans, *args, **kwds)
        else:
            return ans

    def set_value(self, value):
        if self._constructed and not self._mutable:
            raise TypeError(
"""Attempting to set the value of the immutable parameter %s after the
parameter has been constructed.  If you intend to change the value of
this parameter dynamically, please declare the parameter as mutable
[i.e., Param(mutable=True)]""" % (self.name,))
        self[None] = value
        
    def is_constant(self):
        return self._constructed and not self._mutable


class _ParamArray(Param):

    def __init__(self, *args, **kwds):
        Param.__init__(self, *args, **kwds)

    def display(self, ostream=None):
        self.pprint(ostream=ostream)


register_component(Param, "Parameter data that is used to define a model instance.")

