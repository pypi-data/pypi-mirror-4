#
# Unit Tests for coopr.plugins.mip.PICO
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
import pyutilib.common
import pyutilib.services
import coopr.plugins.mip
import coopr.opt
import coopr
import xml
from coopr.opt import ResultsFormat, ProblemFormat

coopr.opt.SolverResults.default_print_options.ignore_time = True
try:
    pico_convert =  pyutilib.services.registered_executable("pico_convert")
    pico_convert_available= (not pico_convert is None)
except pyutilib.common.ApplicationError:
    pico_convert_available=False

try:
    pico = coopr.plugins.mip.PICO(keepfiles=True)
    pico_available= (not pico.executable() is None)
except pyutilib.common.ApplicationError:
    pico_available=False
    pass


class mock_all(unittest.TestCase):

    def setUp(self):
        self.do_setup(False)

    def do_setup(self,flag):
        global tmpdir
        tmpdir = os.getcwd()
        os.chdir(currdir)
        pyutilib.services.TempfileManager.tempdir = currdir
        if flag:
            self.pico = coopr.plugins.mip.PICO(keepfiles=True)
        else:
            self.pico = coopr.plugins.mip.MockPICO(keepfiles=True)
        self.pico.suffixes=['.*']

    def tearDown(self):
        global tmpdir
        pyutilib.services.TempfileManager.clear_tempfiles()
        os.chdir(tmpdir)

    def test_path(self):
        """ Verify that the PICO path is what is expected """
        if type(self.pico) is 'PICO':
            self.failUnlessEqual(self.pico.executable.split(os.sep)[-1],"PICO"+coopr.util.executable_extension)

    def test_solve1(self):
        """ Test PICO - test1.mps """
        results = self.pico.solve(currdir+"test1.mps", logfile=currdir+"test_solve1.log")
        results.write(filename=currdir+"test_solve1.txt",times=False)
        self.failUnlessFileEqualsBaseline(currdir+"test_solve1.txt", currdir+"test1_pico.txt")
        os.remove(currdir+"test_solve1.log")

    def test_solve2a(self):
        """ Test PICO - test1.mps """
        results = self.pico.solve(currdir+"test1.mps", rformat=ResultsFormat.soln, logfile=currdir+"test_solve2a.log")
        results.write(filename=currdir+"test_solve2a.txt",times=False)
        self.failUnlessFileEqualsBaseline(currdir+"test_solve2a.txt", currdir+"test1_pico.txt")
        os.remove(currdir+"test_solve2a.log")

    def test_solve2b(self):
        """ Test PICO - test1.mps """
        results = self.pico.solve(currdir+"test1.mps", pformat=ProblemFormat.mps, rformat=ResultsFormat.soln, logfile=currdir+"test_solve2b.log")
        results.write(filename=currdir+"test_solve2b.txt",times=False)
        self.failUnlessFileEqualsBaseline(currdir+"test_solve2b.txt", currdir+"test1_pico.txt")
        os.remove(currdir+"test_solve2b.log")

    def test_solve3(self):
        """ Test PICO - test2.lp """
        results = self.pico.solve(currdir+"test2.lp", logfile=currdir+"test_solve3.log")
        results.write(filename=currdir+"test_solve3.txt",times=False)
        self.failUnlessFileEqualsBaseline(currdir+"test_solve3.txt", currdir+"test2_pico.txt")
        if os.path.exists(currdir+"test2.solution.dat"):
            os.remove(currdir+"test2.solution.dat")
        os.remove(currdir+"test_solve3.log")

    def test_solve4(self):
        """ Test PICO - test4.nl """
        if pico_convert_available:
            results = self.pico.solve(currdir+"test4.nl", rformat=ResultsFormat.sol,  logfile=currdir+"test_solve4.log")
            results.write(filename=currdir+"test_solve4.txt",times=False)
            self.failUnlessFileEqualsBaseline(currdir+"test_solve4.txt", currdir+"test4_pico.txt")
            os.remove(currdir+"test4.sol")
            os.remove(currdir+"test_solve4.log")
        else:
            try:
                results = self.pico.solve(currdir+"test4.nl", rformat=ResultsFormat.sol, logfile=currdir+"test_solve4.log")
            except coopr.opt.ConverterError:
                pass

    def Xtest_mock5(self):
        """ Mock Test PICO - test5.mps """
        if pico_available:
            pass
        results = self.pico.solve(currdir+"test4.nl", logfile=currdir+"test_solve5.log")
        results.write(filename=currdir+"test_mock5.txt",times=False)
        self.failUnlessFileEqualsBaseline(currdir+"test_mock5.txt", currdir+"test4_pico.txt")
        os.remove(currdir+"test4.sol.txt")
        os.remove(currdir+"test_solve5.log")

    #
    # This test is disabled, but it's useful for interactively exercising
    # the option specifications of a solver
    #
    def Xtest_options(self):
        """ Test PICO options behavior """
        results = self.pico.solve(currdir+"bell3a.mps", logfile=currdir+"test_options.log", options="maxCPUMinutes=0.1 foo=1 bar='a=b c=d' zz=yy")
        results.write(filename=currdir+"test_options.txt",times=False)
        self.failUnlessFileEqualsBaseline(currdir+"test_options.txt", currdir+"test4_pico.txt")
        #os.remove(currdir+"test4.sol")
        os.remove(currdir+"test_solve4.log")

    def test_error1(self):
        """ Bad results format """
        try:
            results = self.pico.solve(currdir+"test1.mps", format=ResultsFormat.sol)
            self.fail("test_error1")
        except ValueError:
            pass

    def test_error2(self):
        """ Bad solve option """
        try:
            results = self.pico.solve(currdir+"test1.mps", foo="bar")
            self.fail("test_error2")
        except ValueError:
            pass

    def test_error3(self):
        """ Bad solve option """
        try:
            results = self.pico.solve(currdir+"bad.mps", foo="bar")
            self.fail("test_error3")
        except ValueError:
            pass


class mip_all(mock_all):

    def setUp(self):
        self.do_setup(True)

mip_all = unittest.skipIf(not pico_available, "The PICO solver is not available")(mip_all)

if __name__ == "__main__":
    unittest.main()
