#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

import sys

import pyutilib.component.core


pyutilib.component.core.PluginGlobals.push_env( 'coopr.pyomo' )

from coopr.pyomo.base import *
import coopr.pyomo.base.pyomo
from coopr.pyomo.expr import *
import coopr.pyomo.data
from coopr.pyomo.io import *
from coopr.pyomo.components import *
import coopr.pyomo.preprocess
import coopr.pyomo.transform
import coopr.pyomo.scripting
import coopr.pyomo.check
import coopr.opt

pyutilib.component.core.PluginGlobals.pop_env()

try:
    import pkg_resources
    #
    # Load modules associated with Plugins that are defined in
    # EGG files.
    #
    for entrypoint in pkg_resources.iter_entry_points('coopr.pyomo'):
        try:
            plugin_class = entrypoint.load()
        except Exception:
            err = sys.exc_info()[1]
            sys.stderr.write( "Error loading coopr.pyomo entry point: %s  entrypoint='%s'\n" % (err, entrypoint) )
except Exception:
    sys.stderr.write( "Error loading coopr.pyomo entry points\n" )

