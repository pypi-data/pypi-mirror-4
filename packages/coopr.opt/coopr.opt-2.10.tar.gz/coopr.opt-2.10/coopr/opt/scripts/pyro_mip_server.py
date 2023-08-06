#! /usr/bin/env python
#
# pyro_mip_server: A script that sets up a Pyro server for solving MIPs in
#           a distributed manner.
#
#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the FAST README.txt file.
#  _________________________________________________________________________

import os
import os.path
import sys
try:
    import cPickle as pickle
except ImportError:
    import pickle
import datetime
import pyutilib.services
import pyutilib.pyro


class CooprMIPWorker(pyutilib.pyro.TaskWorker):

    def process(self, data):
        import coopr.opt

        pyutilib.services.TempfileManager.push()

        # construct the solver on this end, based on the input type stored in "data.opt".
        # this is slightly more complicated for asl-based solvers, whose real executable
        # name is stored in data.solver_options["solver"].
        if data.opt == "asl":
           solver_name = data.solver_options["solver"]
           opt = coopr.opt.SolverFactory(solver_name)
        else:
           opt = coopr.opt.SolverFactory(data.opt)
        if opt is None:
            raise ValueError("Problem constructing solver `"+data.opt+"'")

        opt.suffixes = data.suffixes

        # here is where we should set any options required by the solver, available
        # as specific attributes of the input data object.
        solver_options = data.solver_options
        del data.solver_options
        for key,value in solver_options.items():
            setattr(opt.options,key,value)

        problem_filename_suffix = os.path.split(data.filename)[1]
        temp_problem_filename = pyutilib.services.TempfileManager.create_tempfile(suffix="."+problem_filename_suffix)
        OUTPUT=open(temp_problem_filename,'w')
        OUTPUT.write(data.file)
        OUTPUT.close()

        if data.warmstart_file is not None:
            warmstart_filename_suffix = os.path.split(data.warmstart_filename)[1]
            temp_warmstart_filename = pyutilib.services.TempfileManager.create_tempfile(suffix="."+warmstart_filename_suffix)
            OUTPUT=open(temp_warmstart_filename,'w')
            OUTPUT.write(str(data.warmstart_file)+'\n')
            OUTPUT.close()
            opt.warm_start_solve = True
            opt.warm_start_file_name = temp_warmstart_filename

        now = datetime.datetime.now()
        print(str(now) + ": Applying solver="+data.opt+" to solve problem="+temp_problem_filename)
        sys.stdout.flush()        
        results = opt.solve(temp_problem_filename, **data.kwds)

        # IMPT: The results object will *not* have a symbol map, as the symbol
        #       map is not pickle'able. The responsibility for translation will
        #       will have to be done on the client end.

        pyutilib.services.TempfileManager.pop()

        now = datetime.datetime.now()
        print(str(now) + ": Solve completed - number of solutions="+str(len(results.solution)))
        sys.stdout.flush()
#        results.write()
#        sys.stdout.flush()
        return pickle.dumps(results)


def main():
    pyutilib.pyro.TaskWorkerServer(CooprMIPWorker, argv=sys.argv)
