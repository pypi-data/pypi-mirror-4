#
# Unit Tests for coopr.opt.opt_config
#
#

import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+"/../..")
cooprdir = dirname(abspath(__file__))+os.sep+".."+os.sep+".."+os.sep
currdir = dirname(abspath(__file__))+os.sep

import unittest
from nose.tools import nottest
import coopr.opt
import pyutilib.services
import pyutilib.component.app
import pyutilib.misc

pyutilib.services.TempfileManager.tempdir = currdir

class OptConfigDebug(unittest.TestCase):

    def setUp(self):
        pyutilib.services.TempfileManager.tempdir = currdir

    def tearDown(self):
        pyutilib.services.TempfileManager.clear_tempfiles()

    def test_config1(self):
        """
        Read in config file opt1.cfg
        """
        app = pyutilib.component.app.SimpleApplication("testapp")
        #pyutilib.component.PluginGlobals.pprint()
        #app.config.summarize()
        app.save_configuration(currdir+"opt1-out.cfg")
        app.configure(currdir+"opt1.cfg")
        if pyutilib.services.registered_executable("pico_convert"):
            self.assertEqual( pyutilib.services.registered_executable("pico_convert").get_path(), pyutilib.misc.search_file("pico_convert"))
        if pyutilib.services.registered_executable("glpsol"):
            self.assertEqual( pyutilib.services.registered_executable("glpsol").get_path(), pyutilib.misc.search_file("glpsol"))
        if pyutilib.services.registered_executable("ampl"):
            self.assertEqual( pyutilib.services.registered_executable("ampl").get_path(), pyutilib.misc.search_file("ampl"))
        if pyutilib.services.registered_executable("timer"):
            self.assertEqual( pyutilib.services.registered_executable("timer").get_path(), pyutilib.misc.search_file("timer"))


if __name__ == "__main__":
    unittest.main()
