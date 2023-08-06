#
# Unit Tests for coopr.opt.base.OS
#
#

import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+"/../..")
cooprdir = dirname(abspath(__file__))+os.sep+".."+os.sep+".."+os.sep
currdir = dirname(abspath(__file__))+os.sep

from nose.tools import nottest
import coopr.opt
import coopr
import xml
import pyutilib.th as unittest
import pyutilib.services


class Test(unittest.TestCase):

    def setUp(self):
        pyutilib.services.TempfileManager.tempdir = currdir

    def tearDown(self):
        pyutilib.services.TempfileManager.clear_tempfiles()
        if os.path.exists(currdir+"test_sol.txt"):
            os.remove(currdir+"test_sol.txt")

    def test_read_solution1(self):
        reader = coopr.opt.reader.sol.ResultsReader_sol()

    def test_factory(self):
        reader = coopr.opt.ReaderFactory("sol")
        soln = reader(currdir+"test4_sol.sol", suffixes=["dual"])
        soln.write(filename=currdir+"factory.txt", format='json')
        self.assertMatchesJsonBaseline(currdir+"factory.txt", currdir+"test4_sol.jsn")


if __name__ == "__main__":
    unittest.main()
