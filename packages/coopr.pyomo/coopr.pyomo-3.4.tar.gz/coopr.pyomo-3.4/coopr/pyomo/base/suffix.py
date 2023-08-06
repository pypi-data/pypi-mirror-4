#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['Suffix','active_export_suffix_generator','active_import_suffix_generator']

import sys
import logging
import weakref
import copy
import pyutilib.math
from six import iteritems, iterkeys, itervalues

from coopr.pyomo.base.component import Component, register_component

logger = logging.getLogger('coopr.pyomo')

# A list of convenient suffix generators, including:
#   - active_export_suffix_generator **(used by problem writers)
#   - export_suffix_generator
#   - active_import_suffix_generator **(used by OptSolver and PyomoModel._load_solution)
#   - import_suffix_generator
#   - active_local_suffix_generator
#   - local_suffix_generator
#   - active_suffix_generator
#   - suffix_generator

def active_export_suffix_generator(a_block,datatype=False):
    if (datatype is False):
        for name, suffix in iteritems(a_block.active_subcomponents(Suffix)):
            if suffix.exportEnabled() is True:
                yield name, suffix
    else:
        for name, suffix in iteritems(a_block.active_subcomponents(Suffix)):
            if (suffix.exportEnabled() is True) and \
               (suffix.getDatatype() is datatype):
                yield name, suffix

def export_suffix_generator(a_block,datatype=False):
    if (datatype is False):
        for name, suffix in iteritems(a_block.subcomponents(Suffix)):
            if suffix.exportEnabled() is True:
                yield name, suffix
    else:
        for name, suffix in iteritems(a_block.subcomponents(Suffix)):
            if (suffix.exportEnabled() is True) and \
               (suffix.getDatatype() is datatype):
                yield name, suffix

def active_import_suffix_generator(a_block,datatype=False):
    if (datatype is False):
        for name, suffix in iteritems(a_block.active_subcomponents(Suffix)):
            if suffix.importEnabled() is True:
                yield name, suffix
    else:
        for name, suffix in iteritems(a_block.active_subcomponents(Suffix)):
            if (suffix.importEnabled() is True) and \
               (suffix.getDatatype() is datatype):
                yield name, suffix

def import_suffix_generator(a_block,datatype=False):
    if (datatype is False):
        for name, suffix in iteritems(a_block.subcomponents(Suffix)):
            if suffix.importEnabled() is True:
                yield name, suffix
    else:
        for name, suffix in iteritems(a_block.subcomponents(Suffix)):
            if (suffix.importEnabled() is True) and \
               (suffix.getDatatype() is datatype):
                yield name, suffix

def active_local_suffix_generator(a_block,datatype=False):
    if (datatype is False):
        for name, suffix in iteritems(a_block.active_subcomponents(Suffix)):
            if suffix.getDirection() is Suffix.LOCAL:
                yield name, suffix
    else:
        for name, suffix in iteritems(a_block.active_subcomponents(Suffix)):
            if (suffix.getDirection() is Suffix.LOCAL) and \
               (suffix.getDatatype() is datatype):
                yield name, suffix

def local_suffix_generator(a_block,datatype=False):
    if (datatype is False):
        for name, suffix in iteritems(a_block.subcomponents(Suffix)):
            if suffix.getDirection() is Suffix.LOCAL:
                yield name, suffix
    else:
        for name, suffix in iteritems(a_block.subcomponents(Suffix)):
            if (suffix.getDirection() is Suffix.LOCAL) and \
               (suffix.getDatatype() is datatype):
                yield name, suffix

def active_suffix_generator(a_block,datatype=False):
    if (datatype is False):
        for name, suffix in iteritems(a_block.active_subcomponents(Suffix)):
            yield name, suffix
    else:
        for name, suffix in iteritems(a_block.active_subcomponents(Suffix)):
            if suffix.getDatatype() is datatype:
                yield name, suffix

def suffix_generator(a_block,datatype=False):
    if (datatype is False):
        for name, suffix in iteritems(a_block.subcomponents(Suffix)):
            yield name, suffix
    else:
        for name, suffix in iteritems(a_block.subcomponents(Suffix)):
            if suffix.getDatatype() is datatype:
                yield name, suffix

# THOUGHTS: 

# TODO: Should we, when setting the value on a component, start collecting
#       a dictionary of components by their type (like on Blocks)

# TODO: Do we enforce that a component must be at least declared
#       on a suffix before the default suffix value is associated
#       with it? Another possibility is to explicitly add the component
#       to the internal values dictionary when first accessed, given
#       that the suffix has a default value.

# TODO: Should calling clearValue on a parent component (like _VarArray) clear
#       its own dictionary entry AS WELL AS any possible dictionary entries
#       corresponding to its subcomponent entries (e.g. _VarData members)?
#       Right now this does not happen. One could ask the same of setValue.

# TODO: Can we get rid of the datatype specifier? Or at least only segregate between
#       Symbolic (require a table) vs Numeric (no table) suffixes. Distinguishing 
#       between int, float, and bool seems to be very unpythonic.

class Suffix(Component):
    """A model suffix, representing extranious model data"""

    """
    Constructor Arguments:
        name        The name of this suffix
        direction   The direction of information flow for this suffix.
                        By default, this is LOCAL, indicating that no
                        suffix data is exported or imported.
        datatype    A variable type associated with all values of this
                        suffix. By default, this is float. **Note that
                        all values assigned to this suffix will be 
                        casted using the function associated with
                        this keyword, unless the suffix datatype is
                        assigned None.
        default     The default value associated with all components
                        declared on this suffix.
        table       A dictionary like object mapping datatype values
                        to numeric (integer) values. The associated integer
                        values are used when exporting/importing suffix 
                        data. **Note: this keyword is required for symbolic (str)
                        datatype suffixes.
        rule        A 
    """

    # If more directions are added be sure to update the error
    # message in the setDirection method
    LOCAL  = 0 # neither
    EXPORT = 1 # sent to solver or other external location
    IMPORT = 2 # obtained from solver or other external source
    IMPORT_EXPORT = 3 # both
    SuffixDirections = (LOCAL,EXPORT,IMPORT,IMPORT_EXPORT)
    SuffixDatatypes = (bool,int,float,str,None)

    def __getstate__(self):
        """
        This method must be defined for deepcopy/pickling because 
        this class relies on component ids.
        """
        result = super(Suffix, self).__getstate__()
        result['_component_value_map'] = tuple((ref(),val) for ref,val in itervalues(self._component_value_map) if ref() is not None)
        return result

    def __setstate__(self, state):
        """
        This method must be defined for deepcopy/pickling because 
        this class relies on component ids.
        """
        state['_component_value_map'] = dict((id(comp),(weakref.ref(comp),val)) for comp,val in state['_component_value_map'])
        return super(Suffix,self).__setstate__(state)

    def __init__(self, *args, **kwds):
        
        # Suffix type information
        self._rule = None
        self._direction = None
        self._datatype = None
        self._reverse_table = None
        self._table = None
        self._default = None
        # The meat of suffixes... a dictionary mapping 
        # Pyomo component ids to suffix values
        self._component_value_map = {}

        # TODO: __FIX_ME__: Blocks assume everything is a (Sparse)IndexedComponent inside
        #       __setattr__ so until this is fixed we need to define a dummy _index data
        #       member
        self._index = None

        # The suffix direction
        direction = kwds.pop('direction',Suffix.LOCAL)
        # The suffix datatype
        datatype = kwds.pop('datatype',float)
        # The optional suffix table
        table = kwds.pop('table',None)
        # The default suffix value for all components
        default = kwds.pop('default',None)
        # A constructor rule for convenience with AbstractModels
        self._rule = kwds.pop('rule',None)
        
        # Initialize base class
        kwds.setdefault('ctype', Suffix)
        Component.__init__(self, *args, **kwds)

        # Check that keyword values make sense 
        # (these function have internal error checking).
        self.setDirection(direction)
        self.setDatatype(datatype,table)
        self.setDefault(default)

        if self._rule is None:
            self.construct()

    def reset(self):
        """
        Reconstructs this component by clearing all values and re-calling
        construction rule if it exists
        """
        self.clearValue()
        self._constructed = False
        self.construct()

    def construct(self, data=None):
        """
        Constructs this component, applying rule if it exists.
        """
        generate_debug_messages = (__debug__ is True) and (logger.isEnabledFor(logging.DEBUG) is True)

        if generate_debug_messages is True:
            logger.debug("Constructing suffix %s",self.cname())

        if self._constructed is True:
            return
        self._constructed = True
        if self._rule is not None:
            self._rule(self._parent())
            return

    def exportEnabled(self):
        """
        Returns True when this suffix is enabled for export to solvers.
        """
        return bool(self._direction & Suffix.EXPORT)

    def importEnabled(self):
        """
        Returns True when this suffix is enabled for import from solutions.
        """
        return bool(self._direction & Suffix.IMPORT)

    def getRule(self):
        """
        Returns the current constructor rule on this component."
        """
        return self._rule

    def setRule(self,rule):
        """
        Sets the constructor rule for this component.
        """
        self._rule = rule
        
    def setNumericValue(self,component,value):
        """
        Set the current numeric value of this suffix on the
        specified component. This method should be used by all
        solution loaders that hold a numeric interpretation of 
        the suffix.
        """
        if self._reverse_table is not None:
            if value.__class__ is not int:
                raise ValueError("Can not call Suffix.setNumericValue() with a non-integer type "\
                                  "when the Suffix component has a table. Current value %s has "\
                                  "type %s." % (value, value.__class__))
            self.setValue(component,self._reverse_table[value])
            return

        # this should not be possible at this point
        # str datatype should always have a reverse table
        assert self._datatype is not str

        self.setValue(component,value)

    def getNumericValue(self,component):
        """
        Returns the current numeric value of this suffix on the 
        specified component. This method should be used by all
        problem writers that require a numeric interpretation of
        the suffix. If no value exists and no default value exists
        this function will return None.
        """
        if (self._datatype is None) and (self._table is None):
            raise RuntimeError("Suffix method getNumericValue can not be called on a suffix "\
                                "component whose datatype and table are both None. Only a suffix "\
                                "table can guarantee numeric return type.")

        value = self.getValue(component)
        if value is None:
            return None

        if self._table is not None:
            return self._table[value]

        # this should not be possible at this point
        # str datatype should always have a table
        assert self._datatype is not str

        if self._datatype is bool:
            return int(self.getValue(component))

        return self.getValue(component)

    def updateValues(self,data_buffer):
        """
        Updates the suffix data given a list of component/value tuples. Provides
        an improvement in efficiency over calling setValue on every component.
        """
        if self._datatype is None:
            self._component_value_map.update((id(comp),(weakref.ref(comp),val)) for comp,val in data_buffer)
        else:
            self._component_value_map.update((id(comp),(weakref.ref(comp),self._datatype(val))) for comp,val in data_buffer)

    def setValue(self,*args):
        """
        Sets the value of this suffix on the specified component 
        or on all components if no component is specified. This 
        function accepts exactly one or two arguments. A suffix
        value is always a required argument. If a component
        is specified, it must be the first argument.
        """
        if len(args) == 1:
            # setting the value on all components currently handled
            value = args[0]
            # This helps clear up any ambiguity about what it means for a suffix
            # to be defined for a component. Otherwise we would have to ask questions like:
            #  (1) Is it directly referenced in the internal suffix dict?
            #  (2) Is it indirectly referenced (Vararray -> VarData) in the internal suffix dict?
            #  (3) If default is not None, does it mean this suffix is defined for all components?
            # I can't answer these right now, so it's easiest to say: Obtaining a value of None
            # by calling getValue implies the suffix is NOT defined for a component.
            if value is None:
                raise ValueError("Explicitly setting component suffix values "\
                                  "to None is not allowed. Try calling the suffix method "\
                                  "clearValue() instead, and ensure that the suffix "\
                                  "default value is set to None.")
            if self._datatype is None:
                self._component_value_map = dict((id(ref()),(ref,value)) for ref,val in itervalues(self._component_value_map) \
                                                                               if ref() is not None)
            else:
                self._component_value_map = dict((id(ref()),(ref,self._datatype(value))) for ref,val in itervalues(self._component_value_map) \
                                                                                               if ref() is not None)
        elif len(args) == 2:
            # setting the value on a specified component
            component = args[0]
            value = args[1]
            # This helps clear up any ambiguity about what it means for a suffix
            # to be defined for a component. Otherwise we would have to ask questions like:
            #  (1) Is it directly referenced in the internal suffix dict?
            #  (2) Is it indirectly referenced (Vararray -> VarData) in the internal suffix dict?
            #  (3) If default is not None, does it mean this suffix is defined for all components?
            # I can't answer these right now, so its easiest to say: Obtaining a value of None
            # by calling getValue implies the suffix is NOT defined for a component.
            if value is None:
                raise ValueError("Explicitly setting component suffix values "\
                                  "to None is not allowed. Try calling the suffix method "\
                                  "clearValue() instead, and ensure that the suffix "\
                                  "default value is set to None.")
            cid = id(component)
            if self._datatype is None:
                self._component_value_map[cid] = (weakref.ref(component),value)
            else:
                self._component_value_map[cid] = (weakref.ref(component),self._datatype(value))
        else:
            raise TypeError("Suffix.setValue() takes exactly one or two arguments (%s given)" % (len(args),))

    def getValue(self,component):
        """
        Returns the current value of this suffix on the 
        specified component.
        """
        cid = id(component)
        # check if the component has been assigned an individual
        # suffix value.
        # **Note: We do this safely by checking that the id is still valid
        #         for the original component it was assigned to by checking
        #         the weakref
        value = None
        if cid in self._component_value_map:
            value = self._component_value_map[cid]
            if value[0]() is component:
                value = value[1]
            else:
                # A rare case where the id was reassigned
                value = None
                del self._component_value_map[cid]
        if (value is None) and (not (component is component.component())):     
            # In the event that this component is part of an indexed
            # component and its container component exists (e.g.
            # x[1] has not been assigned a suffix value but x has), then
            # let us return that suffix value. This mocks behavior of
            # allowing for a default suffix value to exist across an
            # indexed component.
            component = component.component()
            cid = id(component)
            if cid in self._component_value_map:
                value = self._component_value_map[cid]
                if value[0]() is component:
                    value = value[1]
                else:
                    # A rare case where the id was reassigned
                    value = None
                    del self._component_value_map[cid]
        if value is None:
            # Then lets go ahead and return the full suffix default,
            # which could be None
            return self._default
        return value
        
    def clearValue(self,*args):
        """
        Clears suffix information for a single component, or all
        components if no component is specified. This function 
        accepts, at most, one argument, which is assumed to be
        the component. 
        """
        if len(args) == 0:
            # clearing the value on all components currently handled
            self._component_value_map = {}
        elif len(args) == 1:
            # clearing the value on a specified component
            cid = id(args[0])
            if cid in self._component_value_map:
                value = self._component_value_map[cid]
                if value[0]() is args[0]:
                    del self._component_value_map[cid]
        else:
            raise TypeError("Suffix.clearValue() takes exactly one or zero arguments (%s given)" % (len(args),))

    def setTable(self,table):
        """
        Set the suffix table. Symbolic type suffixes (str)
        require that the table keyword defines a dictionary
        mapping string values to integers. Setting table
        to None, clears the existing table if possible.
        """
        if (self._datatype is str) and (table is None):
            raise ValueError("Suffix table is required when suffix datatype is of type %s." % (str,))
        if table is not None:
            reverse_table = {}
            for key,value in iteritems(table):
                if (self._datatype is not None) and (not key.__class__ is self._datatype):
                    raise TypeError("Suffix table must have keys of type %s, but key %s has type %s" \
                        % (self._datatype, key, key.__class__))
                if not value.__class__ is int:
                    raise TypeError("Suffix table must have values of type %s, but value %s has type %s" \
                    % (int,value, value.__class__))
                reverse_table[value] = key
            if len(table) != len(reverse_table):
                raise ValueError("Error constructing reverse suffix table. Suffix table values must all" \
                                  "be unique.")
            self._table = copy.deepcopy(table)
            self._reverse_table = reverse_table
        else:
            self._table = None
            self._reverse_table = None

    def getTable(self):
        """
        Return a copy of the suffix table map."
        """
        return copy.deepcopy(self._table)

    def getReverseTable(self):
        """
        Return a copy of the suffix table reverse map."
        """
        return copy.deepcopy(self._reverse_table)
        
    def setDatatype(self,datatype,table=None):
        """
        Set the suffix datatype. Symbolic type suffixes (str)
        require that the table keyword defines a dictionary
        mapping string values to integers. Setting table
        to None or ommiting the table keyword clears the 
        existing table if possible.
        """
        if datatype not in self.SuffixDatatypes:
            raise ValueError("Suffix datatype must be one of: %s. \n" \
                              "Value given: %s" % (Suffix.SuffixDatatypes,datatype))
        self._datatype = datatype
        self.setTable(table)

    def getDatatype(self):
        """
        Return the suffix datatype.
        """
        return self._datatype

    def setDirection(self,direction):
        """ 
        Set the suffix direction.
        """
        if not direction in self.SuffixDirections:
            raise ValueError("Suffix direction must be one of: %s. \n" \
                              "Value given: %s" % (('Suffix.EXPORT','Suffix.IMPORT','Suffix.IMPORT_EXPORT','Suffix.LOCAL'),direction))
        self._direction = direction

    def getDirection(self):
        """
        Return the suffix direction.
        """
        return self._direction

    def setDefault(self,default):
        """
        Set the default value for this suffix on all
        components.
        """
        if default is None:
            self._default = None
        else:
            if self._datatype is None:
                self._default = default
            else:
                self._default = self._datatype(default)
            
    def getDefault(self):
        """
        Return the suffix default.
        """
        return self._default

    def __str__(self):
        """
        Return a string representation of the suffix.  If the name attribute is None,
        then return ''
        """
        if self.cname() is None:
            return ""
        else:
            return self.cname()

    def pprint(self, ostream=None, verbose=False):
        """Print component information"""
        if ostream is None:
            ostream = sys.stdout
        ostream.write("  "+self.cname()+" :")
        if not self.doc is None:
            ostream.write(self.doc+'\n')
        else:
            ostream.write('\n')
        ostream.write("  ")
        ostream.write("\tDirection=")
        if self._direction == Suffix.EXPORT:
            ostream.write("EXPORT\n")
        elif self._direction is Suffix.IMPORT:
            ostream.write("IMPORT\n")
        elif self._direction is Suffix.LOCAL:
            ostream.write("LOCAL\n")
        elif self._direction is Suffix.IMPORT_EXPORT:
            ostream.write("IMPORT_EXPORT\n")
        else:
            raise ValueError("Unexpected Suffix direction encountered in pprint method.")
        ostream.write("\tDatatype= "+str(self._datatype)+'\n')
        ostream.write("\tTable= "+str(self._table)+'\n')
        ostream.write("\tDefault= "+str(self._default)+'\n')
        # print all component values
        if verbose is True:
            ostream.write('\tValues=\n')
            name_data = dict((ref().cname(True),val) for ref,val \
                                                     in itervalues(self._component_value_map) \
                                                     if ref() is not None)
            for key in sorted(iterkeys(name_data)):
                ostream.write('\t  %s = %s\n' % (key, name_data[key]))

register_component(Suffix, "Extraneous model data")
