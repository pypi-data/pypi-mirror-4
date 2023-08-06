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
import itertools

from six import iteritems

from coopr.pyomo.base import Constraint, ConstraintList, Objective, Suffix, active_subcomponents_generator
from coopr.pyomo.base import IPyomoPresolver, IPyomoPresolveAction
import coopr.pyomo.expr
from coopr.pyomo.expr import generate_canonical_repn
import coopr.pyomo.base.connector 


def preprocess_block_objectives(block, var_id_map):

    if getattr(block,'skip_canonical_repn',False):
        return block

    active_objectives = block.active_subcomponents(Objective)
    all_repns = list()
    for key, obj in iteritems(active_objectives):
        # number of objective indicies with non-trivial expressions
        num_nontrivial = 0

        for ondx, objective_data in iteritems(obj._data):
            if not objective_data.active:
                continue
            if objective_data.expr is None:
                raise ValueError("No expression has been defined for objective %s" % str(key))

            try:
                objective_data_repn = generate_canonical_repn(objective_data.expr, var_id_map)
            except Exception:
                err = sys.exc_info()[1]
                logging.getLogger('coopr.pyomo').error\
                    ( "exception generating a canonical representation for objective %s (index %s): %s" \
                          % (str(key), str(ondx), str(err)) )
                raise
            if not coopr.pyomo.expr.canonical_is_constant(objective_data_repn):
                num_nontrivial += 1
            
            all_repns.append((objective_data,objective_data_repn))
            
        if num_nontrivial == 0:
            obj.trivial = True
        else:
            obj.trivial = False

    if all_repns != []:
        # Create a suffix component for the repn
        block_repn_suffix = block.subcomponent("repn")
        if (block_repn_suffix is None) or (not block_repn_suffix.type() is Suffix) or (not block_repn_suffix.active is True):
            block.del_component("repn")
            block_repn_suffix = block.repn = Suffix(direction=Suffix.LOCAL,datatype=None)
        block_repn_suffix.updateValues(all_repns)

def preprocess_constraint(block, constraint, var_id_map, block_repn_suffix=None, block_lin_body_suffix=None):

    # number of constraint indicies with non-trivial bodies
    num_nontrivial = 0

    # Create a suffix component for the repn
    if block_repn_suffix is None:
        block_repn_suffix = block.subcomponent("repn")
        if (block_repn_suffix is None) or (not block_repn_suffix.type() is Suffix) or (not block_repn_suffix.active is True):
            block.del_component("repn")
            block.repn = Suffix(direction=Suffix.LOCAL,datatype=None)
            block_repn_suffix = block.repn

    has_lin_body = False
    if block_lin_body_suffix is None:
        block_lin_body_suffix = block.subcomponent("lin_body")
        if (block_lin_body_suffix is not None) and (block_lin_body_suffix.type() is Suffix) and (block_lin_body_suffix.active is True):
            has_lin_body = True
    else:
        has_lin_body = True

    all_repns = list()
    for index, constraint_data in iteritems(constraint._data):

        if not constraint_data.active:
            continue

        if has_lin_body is True:
            lin_body = block_lin_body_suffix.getValue(constraint_data)
            if lin_body is not None:
                # if we already have the linear encoding of the constraint body, skip canonical expression
                # generation. but we still need to assess constraint triviality.
                if not coopr.pyomo.expr.is_linear_expression_constant(lin_body):
                    num_nontrivial += 1
                continue

        if constraint_data.body is None:
            raise ValueError("No expression has been defined for the body of constraint %s, index=%s" % (str(constraint.name), str(index)))

        # FIXME: This is a huge hack to keep canonical_repn from trying to generate representations
        #        representations of Constraints with Connectors (which will be deactivated once they
        #        have been expanded anyways). This can go away when preprocess is moved out of the
        #        model.create() phase and into the future model validation phase. (ZBF)
        ignore_connector = False
        if hasattr(constraint_data.body,"_args") and constraint_data.body._args is not None:
            for arg in constraint_data.body._args:
                if arg.__class__ is coopr.pyomo.base.connector._ConnectorElement:
                    ignore_connector = True
        if ignore_connector:
            #print "Ignoring",constraint.name,index
            continue

        try:
            canonical_repn = generate_canonical_repn(constraint_data.body, var_id_map)
        except Exception:
            logging.getLogger('coopr.pyomo').error \
                                                    ( "exception generating a canonical representation for constraint %s (index %s)" \
                                                      % (str(constraint.name), str(index)) )
            raise
        
        all_repns.append((constraint_data,canonical_repn))
        
        if not coopr.pyomo.expr.canonical_is_constant(canonical_repn):
            num_nontrivial += 1
        
    block_repn_suffix.updateValues(all_repns)

    if num_nontrivial == 0:
        constraint.trivial = True
    else:
        constraint.trivial = False

def preprocess_block_constraints(block, var_id_map):

    if getattr(block,'skip_canonical_repn',False):
        return

    for constraint in active_subcomponents_generator(block,Constraint):

        block_repn_suffix = block.subcomponent("repn")
        if (block_repn_suffix is None) or (not block_repn_suffix.type() is Suffix) or (not block_repn_suffix.active is True):
            block.del_component("repn")
            block.repn = Suffix(direction=Suffix.LOCAL,datatype=None)
            block_repn_suffix = block.repn

        block_lin_body_suffix = block.subcomponent("lin_body")
        if (block_lin_body_suffix is not None) and (block_lin_body_suffix.type() is Suffix) and (block_lin_body_suffix.active is True):
            block_lin_body_suffix = None

        preprocess_constraint(block, 
                              constraint, 
                              var_id_map, 
                              block_repn_suffix=block_repn_suffix, 
                              block_lin_body_suffix=block_lin_body_suffix)


@coopr.core.coopr_api(namespace='pyomo.model')
def compute_canonical_repn(data, model=None):
    """
    This plugin computes the canonical representation for all
    objectives and constraints linear terms.  All modifications are
    in-place, i.e., components of the input instance are modified.

    NOTE: The idea of this module should be generaized. there are
    two key functionalities: computing a version of the expression
    tree in preparation for output and identification of trivial
    constraints.

    NOTE: this leaves the trivial constraints in the model.

    We break out preprocessing of the objectives and constraints
    in order to avoid redundant and unnecessary work, specifically
    in contexts where a model is iteratively solved and modified.
    we don't have finer-grained resolution, but we could easily
    pass in a Constraint and an Objective if warranted.

    Required:
        model:      A concrete model instance.
    """
    var_id_map = {}
    for block in model.all_blocks():
        preprocess_block_constraints(block, var_id_map)
    #
    # TBD: This assumes the objective(s) are always in the main block
    #
    preprocess_block_objectives(model, var_id_map)

