#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['IOptSolver', 'OptSolver', 'SolverFactory']

import os
import sys
import time

from pyutilib.enum import Enum
from pyutilib.component.core import *
from pyutilib.component.config import *
import pyutilib.common
import pyutilib.misc
import pyutilib.services

# need to do the below for the is_constructed check - just can't yet due to a circular dependency
#from coopr.pyomo.base import Block

from coopr.opt.base.convert import convert_problem
from coopr.opt.base.formats import ResultsFormat, ProblemFormat
import coopr.opt.base.results
from coopr.opt.results import SolverResults, SolverStatus

from six.moves import xrange

# The version string is first searched for trunk/Trunk, and if 
# found a tuple of infinities is returned. Otherwise, the first
# match of number[.number] where [.number] can repeat 1-3 times
# is used, which is translated into a tuple of size matching
# the keyword length (appending 0's when necessary). If no match
# is found None is returned (although one could argue a tuple of
# 0's might be appropriated).
def _extract_version(x, length=4):
    """
    Attempts to extract solver version information from a string.
    """
    assert (1 <= length) and (length <= 4)
    m = re.search('[t,T]runk',x)
    if m is not None:
        # Since most version checks are comparing if the current 
        # version is greater/less than some other version, it makes
        # since that a solver advertising trunk should always be greater
        # than a version check, hence returning a tuple of infinities
        return tuple(float('inf') for i in xrange(length))
    m = re.search('[0-9]+(\.[0-9]+){1,3}',x)
    if not m is None:
        version = tuple(int(i) for i in m.group(0).split('.')[:length])
        while(len(version) < length):
            version += (0,)
        return version
    return None #(0,0,0,0)[:length]

class IOptSolver(Interface):
    """Interface class for creating optimization solvers"""

    def available(self, exception_flag=True):
        """Determine if this optimizer is available."""

    def warm_start_capable(self):
        """ True is the solver can accept a warm-start solution."""

    def solve(self, *args, **kwds):
        """Perform optimization and return an SolverResults object."""

    def reset(self):
        """Reset the state of an optimizer"""

    def set_options(self, istr):
        """Set the options in the optimizer from a string."""


SolverFactory = CreatePluginFactory(IOptSolver)
def __solver_call__(self, _name=None, args=[], **kwds):
    if _name is None:
        return self
    _name=str(_name)
    if ':' in _name:
        _name, subsolver = _name.split(':',1)
    elif 'solver' in kwds:
        subsolver = kwds['solver']
        del kwds['solver']
    else:
        subsolver = None
    opt = None
    if _name in IOptSolver._factory_active:
        opt = PluginFactory(IOptSolver._factory_cls[_name], args, **kwds)
    else:
        mode = kwds.get('solver_io', 'nl')
        if mode is None:
            mode = 'nl'
        pyutilib.services.register_executable(name=_name)
        if pyutilib.services.registered_executable(_name):
            if mode == 'nl':
                opt = PluginFactory(IOptSolver._factory_cls['_asl'], args, **kwds)
            elif mode == 'os':
                opt = PluginFactory(IOptSolver._factory_cls['_ossolver'], args, **kwds)
            if not opt is None:
                opt.set_options('solver='+_name)
    if not opt is None and not subsolver is None:
        opt.set_options('subsolver='+subsolver)
    return opt
pyutilib.misc.add_method(SolverFactory, __solver_call__, name='__call__')


#class OptSolver(ManagedPlugin):
class OptSolver(Plugin):
    """A generic optimization solver"""

    implements(IOptSolver)

    def __init__(self, **kwds):
        """ Constructor """

        Plugin.__init__(self,**kwds)

        #
        # The 'type' is the class type of the solver instance
        #
        if "type" in kwds:
            self.type = kwds["type"]
        else:                           #pragma:nocover
            raise PluginError("Expected option 'type' for OptSolver constructor")
        #
        # The 'name' is either the class type of the solver instance, or a
        # assigned name.
        #
        if "name" in kwds:
            self.name = kwds["name"]
        else:
            self.name = self.type

        if "doc" in kwds:
            self._doc = kwds["doc"]
        else:
            if self.type is None:           # pragma:nocover
                self._doc = ""
            elif self.name == self.type:
                self._doc = "%s OptSolver" % self.name
            else:
                self._doc = "%s OptSolver (type %s)" % (self.name,self.type)

        if False:
            # This was used for the managed plugin
            declare_option("options", cls=DictOption, section=self.name, doc=self._doc, ignore_missing=True)
        else:
            self.options = pyutilib.misc.Options()

        if 'options' in kwds and not kwds['options'] is None:
            for key in kwds['options']:
                setattr(self.options,key,kwds['options'][key])

        # the symbol map is an attribute of the solver plugin only because
        # it is generated in presolve and used to tag results so they are
        # interpretable - basically, it persists across multiple methods.
        self._symbol_map=None

        # when communicating with a solver, only use symbolic (model-oriented) names - such as
        # "my_favorite_variable[1,2,3]", instead of "v1" when requested (useful for debugging).
        self.symbolic_solver_labels = False

        self._problem_format=None
        self._results_format=None
        self._valid_problem_formats=[]
        self._valid_result_formats={}
        self.results_reader=None
        self.problem=None
        self._assert_available=False
        self._report_timing = False # timing statistics are always collected, but optionally reported.
        self.suffixes = [] # a list of the suffixes the user has request be loaded in a solution.

        # We define no capabilities for the generic solver; base classes must override this
        self._capabilities = pyutilib.misc.Options()

    def version(self):
        """
        Returns a tuple describing the solver executable version.
        """
        raise NotImplementedError       #pragma:nocover

    def problem_format(self):
        """
        Returns the current problem format.
        """
        return self._problem_format

    def set_problem_format(self,format):
        """
        Set the current problem format (if it's valid) and update
        the results format to something valid for this problem format.
        """
        if format in self._valid_problem_formats:
            self._problem_format = format
        else:
            raise ValueError("%s is not a valid problem format for solver plugin %s" % (format, self))
        self._results_format = self._default_results_format(self._problem_format)

    def results_format(self):
        """
        Returns the current results format.
        """
        return self._results_format

    def set_results_format(self,format):
        """
        Set the current results format (if it's valid for the current
        problem format).
        """
        if (self._problem_format in self._valid_results_formats) and \
           (format in self._valid_results_formats[self._problem_format]):
            self._results_format = format
        else:
            raise ValueError("%s is not a valid results format for problem format %s with solver plugin %s" % (format, self._problem_format, self))

    def has_capability(self, cap):
        """
        Returns a boolean value representing whether a solver supports
        a specific feature. Defaults to 'False' if the solver is unaware
        of an option. Expects a string.

        Example:
        print solver.sos1 # prints True if solver supports sos1 constraints,
                          # and False otherwise
        print solver.feature # prints True is solver supports 'feature', and
                             # False otherwise
        """
        if not isinstance(cap, str):
            raise TypeError("Expected argument to be of type '%s', not " + \
                  "'%s'." % (str(type(str())), str(type(cap))))
        else:
            val = self._capabilities[str(cap)]
            if val is None:
                return False
            else:
                return val

    def available(self, exception_flag=True):
        """ True if the solver is available """
        if self._assert_available:
            return True
        tmp = self.enabled()
        if exception_flag and not tmp:
            raise pyutilib.common.ApplicationError("OptSolver plugin %s is disabled" % self.name)
        return tmp

    def warm_start_capable(self):
        """ True is the solver can accept a warm-start solution """
        return False

    def solve(self, *args, **kwds):
        """ Solve the problem """
        
        from coopr.pyomo.base import Block
        from coopr.pyomo.base.suffix import Suffix, active_import_suffix_generator
        # If the inputs are models, then validate that they have been
        # constructed! Collect suffix names to try and import from solution.
        #
        for arg in args:
            if isinstance(arg, Block) is True:
                if arg.is_constructed() is False:
                    raise RuntimeError(
                        "Attempting to solve model=%s with unconstructed "
                        "component(s)" % (arg.name,) )
                # Collect suffixes, but only if the suffix keyword is not
                # already defined. The user passing suffix names in this
                # keyword will override this automitic collection of all
                # active import suffixes. Note if they supply a list
                # of suffix names but these suffixes are not declared on the
                # model, it won't matter what gets placed in the results object,
                # nothing will get loaded into the model.
                if not "suffixes" in kwds:
                    kwds['suffixes'] = list(name for (name,comp) in active_import_suffix_generator(arg))
        
        # ignore the verbosity flag.
        if 'verbose' in kwds:
            del kwds['verbose']
        
        # we're good to go.
        initial_time = time.time()

        self._presolve(*args, **kwds)
        presolve_completion_time = time.time()
        
        _status = self._apply_solver()
        if not hasattr(_status, 'rc'):
            logger.warning(
                "Solver (%s) did not return a solver status code.\n"
                "This is indicative of an internal solver plugin error.\n"
                "Please report this to the Coopr developers." )
        elif _status.rc:
            logger.error(
                "Solver (%s) returned non-zero return code (%s)" 
                % (self.name, _status.rc,) )
            if self.tee:
                logger.error(
                    "See the solver log above for diagnostic information." )
            elif hasattr(_status, 'log') and _status.log:
                logger.error( "Solver log:\n" + str(_status.log) )
            raise pyutilib.common.ApplicationError(
                "Solver (%s) did not exit normally" % self.name )
        solve_completion_time = time.time()
        
        result = self._postsolve()
        postsolve_completion_time = time.time()
        
        result._symbol_map = self._symbol_map
        
        if self._report_timing is True:
            print("Presolve time=%0.2f seconds" % (presolve_completion_time-initial_time))
            print("Solve time=%0.2f seconds" % (solve_completion_time - presolve_completion_time))
            print("Postsolve time=%0.2f seconds" % (postsolve_completion_time-solve_completion_time))
        
        return result

    def _presolve(self, *args, **kwds):
        self._timelimit=None
        self.tee=None
        for key in kwds:
            if key == "logfile":
                self.log_file=kwds[key]
            elif key == "solnfile":
                self.soln_file=kwds[key]
            elif key == "timelimit":
                self._timelimit=kwds[key]
            elif key == "tee":
                self.tee=kwds[key]
            elif key == "options":
                self.set_options(kwds[key])
            elif key == "available":
                self._assert_available=True
            elif key == "symbolic_solver_labels":
                self.symbolic_solver_labels = bool(kwds[key])
            elif key == "suffixes":
                self.suffixes=kwds[key]
            else:
                raise ValueError("Unknown option="+key+" for solver="+self.type)
        self.available()

        (self._problem_files,self._problem_format,self._symbol_map) = self._convert_problem(args, self._problem_format, self._valid_problem_formats)
        if type(self._problem_files) in (list,tuple) and not isinstance(self._problem_files[0], basestring):
            self._problem_files = self._problem_files[0]._problem_files()
        if self._results_format is None:
            self._results_format= self._default_results_format(self._problem_format)

        #
        # Disabling this check for now.  A solver doesn't have just _one_ results format.
        #
        #if self._results_format not in self._valid_result_formats[self._problem_format]:
        #   raise ValueError, "Results format `"+str(self._results_format)+"' cannot be used with problem format `"+str(self._problem_format)+"' in solver "+self.name
        if self._results_format == ResultsFormat.soln:
            self.results_reader = None
        else:
            self.results_reader = coopr.opt.base.results.ReaderFactory(self._results_format)

    def _apply_solver(self):
        """The routine that performs the solve"""
        raise NotImplementedError       #pragma:nocover

    def _postsolve(self):
        """The routine that does solve post-processing"""
        return self.results

    def _convert_problem(self, args, problem_format, valid_problem_formats):

        #
        # If the problem is not None, then we assume that it has already
        # been appropriately defined.  Either it's a string name of the
        # problem we want to solve, or its a functor object that we can
        # evaluate directly.
        #
        if self.problem is not None:
            return (self.problem,ProblemFormat.colin_optproblem, None)

        #
        # Otherwise, we try to convert the object explicitly.
        #
        return convert_problem(args, 
                               problem_format, 
                               valid_problem_formats, 
                               self.has_capability,
                               symbolic_solver_labels=self.symbolic_solver_labels)

    def _default_results_format(self, prob_format):
        """Returns the default results format for different problem
            formats.
        """
        return ResultsFormat.results

    def reset(self):
        """
        Reset the state of the solver
        """
        pass

    def set_options(self, istr):
        istr = istr.strip()
        if istr is '':
            return
        if istr[0] == "'" or istr[0] == '"':
            istr = eval(istr)
        tokens = pyutilib.misc.quote_split('[ ]+',istr)
        for token in tokens:
            index = token.find('=')
            if index is -1:
                raise ValueError("Solver options must have the form option=value")
            try:
                val = eval(token[(index+1):])
            except:
                val = token[(index+1):]
            setattr(self.options, token[:index], val)
