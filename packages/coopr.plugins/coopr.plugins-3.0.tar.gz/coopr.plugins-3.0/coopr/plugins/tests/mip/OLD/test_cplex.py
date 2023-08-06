#
# Unit Tests for coopr.plugins.mip.CPLEX
#
#

import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+"/../..")
cooprdir = dirname(abspath(__file__))+os.sep+".."+os.sep+".."+os.sep
currdir = dirname(abspath(__file__))+os.sep

from nose.tools import nottest
import pyutilib.th as unittest
import pyutilib.services
import pyutilib.common
import coopr.plugins.mip
import coopr.opt
import coopr
import xml
from coopr.opt import ResultsFormat, ProblemFormat, ConverterError

coopr.opt.SolverResults.default_print_options.ignore_time = True
try:
    cplex = coopr.plugins.mip.CPLEX(keepfiles=True)
    cplex_available= (not cplex.executable() is None) and cplex.available(False)
except pyutilib.common.ApplicationError:
    cplex_available=False
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
        pyutilib.services.TempfileManager.sequential_files(0)
        pyutilib.services.TempfileManager.tempdir = currdir
        if flag:
            self.cplex = coopr.plugins.mip.CPLEX(keepfiles=True)
        else:
            self.cplex = coopr.plugins.mip.MockCPLEX(keepfiles=True)
        self.cplex.suffixes=['.*']

    def tearDown(self):
        global tmpdir
        pyutilib.services.TempfileManager.clear_tempfiles()
        os.chdir(tmpdir)
        pyutilib.services.TempfileManager.unique_files()

    def test_path(self):
        """ Verify that the CPLEX path is what is expected """
        if type(self.cplex) is 'CPLEX':
            self.failUnlessEqual(self.cplex.executable.split(os.sep)[-1],"CPLEX"+coopr.util.executable_extension)

    def test_solve1(self):
        """ Test CPLEX - test1.mps """
        results = self.cplex.solve(currdir+"test1.mps", logfile=currdir+"test_solve1.log")
        results.write(filename=currdir+"test_solve1.txt",times=False)
        self.failUnlessFileEqualsBaseline(currdir+"test_solve1.txt", currdir+"test1_cplex.txt")
        #os.remove(currdir+"test_solve1.log")

    def test_solve2a(self):
        """ Test CPLEX - test1.mps """
        results = self.cplex.solve(currdir+"test1.mps", rformat=ResultsFormat.soln, logfile=currdir+"test_solve2a.log")
        results.write(filename=currdir+"test_solve2a.txt",times=False)
        self.failUnlessFileEqualsBaseline(currdir+"test_solve2a.txt", currdir+"test1_cplex.txt")
        #os.remove(currdir+"test_solve2a.log")

    def test_solve2b(self):
        """ Test CPLEX - test1.mps """
        results = self.cplex.solve(currdir+"test1.mps", pformat=ProblemFormat.mps, rformat=ResultsFormat.soln, logfile=currdir+"test_solve2b.log")
        results.write(filename=currdir+"test_solve2b.txt",times=False)
        self.failUnlessFileEqualsBaseline(currdir+"test_solve2b.txt", currdir+"test1_cplex.txt")
        #os.remove(currdir+"test_solve2b.log")

    def test_solve3(self):
        """ Test CPLEX - test2.lp """
        results = self.cplex.solve(currdir+"test2.lp", logfile=currdir+"test_solve3.log", keepfiles=True)
        results.write(filename=currdir+"test_solve3.txt",times=False)
        self.failUnlessFileEqualsBaseline(currdir+"test_solve3.txt", currdir+"test2_cplex.txt")
        if os.path.exists(currdir+"test2.solution.dat"):
            os.remove(currdir+"test2.solution.dat")
        #os.remove(currdir+"test_solve3.log")

    def test_solve4(self):
        """ Test CPLEX - test4.nl """
        if pico_convert_available:
            results = self.cplex.solve(currdir+"test4.nl", logfile=currdir+"test_solve4.log")
            results.write(filename=currdir+"test_solve4.txt",times=False)
            self.failUnlessFileEqualsBaseline(currdir+"test_solve4.txt", currdir+"test4_cplex.txt")
        else:
            try:
                results = self.cplex.solve(currdir+"test4.nl", logfile=currdir+"test_solve4.log")
            except ConverterError:
                return
        #os.remove(currdir+"test4.sol")
        #os.remove(currdir+"test_solve4.log")

    #
    # This test is disabled, but it's useful for interactively exercising
    # the option specifications of a solver
    #
    def Xtest_options(self):
        """ Test CPLEX options behavior """
        results = self.cplex.solve(currdir+"bell3a.mps", logfile=currdir+"test_options.log", options="sec=0.1 foo=1 bar='a=b c=d' xx_zz=yy")
        results.write(filename=currdir+"test_options.txt",times=False)
        self.failUnlessFileEqualsBaseline(currdir+"test_options.txt", currdir+  "test4_cplex.txt")
        #os.remove(currdir+"test4.sol")
        #os.remove(currdir+"test_solve4.log")

    def Xtest_mock5(self):
        """ Mock Test CPLEX - test5.mps """
        if cplex_available:
            pass
        results = self.cplex.solve(currdir+"test4.nl", logfile=currdir+"test_solve5.log", keepfiles=True)
        results.write(filename=currdir+"test_mock5.txt",times=False)
        self.failUnlessFileEqualsBaseline(currdir+"test_mock5.txt", currdir+"test4_cplex.txt")
        os.remove(currdir+"test4.sol")
        os.remove(currdir+"test_solve5.log")

    def test_error1(self):
        """ Bad results format """
        try:
            results = self.cplex.solve(currdir+"test1.mps", format=ResultsFormat.sol)
            self.fail("test_error1")
        except ValueError:
            pass

    def test_error2(self):
        """ Bad solve option """
        try:
            results = self.cplex.solve(currdir+"test1.mps", foo="bar")
            self.fail("test_error2")
        except ValueError:
            pass

    def test_error3(self):
        """ Bad solve option """
        try:
            results = self.cplex.solve(currdir+"bad.mps", foo="bar")
            self.fail("test_error3")
        except ValueError:
            pass


class mip_all(mock_all):

    def setUp(self):
        self.do_setup(True)

mip_all = unittest.skipIf(not cplex_available, "The CPLEX solver is not available")(mip_all)

if __name__ == "__main__":
    unittest.main()
