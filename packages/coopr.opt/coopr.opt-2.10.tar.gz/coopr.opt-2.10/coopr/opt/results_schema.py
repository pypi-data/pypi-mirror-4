#! /usr/bin/env python
#
# results_schema
#

import sys
from pyutilib.misc import Options
from coopr.opt import SolverResults

def main():
    if len(sys.argv) > 1:
        print("results_schema  - Print the predefined schema in a SolverResults object")
    options = Options(schema=True)
    r=SolverResults()
    repn = r._repn_(options)
    r.pprint(sys.stdout, options, repn=repn)
