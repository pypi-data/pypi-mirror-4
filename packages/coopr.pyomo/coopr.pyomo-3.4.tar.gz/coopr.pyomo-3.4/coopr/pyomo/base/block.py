#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

"""
Block Properties:

1. Blocks are indexed components that contain other components
   (including blocks)

2. Blocks have a global attribute that defines whether construction is
   deferred.  This applies to all components that they contain except
   blocks.  Blocks contained by other blocks use their local attribute
   to determine whether construction is deferred.

NOTE: Blocks do not currently maintain statistics about the sets,
parameters, constraints, etc that they contain, including these
components from subblocks.
"""

__all__ = ['Block', 'active_subcomponents_generator', 'active_subcomponents_data_generator']

import sys
import weakref
import logging
from operator import itemgetter
from six import iterkeys, iteritems, itervalues, StringIO

from pyutilib.component.core import alias, ExtensionPoint
from pyutilib.misc import Container

from coopr.pyomo.base.plugin import *
from coopr.pyomo.base.component import Component, ComponentData
from coopr.pyomo.base.sets import Set, _SetContainer
from coopr.pyomo.base.rangeset import RangeSet
from coopr.pyomo.base.var import Var
from coopr.pyomo.base.constraint import Objective, Constraint
from coopr.pyomo.base.param import Param
from coopr.pyomo.base.misc import apply_indexed_rule
from coopr.pyomo.base.set_types import IntegerSet, BooleanSet
from coopr.pyomo.base.sparse_indexed_component import SparseIndexedComponent

logger = logging.getLogger('coopr.pyomo')

#
# We now include a number of generators for iterating over various
# components within a block.  the primary purpose is to streamline code,
# as this kind of iteration is done *everywhere* in Coopr. any generally
# useful iteration schemes should be moved into the following segment.
# 

# iterates over all active components (e.g., Var) of the specified type
# in the input block.  sorting, if specified, is by component name.
def active_subcomponents_generator(block, component_type, deterministic=False):
    compList = iteritems( block.active_subcomponents(component_type) )
    for name, component in compList:
        if component.active:
            yield component

# iterates over all active sub_components (e.g., _VarData) of all active
# components of the specified type in the input block.  If deterministic
# is set to True, the objects will be returned in a deterministic order
# (components in declaration order and within each component sorted by index)
def active_subcomponents_data_generator(block, component_type, deterministic=False):
    active_components = \
        active_subcomponents_generator( block, component_type, deterministic )
    for component in active_components:
        subCompList = iteritems(component._data)
        if deterministic:
            subCompList = sorted(subCompList, key=itemgetter(0))
        for name, componentData in subCompList:
            if componentData.active:
                yield componentData

# 
#
#

class _BlockConstruction(object):
    """
    This class holds a "global" dict used when constructing
    (hierarchical) models.
    """
    data = {}


class _BlockData(ComponentData):
    """
    This class holds the fundamental block data.
    """

    class PseudoMap(object):
        """
        This class presents a "mock" dict interface to the internal
        BlockComponents data structures.  We return this object to the
        user to preserve the historical "{ctype : {name : obj}}"
        interface without actually regenerating that dict-of-dicts data
        structure.
        """

        __slots__ = ( '_block', '_ctype', '_active' )
        
        def __init__(self, block, ctype, active=None):
            self._block = block
            self._ctype = ctype
            self._active = active

        def __iter__(self):
            return self.iterkeys()

        def __getitem__(self, key):
            if key in self._block._decl:
                x = self._block._decl_order[self._block._decl[key]]
                if self._ctype is None or x[0].type() is self._ctype:
                    if self._active is None or x[0].active == self._active:
                        return x[0]
            msg = ""
            if self._active is not None:
                msg += self._active and "active " or "inactive "
            if self._ctype is not None:
                msg += self._ctype.__name__ + " "
            raise KeyError( "%scomponent %s not found in block %s" 
                            % (msg, key, self._block.cname()))

        def __nonzero__(self):
            # Shortcut: this will bail after finding the first item
            for x in itervalues(self):
                return True
            return False

        __bool__ = __nonzero__

        def __len__(self):
            if self._active is None:
                if self._ctype is None:
                    return sum(x[2] for x in itervalues(self._block._ctypes))
                else:
                    return self._block._ctypes.get(self._ctype,(0,0,0))[2]
            #For active==True/False, we have to count by brute force
            ans = 0
            for x in itervalues(self):
                ans += 1
            return ans

        def __contains__(self, key):
            if key in self._block._decl:
                x = self._block._decl_order[self._block._decl[key]]
                if x[0].type() is self._ctype:
                    if self._active is None or x[0].active == self._active:
                        return True
            return False

        def iterkeys(self):
            if self._ctype is None:
                idx = 0
            else:
                idx = self._block._ctypes.get(self._ctype, [None])[0]
            while idx is not None:
                try:
                    x = self._block._decl_order[idx]
                except IndexError:
                    break

                if x[0] is not None:
                    if self._active is None or x[0].active == self._active:
                        yield x[0].name
                if self._ctype is None:
                    idx += 1
                else:
                    idx = x[1]

        def itervalues(self):
            if self._ctype is None:
                idx = 0
            else:
                idx = self._block._ctypes.get(self._ctype, [None])[0]
            while idx is not None:
                try:
                    x = self._block._decl_order[idx]
                except IndexError:
                    break

                if x[0] is not None:
                    if self._active is None or x[0].active == self._active:
                        yield x[0]
                if self._ctype is None:
                    idx += 1
                else:
                    idx = x[1]

        def iteritems(self):
            if self._ctype is None:
                idx = 0
            else:
                idx = self._block._ctypes.get(self._ctype, [None])[0]
            while idx is not None:
                try:
                    x = self._block._decl_order[idx]
                except IndexError:
                    break

                if x[0] is not None:
                    if self._active is None or x[0].active == self._active:
                        yield (x[0].name, x[0])
                if self._ctype is None:
                    idx += 1
                else:
                    idx = x[1]

        def keys(self):
            return list(self.iterkeys())

        def values(self):
            return list(self.itervalues())

        def items(self):
            return list(self.iteritems())

    def __init__(self, owner):
        #
        # We used to define an internal structure that looked like:
        #
        #    _component    = { ctype : OrderedDict( name : obj ) }
        #    _declarations = OrderedDict( name : obj )
        #
        # This structure is convenient, but the overhead of carrying
        # around roughly 20 dictionaries for every block consumed a
        # nontrivial amount of memory.  Plus, the generation and
        # maintenance of OrderedDicts appeared to be disturbingly slow.
        #
        # We now "mock up" this data structure using 2 dicts and a list:
        #
        #    _ctypes     = { ctype : [ first idx, last idx, count ] }
        #    _decl       = { name  : idx }
        #    _decl_order = [ (obj, next_ctype_idx) ]
        #
        # Some notes: As Pyomo models rarely *delete* objects, we
        # currently never remove items from the _decl_order list.  If
        # the component is ever removed / cleared, we simply mark the
        # object as None.  If models crop up where we start seeing a
        # significant amount of adding / removing components, then we
        # can revisit this decision (although we will probably continue
        # marking entries as None and just periodically rebuild the list
        # as opposed to maintining the list without any holes.
        #
        ComponentData.__init__(self, owner)
        # Note: call super() here to bypass the Block __setattr__
        #   _ctypes:      { ctype -> [1st idx, last idx, count] }
        #   _decl:        { name -> idx }
        #   _decl_order:  list( tuples( obj, next_type_idx ) )
        super(_BlockData, self).__setattr__('_ctypes', {})
        super(_BlockData, self).__setattr__('_decl', {})
        super(_BlockData, self).__setattr__('_decl_order', [])


    def __getstate__(self):
        # Note: _BlockData is NOT slot-ized, so we must pickle the
        # entire __dict__.  However, we want the base class's
        # __getstate__ to override our blanket approach here (i.e., it
        # will handle the _component weakref).
        ans =  dict(self.__dict__)
        ans.update(ComponentData.__getstate__(self))
        return ans

    def __setstate__(self, state):
        # We want the base class's __setstate__ to override our blanket
        # approach here (i.e., it will handle the _component weakref).
        for (slot_name, value) in iteritems(state):
            super(_BlockData, self).__setattr__(slot_name, value)
        ComponentData.__setstate__(self, state)


    #def __getitem__(self, name):
    #    # This supports two key functionalities:
    #    #  1. block["component_name"] as a convenient alternative to
    #    #     block.component_name
    #    #  2. block[Var] as an alternative to block.subcomponents(Var)
    #
    #    if name in self._decl:
    #        return self._decl_order[self._decl[name]][0]
    #    elif name in self._ctypes:
    #        return BlockComponents.PseudoMap(self, name)
    #    elif isinstance(name,basestring):
    #        return None
    #    else:
    #        return {}

    def __setattr__(self, name, val):
        #
        # Set an attribute on this Block.  In general, the most common
        # case for this is setting a *new* attribute.  After that, there
        # is updating an existing Component value, with the least common
        # case being resetting an existing general attribute.  Given
        # that, we will:
        #
        # 1) handle new attributes, with special handling of Components
        if name not in self.__dict__:
            if isinstance(val, Component):
                self.add_component(name, val)
            else:
                super(_BlockData, self).__setattr__(name, val)
                #self.__dict__[name] = val
        # 2) Update the value of existing [singleton] Components
        # (through the component's set_value())
        elif name in self._decl:
            # JDS: setting a component to None should attempt
            #if val is None:
            #    self.del_component(name)
            if isinstance(val, Component):
                logger.warn(
                    "Attempting to implictly replace the Component attribute "
                    "%s (type=%s) on block %s with a new Component (type=%s)."
                    "\nThis is usually indicative of a modelling error.\n"
                    "To avoid this warning, use block.del_component() and "
                    "block.add_component()."
                    % ( name, type(self.subcomponent(name)), self.cname(True), 
                        type(val) ) )
                self.del_component(name)
                self.add_component(name, val)
            else:
                try:
                   self.subcomponent(name).set_value(val)
                except AttributeError:
                    logger.error(
                        "Expected component %s (type=%s) on block %s to have a "
                        "'set_value' method, but none was found." % 
                        ( name, type(self.subcomponent(name)), 
                          self.cname(True) ) )
                    raise
        # 3) handle setting non-Component attributes
        else:
            # NB: This is important: the _BlockData is either a
            # singleton Block (where _parent and _component are defined)
            # or a single block within an Indexed Block (where only
            # _component is defined).  Regardless, the __init__()
            # declares these attributes and sets them to either None or
            # a weakref.  This means that we will never have a problem
            # converting these objects from weakrefs into Blocks and
            # back (when pickling): because the attribute is already
            # in __dict__, we will not hit the add_component /
            # del_component branches above.  It also means that any
            # error checking we want to do when assigning these
            # attributes should be done here.

            # NB: isintance() can be slow; however, it is only slow when
            # it returns False.  Since the common paths on this branch
            # should return True, this shouldn't be too inefficient.
            if name == '_parent':
                if val is not None and not isinstance(val(), _BlockData):
                    raise ValueError(
                        "Cannot set the '_parent' attribute of Block '%s' "
                        "to a non-Block object (with type=%s); Did you "
                        "try to create a model component named '_parent'?" 
                        % (self.cname(), type(val)) )
                super(_BlockData, self).__setattr__(name, val)
                #self.__dict__[name] = val
            elif name == '_component':
                if val is not None and not isinstance(val(), _BlockData):
                    raise ValueError(
                        "Cannot set the '_component' attribute of Block '%s' "
                        "to a non-Block object (with type=%s); Did you "
                        "try to create a model component named '_component'?" 
                        % (self.cname(), type(val)) )
                super(_BlockData, self).__setattr__(name, val)
                #self.__dict__[name] = val
            # At this point, we should only be seeing non-component data
            # the user is hanging on the blocks (uncommon) or the
            # initial setup of the object data (in __init__).
            elif isinstance(val, Component):
                logger.warn(
                    "Attempting to reassign the non-component attribute %s "
                    "on block %s with a new Component with type %s.  This is "
                    "usually indicative of a modelling error."
                    % (name, self.cname(True), type(val)) )
                self.del_component(name)
                self.add_component(name, val)
            else:
                super(_BlockData, self).__setattr__(name, val)
                #self.__dict__[name] = val

 
    def __delattr__(self, name):
        # We need to make sure that del_component() gets called if a
        # user attempts to remove an attribute from a block that happens
        # to be a component
        if name in self._decl:
            self.del_component(name)
        else:
            super(_BlockData, self).__delattr__(name)


    def _add_temporary_set(self,val):
        """ TODO """
        # NB: only "old" IndexedComponent contain _index_set.
        #    SparseIndexedComponent has _implicit_subsets
        # FIXME: We need to make IndexedComponent look more like
        #    SparseIndexedComponent (or make it go away entirely)
        _component_sets = getattr(val, '_index_set', None)
        if _component_sets is None:
            _construct_index_set = False
            _component_sets = getattr(val, '_implicit_subsets', None)
        else:
            _construct_index_set = True

        # FIXME: The name attribute should begin with "_", and None
        # should replace "_unknown_"
        if _component_sets is not None:
            ctr=0
            for tset in _component_sets:
                if tset.cname() == "_unknown_":
                    self._construct_temporary_set(
                      tset,
                      val.cname()+"_index_"+str(ctr)
                    )
                ctr += 1
            if _construct_index_set:
                val._index = self._construct_temporary_set(
                    _component_sets,
                    val.cname()+"_index" )
        if isinstance(val._index,_SetContainer) and val._index.name == "_unknown_":
            self._construct_temporary_set(val._index,val.cname()+"_index")
        if getattr(val,'domain',None) is not None and val.domain.name == "_unknown_":
            self._construct_temporary_set(val.domain,val.cname()+"_domain")

    def _construct_temporary_set(self, obj, name):
        """ TODO """
        if type(obj) is tuple:
            if len(obj) == 1:                #pragma:nocover
                raise Exception(
                    "Unexpected temporary set construction for set "
                    "%s on block %s" % ( name, self.cname()) )
            else:
                tobj = obj[0]
                for t in obj[1:]:
                    tobj = tobj*t
                setattr(self,name,tobj)
                tobj.virtual=True
                return tobj
        if isinstance(obj,Set):
            setattr(self,name,obj)
            return obj


    def add_component(self, name, val):
        if not val.valid_model_component():
            raise RuntimeError(
                "Cannot add '%s' as a component to a model" % str(type(val)) )
        if name in self.__dict__:
            raise RuntimeError(
                "Cannot add component '%s' (type %s) to block '%s': a "
                "component by that name (type %s) is already defined."
                % (name, type(val), self.cname(), type(getattr(self, name))))

        # all Pyomo components have names. 
        val.name = name
        # all Pyomo components have Parents
        if val._parent is not None:
            logger.warn("Reassigning component %s to block %s"
                        % (val.cname(True), self.cname(True)) )
            val.parent().del_component(name)
        val._parent = weakref.ref(self)

        # We want to add the temporary / implicit sets first so that
        # they get constructed before this component
        self._add_temporary_set(val)

        # Add the component to the underlying Component store
        _new_idx = len(self._decl_order)
        self._decl[name] = _new_idx
        self._decl_order.append( (val, None) )

        # Add the component as an attribute
        super(_BlockData, self).__setattr__(name, val)
        #self.__dict__[name]=val

        # Update the ctype linked lists
        _type = val.type()
        if _type in self._ctypes:
            idx_info = self._ctypes[_type]
            tmp = idx_info[1]
            self._decl_order[tmp] = (self._decl_order[tmp][0], _new_idx)
            idx_info[1] = _new_idx
            idx_info[2] += 1
        else:
            self._ctypes[_type] = [_new_idx, _new_idx, 1]

        # Support implicit rule names
        if '_rule' in val.__dict__:
            if val._rule is None:
                frame = sys._getframe(2)
                locals_ = frame.f_locals
                if val.cname()+'_rule' in locals_:
                    val._rule = locals_[val.cname()+'_rule']
        # FIXME: This is a HACK to support the way old Blocks and legacy
        # IndexedComponents (like Set) behave.  In particular, Set does
        # not define a "rule" attribute.  I put the hack back in to get
        # some tests passing again, but in all honesty, I am amazed this
        # ever worked properly. [JDS]
        elif getattr(val, 'rule', None) is None:
            frame = sys._getframe(2)
            locals_ = frame.f_locals
            if val.cname()+'_rule' in locals_:
                val.rule = locals_[val.cname()+'_rule']

        # If the block is Concrete, construct the component
        if self.component()._constructed:
            # NB: we don't have to construct the temporary / implicit
            # sets here: if necessary, that happens when
            # _add_temporary_set() calls add_component().
            if id(self) in _BlockConstruction.data:
                data = _BlockConstruction.data[id(self)].get(name,None)
            else:
                data = None
            # This is tricky: If we are in the middle of constructing an
            # indexed block, the block component already has
            # _constructed=True.  Now, if the _BlockData.__init__()
            # defines any local variables (like coopr.gdp.Disjunct's
            # indicator_var), cname(True) will fail: this block data
            # exists and has a parent(), but it has not yet been added
            # to the parent's _data (so the idx lookup will fail in cname()).
            if __debug__ and logger.isEnabledFor(logging.DEBUG):
                if self.parent() is None:
                    _blockName = "[Model]"
                else:
                    try:
                        _blockName = "Block '%s'" % self.cname(True)
                    except:
                        _blockName = "Block '%s[...]'" \
                            % self.component().cname(True)
                logger.debug( "Constructing %s '%s' on %s from data=%s",
                              val.__class__.__name__, val.cname(), 
                              _blockName, str(data) )
            try:
                val.construct(data)
            except:
                err = sys.exc_info()[1]
                logger.error(
                    "Constructing component '%s' from data=%s failed:\n%s: %s",
                    str(val.cname(True)), str(data).strip(),
                    type(err).__name__, err )
                raise
            if __debug__ and logger.isEnabledFor(logging.DEBUG):
                if _blockName[-1] == "'":
                    _blockName = _blockName[:-1] + '.' + val.cname() + "'"
                else:
                    _blockName = "'" + _blockName + '.' + val.cname() + "'"
                _out = StringIO()
                val.pprint(ostream=_out)
                logger.debug( "Constructed component '%s':\n%s" 
                              % ( _blockName, _out.getvalue() ) )


    def del_component(self, name):
        # FIXME: Is this necessary?  Should this raise an exception?
        if name not in self._decl:
            return

        # Remove the attribute
        del self.__dict__[name]

        # Replace the component in the master list
        idx = self._decl[name]
        del self._decl[name]
        obj = self._decl_order[idx][0]
        self._decl_order[idx] = (None, self._decl_order[idx][1])

        # Update the ctype linked lists
        ctype_info = self._ctypes[obj.type()]
        ctype_info[2] -= 1
        if ctype_info[2] == 0:
            del self._ctypes[obj.type()]

        # Clear the _parent attribute
        obj._parent = None

    def reclassify_subcomponent_type(self, name_or_object, new_ctype):
        try:
            c = name_or_object.component()
        except AttributeError:
            c = self.subcomponent(name_or_object)
        if c._type is not new_ctype:
            self.del_component(c.cname())
            c._type = new_ctype
            self.add_component(c.cname(), c)


    #def keys(self):
    #    return list(self.iterkeys())

    #def __iter__(self):
    #    for x in self._decl_order:
    #        if x[0] is not None:
    #            yield x[0].cname()

    #def iterkeys(self):
    #    for x in self._decl_order:
    #        if x[0] is not None:
    #            yield x[0].cname()

    #def itervalues(self):
    #    for x in self._decl_order:
    #        if x[0] is not None:
    #            yield x[0]

    #def iteritems(self):
    #    for x in self._decl_order:
    #        if x[0] is not None:
    #            yield (x[0].cname(), x[0])

    def contains_component(self, ctype):
        return ctype in self._ctypes and self._ctypes[ctype][2]

    def subcomponent_map(self, ctype=None, active=None):
        """
        Return information about the block components.  If ctype is
        None, return the dictionary that maps
           {component type -> {name -> instance}}
        Otherwise, return the dictionary that maps
           {name -> instance}
        for the specified component type.

        Note: the actual {name->instance} object is a PseudoMap that
        implements a lightweight interface to the underlying
        BlockComponents data structures.
        """

        if ctype is None:
            ans = {}
            for x in self._ctypes:
                ans[x] = _BlockData.PseudoMap(self, x, active)
            return ans
        else:
            return _BlockData.PseudoMap(self, ctype, active)

    def components(self, ctype=None, active=None):
        #logger.warn("DEPRECATION WARNING: Block.components() has been "
        #            "renamed Block.subcomponents().")
        return self.subcomponents(ctype, active)

    def active_components(self, ctype=None):
        #logger.warn("DEPRECATION WARNING: Block.active_components() has been "
        #            "renamed Block.active_subcomponents().")
        return self.active_subcomponents(ctype)

    def subcomponent(self, name):
        if name in self._decl:
            return self._decl_order[self._decl[name]][0]
        else:
            return None

    def subcomponents(self, ctype=None, active=None):
        return _BlockData.PseudoMap(self, ctype, active)
            
    def active_subcomponents(self, ctype=None):
        """
        Returns the active components in this block.  Return values
        match those of .subcomponents().
        """
        return self.subcomponents(ctype, True)

    def fix_all_vars(self):
        for var in itervalues(self.subcomponents(Var)):
            var.fix_all()
        for block in itervalues(self.subcomponents(Block)):
            block.fix_all_vars()

    def unfix_all_vars(self):
        for var in itervalues(self.subcomponents(Var)):
            var.unfix_all()
        for block in itervalues(self.subcomponents(Block)):
            block.unfix_all_vars()

    def is_constructed(self):
        """
        A boolean indicating whether or not all *active* components of the
        input model have been properly constructed.
        """
        if not self._constructed:
            return False
        for x in self._decl_order:
            if x[0] is not None and x[0].active and not x[0].is_constructed():
                return False
        return True

    def pprint(self, filename=None, ostream=None, verbose=False):
        """
        Print a summary of the model info
        """
        if ostream is None:
            ostream = sys.stdout
        if filename is not None:
            OUTPUT=open(filename,"w")
            self.pprint(ostream=OUTPUT, verbose=verbose)
            OUTPUT.close()
            return
        if ostream is None:
            ostream = sys.stdout
        #
        # We hard-code the order of the core Pyomo modeling
        # components, to ensure that the output follows the logical order
        # that expected by a user.
        #
        items = [Set, RangeSet, Param, Var, Objective, Constraint, Block]
        for item in ExtensionPoint(IModelComponent):
            if not item in items:
                items.append(item)

        # Currently, model components are not actually being registered
        # with the IModelComponent extension point (1 Nov 2010), so as a
        # workaround, we will loop through the components and add any
        # new components that actually have defined members.
        extra_items = []
        for ctype, info in iteritems(self._ctypes):
            if ctype not in items and info[2]:
                extra_items.append(ctype)
        # extra items get added alphabetically (so output is consistent)
        if sys.version_info < (3,0):
            items.extend(sorted(extra_items, key=lambda x: x.__name__))
        else:
            items.extend(sorted(extra_items, key=lambda x: x.__name__))

        for item in items:
            keys = list(iterkeys(self.subcomponents(item)))
            keys.sort()

            #
            # NOTE: these conditional checks should not be hard-coded.
            #
            ostream.write(str(len(keys))+' '+item.__name__+" Declarations\n")
            for key in keys:
                self.subcomponent(key).pprint(ostream=ostream, verbose=verbose)
            ostream.write("\n")
        #
        # Model Order
        #
        decl_order_keys = list(iterkeys(self.subcomponents()))
        ostream.write(str(len(decl_order_keys))+" Declarations:")
        for x in decl_order_keys:
            ostream.write(' '+str(x))
        ostream.write("\n")


class Block(SparseIndexedComponent):
    """
    A block in an optimization model.  By default, this defers construction of
    components until data is loaded.
    """

    def __new__(cls, *args, **kwds):
        if cls != Block:
            return super(Block, cls).__new__(cls)
        if args == ():
            return SingletonBlock.__new__(SingletonBlock)
        else:
            return IndexedBlock.__new__(IndexedBlock)


    def __init__(self, *args, **kwargs):
        """Constructor"""
        self._rule = kwargs.pop('rule', None )
        self._options = kwargs.pop('options', None )
        kwargs.setdefault('ctype', Block)
        SparseIndexedComponent.__init__(self, *args, **kwargs)

    def _default(self, idx):
        return self._data.setdefault(idx, _BlockData(self))

    def concrete_mode(self):
        """Configure block to immediately construct components"""
        self.construct()

    def symbolic_mode(self):
        """Configure block to defer construction of components"""
        if self._constructed:
            logger.error(
                "Attempting to return a Concrete model to Symbolic (Abstract) "
                "mode: you will likely experience unexpected and potentially "
                "erroneous behavior.")
        self._constructed=False

    def all_blocks(self, active=None, sort_by_keys=False):
        if active is not None and self.active != active:
            return
        blocks = iteritems(self)
        if sort_by_keys:
            blocks = sorted(blocks, key=itemgetter(0))

        for idx, b in blocks:
            yield b
            for subblock in itervalues(b.subcomponents(Block, active)):
                for tmp in subblock.all_blocks(active, sort_by_keys):
                    yield tmp

    # flags *all* active variables and their composite _VarData objects
    # as stale.  fixed variables are flagged as non-stale. the state of
    # all inactive variables is left unchanged.
    def flag_vars_as_stale(self):
        for block in self.all_blocks():
            for variable in active_subcomponents_generator(block,Var):
                variable.flag_as_stale()


    def find_component(self, label):
        """ TODO """
        cList = label.split('.')
        obj = self
        while cList:
            c = cList.pop(0).split(':')
            if len(c) > 1:
                idx = c[1].split(',')
                for i, val in enumerate(idx):
                    if val[0]=='#':
                        idx[i] = int(val[1:])
                    elif val[0]=='$':
                        idx[i] = val[1:]
                    elif val[0]=='!':
                        idx[i] = None
                    else:
                        # last-ditch effort to find things
                        try:
                            tmp = int(val)
                            idx[i] = tmp
                        except ValueError:
                            pass
                        #raise ValueError(
                        #    "missing index type specifier for index %s in canonical label %s" % (val,label) )
                if len(idx) > 1:
                    idx = tuple(idx)
                else:
                    idx = idx[0]
            else:
                idx = None
            try:
                if idx is None:
                    obj = getattr(obj, c[0])
                else:
                    obj = getattr(obj, c[0])[idx]
            except AttributeError:
                return None
        return obj


    def construct(self, data=None):
        """ TODO """
        if __debug__ and logger.isEnabledFor(logging.DEBUG):
            logger.debug( "Constructing %s '%s', from data=%s",
                          self.__class__.__name__, self.cname(), str(data) )
        if self._constructed:
            return
        self._constructed = True

        # We must check that any pre-existing components are
        # constructed.  This catches the case where someone is building
        # a Concrete model by building (potentially pseudo-abstract)
        # sub-blocks and then adding them to a Concrete model block.
        for idx in self._data:
            _block = self[idx]
            for name, obj in iteritems( _block.subcomponents() ):
                if not obj._constructed:
                    if data is None:
                        _data = None
                    else:
                        _data = data.get(name, None)
                    obj.construct(_data)
        
        if self._rule is None:
            return
        # If we have a rule, fire the rule for all indices.  
        # Notes:
        #  - Since this block is now concrete, any components added to
        #    it will be immediately constructed by
        #    block.add_component().
        #  - Since the rule does not pass any "data" on, we build a
        #    singleton "stack" of pointers to block data
        #    (_BlockConstruction.data) that the individual blocks'
        #    add_component() can refer back to to handle subcomponent
        #    construction.
        for idx in self._index:
            _block = self[idx]
            if data is not None and idx in data:
                _BlockConstruction.data[id(_block)] = data[idx]
            obj = apply_indexed_rule(
                None, self._rule, _block, idx, self._options )
            if id(_block) in _BlockConstruction.data:
                del _BlockConstruction.data[id(_block)]

            # TBD: Should we allow skipping Blocks???
            #if obj is Block.Skip and idx is not None:
            #   del self._data[idx]

    def display(self, filename=None, ostream=None):
        """
        Print the Pyomo model in a verbose format.
        """
        if filename is not None:
            OUTPUT=open(filename,"w")
            self.display(ostream=OUTPUT)
            OUTPUT.close()
            return
        if ostream is None:
            ostream = sys.stdout
        if self._parent is not None and self._parent() is not None:
            ostream.write("Block "+self.cname()+'\n')
        else:
            ostream.write("Model "+self.cname()+'\n')
        #
        ostream.write("\n")
        ostream.write("  Variables:\n")
        VAR = self.active_subcomponents(Var)
        if not VAR:
            ostream.write("    None\n")
        else:
            for obj in itervalues(VAR):
                obj.display(prefix="    ",ostream=ostream)
        #
        ostream.write("\n")
        ostream.write("  Objectives:\n")
        OBJ = self.active_subcomponents(Objective)
        if not OBJ:
            ostream.write("    None\n")
        else:
            for obj in itervalues(OBJ):
                obj.display(prefix="    ",ostream=ostream)
        ostream.write("\n")
        #
        CON = self.active_subcomponents(Constraint)
        ostream.write("  Constraints:\n")
        if not CON:
            ostream.write("    None\n")
        else:
            for obj in itervalues(CON):
                obj.display(prefix="    ",ostream=ostream)


class SingletonBlock(_BlockData, Block):

    def __init__(self, *args, **kwds):
        _BlockData.__init__(self, self)
        Block.__init__(self, *args, **kwds)

    def __getstate__(self):
        ans = Block.__getstate__(self)
        ans2 = _BlockData.__getstate__(self)
        for attr, val in iteritems(ans2):
            if attr not in ans:
                ans[attr] = val
            elif val is not ans[attr]:
                if type(val) is weakref.ref:
                    pass
                elif type(ans[attr]) is weakref.ref:
                    ans[attr] = val
                else:
                    raise RuntimeError(
                        "Unexpected attribute difference when pickling "
                        "block attribute '%s' for block '%s'" 
                        % (attr, self.cname()) )
        return ans

    def __setstate__(self, state):
        # Important: call Block before _BlockData so that the Block
        # hierarchy has an opportunity to correct weakrefs before
        # _BlockData performs a blanket assignment
        Block.__setstate__(self, state)
        _BlockData.__setstate__(self, state)


class IndexedBlock(Block):

    def __init__(self, *args, **kwds):
        Block.__init__(self, *args, **kwds)

    #def display(self, ostream=None):
    #    self.pprint(ostream=ostream)

    #def __str__(self):
    #    return str(self.cname())


#register_component(Block, "Blocks are indexed components that contain "
#                   "one or more other model components.")
