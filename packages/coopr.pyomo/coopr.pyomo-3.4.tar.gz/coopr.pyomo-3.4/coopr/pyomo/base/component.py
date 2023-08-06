#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['Component', 'cname']

import weakref
import sys
from six import iteritems
from coopr.pyomo.base.plugin import register_component


def _cname_index_generator(idx):
    if idx.__class__ is tuple:
        return "[" + ",".join(str(i) for i in idx) + "]"
    else:
        return "[" + str(idx) + "]"


def cname(component, index=None, fully_qualified=False):
    base = component.cname(fully_qualified=fully_qualified)
    if index is None:
        return base
    else:
        if index not in component.index_set():
            raise KeyError( "Index %s is not valid for component %s"
                            % (index, component.cname(True)) )
        return base + _cname_index_generator( index )


class Component(object):
    """
    This is the base class for all Pyomo modeling components.

    Constructor arguments:
        ctype           The class type for the derived subclass
        doc             A text string describing this component
        name            A name for this component

    Public class attributes:
        active          A boolean that is true if this component will be 
                            used to construct a model instance
        doc             A text string describing this component

    Private class attributes:
        _constructed    A boolean that is true if this component has been
                            constructed
        _parent         A weakref to the parent block that owns this component
        _type           The class type for the derived subclass
    """

    def __init__ (self, **kwds):
        #
        # Get arguments
        #
        self.doc   = kwds.pop('doc', None)
        self.name  = kwds.pop('name', str(type(self).__name__)) # "{unnamed}"
        self._type = kwds.pop('ctype', None)
        if kwds:
            raise ValueError(
                "Unexpected keyword options found while constructing '%s':\n\t%s"
                % ( type(self).__name__, ','.join(sorted(kwds.keys())) ))
        #
        # Verify that ctype has been specified.
        #
        if self._type is None:
            raise DeveloperError("Must specify a class for the component type!")
        #
        self.active = True
        self._constructed = False
        self._parent = None    # Must be a weakref

    def __getstate__(self):
        """
        This method must be defined to support pickling because this class
        owns weakrefs for '_parent'.
        """
        # Nominally, __getstate__() should return:
        #
        # state = super(Class, self).__getstate__()
        # for i in Class.__dict__:
        #     state[i] = getattr(self,i)
        # return state
        #
        # Hoewever, in this case, the (nominal) parent class is
        # 'object', and object does not implement __getstate__.  Since
        # super() doesn't actually return a class, we are going to check
        # the *derived class*'s MRO and see if this is the second to
        # last class (the last is always 'object').  If it is, then we
        # can allocate the state dictionary.  If it is not, then we call
        # the super-class's __getstate__ (since that class is NOT
        # 'object').
        if self.__class__.__mro__[-2] is Component:
            state = dict(self.__dict__)
        else:
            state = super(Component,self).__getstate__()
            for key,val in iteritems(self.__dict__):
                if key not in state:
                    state[key] = val
        
        if self._parent is not None:
            state['_parent'] = self._parent()
        return state

    def __setstate__(self, state):
        """
        This method must be defined to support pickling because this class
        owns weakrefs for '_parent'.
        """
        if state['_parent'] is not None and \
                type(state['_parent']) is not weakref.ref:
            state['_parent'] = weakref.ref(state['_parent'])
        # Note: our model for setstate is for derived classes to modify
        # the state dictionary as control passes up the inheritance
        # hierarchy (using super() calls).  All assignment of state ->
        # object attributes is handled at the last class before 'object'
        # (which may -- or may not (thanks to MRO) -- be here.
        if self.__class__.__mro__[-2] is Component:
            for key, val in iteritems(state):
                # Note: per the Python data model docs, we explicitly
                # set the attribute using object.__setattr__() instead
                # of setting self.__dict__[key] = val.
                object.__setattr__(self, key, val)
        else:
            return super(Component,self).__setstate__(state)

    def __str__(self):
        return self.cname()

    def activate(self):
        """Set the active attribute to True"""
        self.active=True

    def deactivate(self):
        """Set the active attribute to False"""
        self.active=False

    def type(self):
        """Return the class type for this component"""
        return self._type

    def construct(self, data=None):                     #pragma:nocover
        """API definition for constructing components"""
        pass

    def is_constructed(self):                           #pragma:nocover
        """Return True if this class has been constructed"""
        return self._constructed

    def valid_model_component(self):
        """Return True if this can be used as a model component."""
        return True

    def pprint(self, ostream=None, verbose=False):
        """Print component information"""
        if ostream is None:
            ostream = sys.stdout
        ostream.write("  %s:"%(self.name))

    def component(self):
        return self

    def parent(self):
        if self._parent is None:
            return None
        else:
            return self._parent()

    def model(self):
        ans = self.parent()
        if ans is None:
            return None
        while ans.parent() is not None:
            ans = ans.parent()
        return ans

    def cname(self, fully_qualified=False, name_buffer=None):
        if fully_qualified and self.parent() != self.model():
            return self.parent().cname(fully_qualified, name_buffer) \
                + "." + self.name
        return self.name

    # a simple utility to return an id->index dictionary for
    # all composite ComponentData instances.
    def id_index_map(self):
        result = dict()
        for index, component_data in iteritems(self):
            result[id(component_data)] = index
        return result

class ComponentData(object):

    __slots__ = ( '_component', )

    def __init__(self, owner):
        if owner is None:
            self._component = None
        else:
            self._component = weakref.ref(owner)

    def __getstate__(self):
        # Nominally, __getstate__() should return:
        #
        # state = super(Class, self).__getstate__()
        # for i in Class.__slots__:
        #    state[i] = getattr(self,i)
        # return state
        #
        # Hoewever, in this case, the (nominal) parent class is
        # 'object', and object does not implement __getstate__.  Since
        # super() doesn't actually return a class, we are going to check
        # the *derived class*'s MRO and see if this is the second to
        # last class (the last is always 'object').  If it is, then we
        # can allocate the state dictionary.  If it is not, then we call
        # the super-class's __getstate__ (since that class is NOT
        # 'object').
        #
        # Further, since there is only a single slot, and that slot
        # (_component) requires special processing, we will just deal
        # with it explicitly.  As _component is a weakref (not
        # pickable), so we need to resolve it to a concrete object.
        if self.__class__.__mro__[-2] is ComponentData:
            state = {}
        else:
            state = super(ComponentData,self).__getstate__()
        
        if self._component is None:
            state['_component'] = None
        else:
            state['_component'] = self._component()
        return state

    def __setstate__(self, state):
        # FIXME: We shouldn't have to check for weakref.ref here, but if
        # we don't the model cloning appears to fail (in the Benders
        # example)
        if state['_component'] is not None and \
                type(state['_component']) is not weakref.ref:
            state['_component'] = weakref.ref(state['_component'])

        # Note: our model for setstate is for derived classes to modify
        # the state dictionary as control passes up the inheritance
        # hierarchy (using super() calls).  All assignment of state ->
        # object attributes is handled at the last class before 'object'
        # (which may -- or may not (thanks to MRO) -- be here.
        if self.__class__.__mro__[-2] is ComponentData:
            for key, val in iteritems(state):
                # Note: per the Python data model docs, we explicitly
                # set the attribute using object.__setattr__() instead
                # of setting self.__dict__[key] = val.
                object.__setattr__(self, key, val)
        else:
            return super(ComponentData,self).__setstate__(state)

    def __str__(self):
        return self.cname()

    def component(self):
        if self._component is None: 
            return None
        return self._component()

    # returns the index of this ComponentData instance relative
    # to the parent component index set. None is returned if 
    # this instance does not have a parent component, or if
    # - for some unknown reason - this instance does not belong
    # to the parent component's index set. not intended to be
    # a fast method - should be used rarely, primarily in 
    # cases of label formulation.
    def index(self):
        self_component = self.component()
        if self_component is None:
            return None
        for idx, component_data in self_component.iteritems():
            if id(component_data) == id(self):
                return idx
        return None
        
    def parent(self):
        ans = self.component()
        if ans is None:
            return None
        # Directly call the Component's model() to prevent infinite
        # recursion for singleton objects.
        if ans is self:
            return super(ComponentData, ans).parent()
        else:
            return ans.parent()

    def cname(self, fully_qualified=False, name_buffer=None):
        c = self.component()
        if c is self:
            return super(ComponentData, self).cname(fully_qualified, name_buffer)

        base = c.cname(fully_qualified, name_buffer)
        if name_buffer is not None:
            if id(self) in name_buffer:
                # should we delete the entry to save mamory?  JDS:
                # probably not, because for nested blocks, we would hit
                # this part of the code numerous times.
                return name_buffer[id(self)]
            for idx, obj in iteritems(c._data):
                name_buffer[id(obj)] = base + _cname_index_generator(idx)
            if id(self) in name_buffer:
                return name_buffer[id(self)]
        else:
            for idx, obj in iteritems(c._data):
                if obj is self:
                    return base + _cname_index_generator(idx)

        raise RuntimeError("Fatal error: cannot find the component data in "
                           "the owning component's _data dictionary.")

    def model(self):
        ans = self.component()
        if ans is None:
            return None
        # Directly call the Component's model() to prevent infinite
        # recursion for singleton objects.
        if ans is self:
            return super(ComponentData, ans).model()
        else:
            return ans.model()


class DeveloperError(Exception):
    """
    Exception class used to throw errors that result from
    programming errors, rather than user modeling errors (e.g., a
    component not declaring a 'ctype').
    """

    def __init__(self, val):
        self.parameter = val

    def __str__(self):                                  #pragma:nocover
        return repr(self.parameter)

