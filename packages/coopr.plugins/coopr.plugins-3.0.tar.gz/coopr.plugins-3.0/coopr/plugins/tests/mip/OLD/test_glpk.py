#
# Unit Tests for coopr.plugins.mip.GLPK
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
    glpk = coopr.plugins.mip.GLPK(keepfiles=True)
    glpk_available= (not glpk.executable() is None)
except IOError:
    glpk_available=False
    pass
except pyutilib.common.ApplicationError:
    glpk_available=False
    pass

try:
    pico_convert =  pyutilib.services.registered_executable("pico_convert")
    pico_convert_available= (not pico_convert is None)
except pyutilib.common.ApplicationError:
    pico_convert_available=False



class mock_all(unittest.TestCase):

    def setUp(self):
        self.do_setup(False)
        pyutilib.services.TempfileManager.tempdir = currdir

    def do_setup(self,flag):
        if flag:
            self.glpk = coopr.plugins.mip.GLPK(keepfiles=True)
        else:
            self.glpk = coopr.plugins.mip.MockGLPK(keepfiles=True)
        self.glpk.suffixes=['.*']

    def tearDown(self):
        if os.path.exists(currdir+"glpk.soln"):
            os.remove(currdir+"glpk.soln")
        pyutilib.services.TempfileManager.clear_tempfiles()

    def test_path(self):
        """ Verify that the GLPK path is what is expected """
        if type(self.glpk) is 'GLPK':
            self.failUnlessEqual(self.glpk.executable.split(os.sep)[-1],"GLPK"+coopr.util.executable_extension)

    def test_solve1(self):
        """ Test GLPK - test1.mps """
        results = self.glpk.solve(currdir+"test1.mps",logfile=currdir+"test_solve1.log", solnfile=currdir+"test1.soln")
        results.write(filename=currdir+"test_solve1.txt", times=False)
        self.failUnlessFileEqualsBaseline(currdir+"test_solve1.txt", currdir+"test1_glpk.txt")
        os.remove(currdir+"test_solve1.log")
        os.remove(currdir+"test1.soln")

    def test_solve2a(self):
        """ Test GLPK - test1.mps """
        results = self.glpk.solve(currdir+"test1.mps", rformat=ResultsFormat.soln, logfile=currdir+"test_solve2a.log", solnfile=currdir+"test1.soln")
        results.write(filename=currdir+"test_solve2a.txt", times=False)
        self.failUnlessFileEqualsBaseline(currdir+"test_solve2a.txt", currdir+"test1_glpk.txt")
        os.remove(currdir+"test_solve2a.log")
        os.remove(currdir+"test1.soln")

    def test_solve2b(self):
        """ Test GLPK - test1.mps """
        results = self.glpk.solve(currdir+"test1.mps", pformat=ProblemFormat.mps, rformat=ResultsFormat.soln, logfile=currdir+"test_solve2b.log", solnfile=currdir+"test1.soln")
        results.write(filename=currdir+"test_solve2b.txt", times=False)
        self.failUnlessFileEqualsBaseline(currdir+"test_solve2b.txt", currdir+"test1_glpk.txt")
        os.remove(currdir+"test_solve2b.log")
        os.remove(currdir+"test1.soln")

    def test_solve3(self):
        """ Test GLPK - test2.lp """
        results = self.glpk.solve(currdir+"test2.lp", logfile=currdir+"test_solve3.log", solnfile=currdir+"test2.soln")
        results.write(filename=currdir+"test_solve3.txt", times=False)
        self.failUnlessFileEqualsBaseline(currdir+"test_solve3.txt", currdir+"test2_glpk.txt")
        os.remove(currdir+"test_solve3.log")
        os.remove(currdir+"test2.soln")

    def test_solve4(self):
        """ Test GLPK - test4.nl """
        if pico_convert_available:
            results = self.glpk.solve(currdir+"test4.nl", rformat=ResultsFormat.soln, logfile=currdir+"test_solve4.log")
            results.write(filename=currdir+"test_solve4.txt",times=False)
            self.failUnlessFileEqualsBaseline(currdir+"test_solve4.txt", currdir+"test4_glpk.txt")
            #os.remove(currdir+"test4.soln")
            os.remove(currdir+"test_solve4.log")
        else:
            try:
                results = self.glpk.solve(currdir+"test4.nl", rformat=ResultsFormat.soln, logfile=currdir+"test_solve4.log")
            except coopr.opt.ConverterError:
                pass


    def Xtest_solve5(self):
        """ Test GLPK - test5.mps """
        results = self.glpk.solve(currdir+"test5.mps", rformat=ResultsFormat.soln, logfile=currdir+"test_solve5.log", solnfile=currdir+"test5.soln",timelimit=300)
        self.failUnlessEqual(results.solution(0).status, coopr.opt.SolutionStatus.bestSoFar)
        os.remove(currdir+"test_solve5.log")
        os.remove(currdir+"test5.soln")

    def test_diet(self):
        """ Test GLPK - diet.mod """
        results = self.glpk.solve(currdir+"diet.mod", logfile=currdir+"test_diet.log", solnfile=currdir+"diet.soln")
        results.write(filename=currdir+"test_diet.txt", times=False)
        self.failUnlessFileEqualsBaseline(currdir+"test_diet.txt", currdir+"diet_glpk.txt")
        os.remove(currdir+"test_diet.log")
        if os.path.exists(currdir+"ipconvert.lp"):
            os.remove(currdir+"ipconvert.lp")
        os.remove(currdir+"diet.soln")

    #
    # This test is disabled, but it's useful for interactively exercising
    # the option specifications of a solver
    #
    def Xtest_options(self):
        """ Test GLPK options behavior """
        results = self.glpk.solve(currdir+"bell3a.mps", logfile=currdir+"test_options.log", options="maxCPUMinutes=0.1 foo=1 bar='a=b c=d' zz=yy")
        results.write(filename=currdir+"test_options.txt",times=False)
        self.failUnlessFileEqualsBaseline(currdir+"test_options.txt", currdir+  "test4_glpk.txt")
        #os.remove(currdir+"test4.sol")
        #os.remove(currdir+"test_solve4.log")

    def Xtest_error1(self):
        """ Bad results format """
        try:
            results = self.glpk.solve(currdir+"test1.mps", rformat=ResultsFormat.sol)
            self.fail("test_error1")
        except ValueError:
            pass

    def test_error2(self):
        """ Bad solve option """
        try:
            results = self.glpk.solve(currdir+"test1.mps", foo="bar")
            self.fail("test_error2")
        except ValueError:
            pass

    def test_error3(self):
        """ Bad solve option """
        try:
            results = self.glpk.solve(currdir+"bad.mps", foo="bar")
            self.fail("test_error3")
        except ValueError:
            pass


class mip_all(mock_all):

    def setUp(self):
        self.do_setup(True)

    def test_solve1a(self):
        """ Test GLPK - test1.mps """
        results = self.glpk.solve(currdir+"test1.mps")
        results.write(filename=currdir+"test_solve1.txt", times=False)
        self.failUnlessFileEqualsBaseline(currdir+"test_solve1.txt", currdir+"test1_glpk.txt")
        if os.path.exists(currdir+"glpk.log"):
            os.remove(currdir+"glpk.log")
        if os.path.exists(currdir+"glpk.soln"):
            os.remove(currdir+"glpk.soln")

mip_all = unittest.skipIf(not glpk_available, "The 'glpsol' command is not available")(mip_all)

if __name__ == "__main__":
    unittest.main()
