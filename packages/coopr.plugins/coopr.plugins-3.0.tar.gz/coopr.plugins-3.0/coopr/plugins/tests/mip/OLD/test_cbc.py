#
# Unit Tests for coopr.plugins.mip.CBC
#
#

import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+"/../..")
cooprdir = dirname(abspath(__file__))+os.sep+".."+os.sep+".."+os.sep
currdir = dirname(abspath(__file__))+os.sep

import pyutilib.th as unittest
import pyutilib.common
import pyutilib.services
from nose.tools import nottest
import coopr.plugins.mip
import coopr.opt
import coopr
import xml
from coopr.opt import ResultsFormat, ProblemFormat

coopr.opt.SolverResults.default_print_options.ignore_time = True
try:
    cbc = coopr.plugins.mip.CBC(keepfiles=True)
    cbc_available= (not cbc.executable() is None)
except pyutilib.common.ApplicationError:
    cbc_available=False
    pass

try:
    pico_convert =  pyutilib.services.registered_executable("pico_convert")
    pico_convert_available= (not pico_convert is None)
except pyutilib.common.ApplicationError:
    pico_convert_available=False



class mock_all(unittest.TestCase):

    def setUp(self):
        self.do_setup(False)

    def do_setup(self,flag):
        global tmpdir
        tmpdir = os.getcwd()
        os.chdir(currdir)
        pyutilib.services.TempfileManager.tempdir = currdir
        if flag:
            self.cbc = coopr.plugins.mip.CBC(keepfiles=True)
        else:
            self.cbc = coopr.plugins.mip.MockCBC(keepfiles=True)
        self.cbc.suffixes=['.*']

    def tearDown(self):
        global tmpdir
        pyutilib.services.TempfileManager.clear_tempfiles()
        os.chdir(tmpdir)

    def test_path(self):
        """ Verify that the CBC path is what is expected """
        if type(self.cbc) is 'CBC':
            self.failUnlessEqual(self.cbc.executable.split(os.sep)[-1],"CBC"+coopr.    util.executable_extension)

    def test_solve1(self):
        """ Test CBC - test1.mps """
        results = self.cbc.solve(currdir+"test1.mps",logfile=currdir+"test_solve1.log", solnfile=currdir+"test1.soln")
        results.write(filename=currdir+"test_solve1.txt",times=False)
        self.failUnlessFileEqualsBaseline(currdir+"test_solve1.txt", currdir+"test1_cbc.txt")
        os.remove(currdir+"test_solve1.log")
        os.remove(currdir+"test1.soln")

    def test_solve2a(self):
        """ Test CBC - test1.mps """
        results = self.cbc.solve(currdir+"test1.mps", rformat=ResultsFormat.soln, logfile=currdir+"test_solve2a.log", solnfile=currdir+"test1.soln")
        results.write(filename=currdir+"test_solve2a.txt",times=False)
        self.failUnlessFileEqualsBaseline(currdir+"test_solve2a.txt", currdir+"test1_cbc.txt")
        os.remove(currdir+"test_solve2a.log")
        os.remove(currdir+"test1.soln")

    def test_solve2b(self):
        """ Test CBC - test1.mps """
        results = self.cbc.solve(currdir+"test1.mps", pformat=ProblemFormat.mps, rformat=ResultsFormat.soln, logfile=currdir+"test_solve2b.log", solnfile=currdir+"test1.soln")
        results.write(filename=currdir+"test_solve2b.txt",times=False)
        self.failUnlessFileEqualsBaseline(currdir+"test_solve2b.txt", currdir+"test1_cbc.txt")
        os.remove(currdir+"test_solve2b.log")
        os.remove(currdir+"test1.soln")

    def test_solve3(self):
        """ Test CBC - test2.lp """
        results = self.cbc.solve(currdir+"test2.lp", logfile=currdir+"test_solve3.log", solnfile=currdir+"test2.soln")
        results.write(filename=currdir+"test_solve3.txt",times=False)
        self.failUnlessFileEqualsBaseline(currdir+"test_solve3.txt", currdir+"test2_cbc.txt")
        os.remove(currdir+"test_solve3.log")
        os.remove(currdir+"test2.soln")

    def test_solve4(self):
        """ Test CBC - test4.nl """
        try:
            results = self.cbc.solve(currdir+"test4.nl", rformat=ResultsFormat.sol, logfile=currdir+"test_solve4.log", solnfile=currdir+"test4.soln")
            results.write(filename=currdir+"test_solve4.txt",times=False)
            self.failUnlessFileEqualsBaseline(currdir+"test_solve4.txt", currdir+"test4_cbc.txt")
            #os.remove(currdir+"test_solve4.log")
            if os.path.exists(currdir+"ipconvert.lp"):
                os.remove(currdir+"ipconvert.lp")
        except coopr.opt.ConverterError:
            if pico_convert_available:
                raise "Expected conversion of test4.nl to a format that CBC can solve"

    #
    # This test is disabled, but it's useful for interactively exercising
    # the option specifications of a solver
    #
    def Xtest_options(self):
        """ Test CBC options behavior """
        results = self.cbc.solve(currdir+"bell3a.mps", logfile=currdir+"test_options.log", options="sec=0.1 foo=1 bar='a=b c=d' zz=yy")
        results.write(filename=currdir+"test_options.txt",times=False)
        self.failUnlessFileEqualsBaseline(currdir+"test_options.txt", currdir+  "test4_cbc.txt")
        os.remove(currdir+"test4.sol")
        os.remove(currdir+"test_solve4.log")

    def Xtest_prod(self):
        """ Test CBC - prod.mod """
        results = self.cbc.solve(currdir+"prod.mod", logfile=currdir+"test_prod.log", solnfile=currdir+"prod.soln")
        results.write(filename=currdir+"test_prod.txt",times=False)
        self.failUnlessFileEqualsBaseline(currdir+"test_prod.txt", currdir+"prod_cbc.txt")
        os.remove(currdir+"test_prod.log")
        if os.path.exists(currdir+"ipconvert.lp"):
            os.remove(currdir+"ipconvert.lp")
        os.remove(currdir+"prod.soln")

    def Xtest_error1(self):
        """ Bad results format """
        try:
            results = self.cbc.solve(currdir+"test1.mps", rformat=ResultsFormat.sol)
            self.fail("test_error1")
        except ValueError:
            pass

    def test_error2(self):
        """ Bad solve option """
        try:
            results = self.cbc.solve(currdir+"test1.mps", foo="bar")
            self.fail("test_error2")
        except ValueError:
            pass

    def test_error3(self):
        """ Bad solve option """
        try:
            results = self.cbc.solve(currdir+"bad.mps", foo="bar")
            self.fail("test_error3")
        except ValueError:
            pass


class mip_all(mock_all):

    def setUp(self):
        self.do_setup(True)

    def test_solve1a(self):
        """ Test CBC - test1.mps """
        results = self.cbc.solve(currdir+"test1.mps",logfile=currdir+"test_solve1a.log", solnfile=currdir+"test_solve1a.soln")
        results.write(filename=currdir+"test_solve1a.txt",times=False)
        self.failUnlessFileEqualsBaseline(currdir+"test_solve1a.txt", currdir+"test1_cbc.txt")
        os.remove(currdir+"test_solve1a.log")
        #os.remove(currdir+"test_solve1a.soln")

mip_all = unittest.skipIf(not cbc_available, "The 'cbc' command is not available")(mip_all)

if __name__ == "__main__":
    unittest.main()
