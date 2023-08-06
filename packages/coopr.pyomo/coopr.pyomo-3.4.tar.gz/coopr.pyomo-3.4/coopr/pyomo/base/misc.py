#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['display']

import logging
import sys

logger = logging.getLogger('coopr.pyomo')


def display(obj, ostream=None):
    """ Display data in a Pyomo object"""
    if ostream is None:
        ostream = sys.stdout
    try:
        display_fcn = obj.display
    except AttributeError:
        raise TypeError(
            "Error trying to display values for object of type %s:\n"
            "\tObject does not support the 'display()' method"
            % (type(obj), ) )
    try:
        display_fcn(ostream=ostream)
    except Exception:
        err = sys.exc_info()[1]
        logger.error(
            "Error trying to display values for object of type %s:\n\t%s"
            % (type(obj), err) )
        raise 


def create_name(name, ndx):
    if ndx is None:
        return name
    if type(ndx) is tuple:
        tmp = str(ndx).replace(', ',',')
        return name+"["+tmp[1:-1]+"]"
    return name+"["+str(ndx)+"]"


def apply_indexed_rule(obj, rule, model, index, options=None):
    try:
        if options is None:
            if index.__class__ is tuple:
                return rule(model, *index)
            return rule(model, index)
        else:
            if index.__class__ is tuple:
                return rule(model, *index, **options)
            return rule(model, index, **options)
    except TypeError:
        try:
            if options is None:
                return rule(model)
            else:
                return rule(model, **options)
        except:
            # Nothing appears to have matched... re-trigger the original
            # TypeError
            if options is None:
                if index.__class__ is tuple:
                    return rule(model, *index)
                return rule(model, index)
            else:
                if index.__class__ is tuple:
                    return rule(model, *index, **options)
                return rule(model, index, **options)

def apply_parameterized_indexed_rule(obj, rule, model, param, index):
    if index.__class__ is tuple:
        return rule(model, param, *index)
    return rule(model, param, index)

