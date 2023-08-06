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

pyutilib.component.core.PluginGlobals.push_env( 'coopr.opt' )

from coopr.opt.base import *
from coopr.opt.results import *
import coopr.opt.solver
import coopr.opt.reader
from coopr.opt.problem import *
from coopr.opt.parallel import *

pyutilib.component.core.PluginGlobals.pop_env()


try:
    import pkg_resources
    #
    # Load modules associated with Plugins that are defined in
    # EGG files.
    #
    for entrypoint in pkg_resources.iter_entry_points('coopr.opt'):
        try:
            plugin_class = entrypoint.load()
        except Exception:
            msg = sys.exc_info()[1]
            sys.stderr.write( "Error loading coopr.opt entry point: %s  entrypoint='%s'\n" % (msg, entrypoint) )
except Exception:
    sys.stderr.write( "Error loading coopr.opt entry points\n" )

