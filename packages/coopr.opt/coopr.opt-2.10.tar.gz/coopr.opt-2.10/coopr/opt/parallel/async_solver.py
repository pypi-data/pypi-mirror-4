#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________


__all__ = ['AsynchronousSolverManager', 'SolverManagerFactory']

from pyutilib.component.core import *
from pyutilib.component.config import ManagedPlugin
from coopr.opt.parallel.manager import *


class ISolverManager(Interface):
    pass


SolverManagerFactory = CreatePluginFactory(ISolverManager)


class AsynchronousSolverManager(AsynchronousActionManager, ManagedPlugin):

    implements(ISolverManager)

    def __init__(self, **kwds):
        AsynchronousActionManager.__init__(self)
        ManagedPlugin.__init__(self, **kwds)

    def solve(self, *args, **kwds):
        return self.execute(*args, **kwds)
