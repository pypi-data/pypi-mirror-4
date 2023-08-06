#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the FAST README.txt file.
#  _________________________________________________________________________

import sys
import logging

import coopr.pyomo
from coopr.pyomo.base import Constraint, \
                             Objective, \
                             Suffix, \
                             active_subcomponents_data_generator
from coopr.pyomo.expr import generate_ampl_repn


def preprocess_block_objectives(block):

    # Create a suffix component for the repn
    block_repn_suffix = block.subcomponent("_ampl_repn")
    if (block_repn_suffix is None) or (not block_repn_suffix.type() is Suffix) or (not block_repn_suffix.active is True):
        block.del_component("_ampl_repn")
        block_repn_suffix = block._ampl_repn = Suffix(direction=Suffix.LOCAL,datatype=None)

    all_repns = list()
    for objective_data in active_subcomponents_data_generator(block, Objective): #recursive = False

        if objective_data.expr is None:
            raise ValueError("No expression has been defined for objective %s" % str(key))

        try:
            ampl_repn = generate_ampl_repn(objective_data.expr)
        except Exception:
            err = sys.exc_info()[1]
            logging.getLogger('coopr.pyomo').error\
                ( "exception generating a ampl representation for objective %s: %s" \
                      % (objective_data.cname(True), str(err)) )
            raise
            
        all_repns.append((objective_data,ampl_repn))

    if len(all_repns) > 0:
        block_repn_suffix.updateValues(all_repns)

def preprocess_block_constraints(block):

    # Create a suffix component for the repn
    block_repn_suffix = block.subcomponent("_ampl_repn")
    if (block_repn_suffix is None) or (not block_repn_suffix.type() is Suffix) or (not block_repn_suffix.active is True):
        block.del_component("_ampl_repn")
        block_repn_suffix = block._ampl_repn = Suffix(direction=Suffix.LOCAL,datatype=None)

    all_repns = list()
    for constraint_data in active_subcomponents_data_generator(block, Constraint): #recursive = False

        if constraint_data.body is None:
            raise ValueError("No expression has been defined for the body of constraint %s, index=%s" % (str(constraint.name), str(index)))

        try:
            ampl_repn = generate_ampl_repn(constraint_data.body)
        except Exception:
            err = sys.exc_info()[1]
            logging.getLogger('coopr.pyomo').error\
                ( "exception generating a ampl representation for constraint %s: %s" \
                      % (constraint_data.cname(True), str(err)) )
            raise
        
        all_repns.append((constraint_data,ampl_repn))
                
    if len(all_repns) > 0:
        block_repn_suffix.updateValues(all_repns)

@coopr.core.coopr_api(namespace='pyomo.model')
def compute_ampl_repn(data, model=None):
    """
    This plugin computes the ampl representation for all
    objectives and constraints. All results are stored at the
    block level on a Suffix named "_ampl_repn"

    NOTE: this does not check for trivial constraints

    We break out preprocessing of the objectives and constraints
    in order to avoid redundant and unnecessary work, specifically
    in contexts where a model is iteratively solved and modified.
    we don't have finer-grained resolution, but we could easily
    pass in a Constraint and an Objective if warranted.

    Required:
        model:      A concrete model instance.
    """
    for block in model.all_blocks():
        preprocess_block_constraints(block)
    #
    # TBD: This assumes the objective(s) are always in the main block
    #
    preprocess_block_objectives(model)

