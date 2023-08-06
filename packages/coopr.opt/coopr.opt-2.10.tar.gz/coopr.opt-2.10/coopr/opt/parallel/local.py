#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________


__all__ = []

from pyutilib.component.core import alias

from coopr.opt.parallel.manager import *
from coopr.opt.parallel.async_solver import *


class SolverManager_Serial(AsynchronousSolverManager):

    alias("serial")

    def clear(self):
        """
        Clear manager state
        """
        AsynchronousSolverManager.clear(self)
        self._ah_list = []
        self._opt = None

    def _perform_queue(self, ah, *args, **kwds):
        """
        Perform the queue operation.  This method returns the ActionHandle,
        and the ActionHandle status indicates whether the queue was successful.
        """
        if 'opt' in kwds:
            self._opt = kwds['opt']
            del kwds['opt']
        if self._opt is None:
            raise ActionManagerError("Undefined solver")
        self.results[ah.id] = self._opt.solve(*args, **kwds)
        ah.status = ActionStatus.done
        self._ah_list.append(ah)
        return ah

    def _perform_wait_any(self):
        """
        Perform the wait_any operation.  This method returns an
        ActionHandle with the results of waiting.  If None is returned
        then the ActionManager assumes that it can call this method again.
        Note that an ActionHandle can be returned with a dummy value,
        to indicate an error.
        """
        if len(self._ah_list) > 0:
            return self._ah_list.pop()
        return ActionHandle(error=True, explanation="No queued evaluations available in the 'local' solver manager, which only executes solvers synchronously")
