#
# Unit Tests for coopr.os
#
#

import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+"/../..")
currdir = dirname(abspath(__file__))+os.sep

from nose.tools import nottest
import coopr.pyomo
import coopr.opt
import coopr.os
import coopr
import xml
import pyutilib.th as unittest
import pyutilib.services

pyutilib.services.TempfileManager.tempdir = currdir

class Test(unittest.TestCase):

    def setUp(self):
        pyutilib.services.TempfileManager.tempdir = currdir
        #
        # Create OSrL object
        #
        self.osrl = coopr.os.OSrL()
        self.reader = coopr.opt.ReaderFactory("osrl")

    def tearDown(self):
        pyutilib.services.TempfileManager.clear_tempfiles()

    def test_read_solution(self):
        soln = self.reader(currdir+"test1.OSrL.xml")
        self.assertEqual(len(soln.solution),1)
        soln.write(filename=currdir+"test_os.txt", format='json')
        self.assertMatchesJsonBaseline(currdir+"test_os.txt", currdir+"test1.txt")

    def test_test2_error(self):
        try:
            self.osrl.read(currdir+"test2.OSrL.xml")
            self.fail("test_test2_error - Failed to find error in test2.OSrL.xml")
        except ValueError:
            pass

    def Xtest_write_osil1 ( self ):
        """Disabled until we can figure out how to perform writes in a deterministic fashion."""
        if not 'osil' in coopr.opt.WriterFactory().services():
            self.skipTest('No OSiL writer is available.')
        base = '%s/test_write_osil1' % currdir
        fout, fbase = (base + '.out', base + '.txt')

        model = coopr.pyomo.AbstractModel()
        model.A = coopr.pyomo.RangeSet(1, 4)
        model.x = coopr.pyomo.Var( model.A, bounds=(-1,1) )
        def obj_rule ( model ):
            return coopr.pyomo.summation( model.x )
        model.obj = coopr.pyomo.Objective( rule=obj_rule )
        instance = model.create()
        instance.write( format=coopr.opt.ProblemFormat.osil, filename=fout)
        self.assertFileEqualsBaseline( fout, fbase )


if __name__ == "__main__":
    unittest.main()
