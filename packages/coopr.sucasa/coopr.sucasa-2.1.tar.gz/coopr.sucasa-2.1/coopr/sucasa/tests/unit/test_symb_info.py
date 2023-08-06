#
# Unit Tests for MILPSymbInfo
#


import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+os.sep+".."+os.sep+"..")
currdir = dirname(abspath(__file__))+os.sep

from nose.tools import nottest
from coopr.sucasa import parse_mapfile,MILPSymbInfo
import pyutilib.misc
import pyutilib.th as unittest

class ParseMapFileTester(unittest.TestCase):

    def setUp(self):
        self.info = MILPSymbInfo()

    def tearDown(self):
        if os.path.exists(currdir+"parsetab.py"):
            os.remove(currdir+"parsetab.py")
        if os.path.exists(currdir+"parsetab.pyc"):
            os.remove(currdir+"parsetab.pyc")
        del self.info

    def test_parse1(self):
        """Parser empty string"""
        ans = parse_mapfile(self.info, "")
        tmp = str(ans)
        self.assertEqual(tmp,"")

    def test_parse2(self):
        """Parser None"""
        ans = parse_mapfile(self.info, None)
        self.assertEqual(ans,None)

    def test_parse3(self):
        """Parser sucasa1.map"""
        ans = parse_mapfile(self.info, filename=currdir+"sucasa1.map")
        pyutilib.misc.setup_redirect(currdir+"sucasa1.out")
        ans.print_symbols()
        pyutilib.misc.reset_redirect()
        self.assertFileEqualsBaseline(currdir+"sucasa1.out",currdir+"sucasa1.txt")

    def test_mapfile_io(self):
        """Read/write mapfile correctly"""
        ans = parse_mapfile(self.info, filename=currdir+"sucasa1.map")
        ans.write_mapfile(currdir+"tmp.map",quiet=True)
        self.assertFileEqualsBaseline(currdir+"tmp.map",currdir+"sucasa1.map")
        self.info = MILPSymbInfo(currdir+"tmp")
        self.info.read_mapfile(currdir+"sucasa1.map")
        self.info.write_mapfile(quiet=True)
        self.assertFileEqualsBaseline(currdir+"tmp.map",currdir+"sucasa1.map")
        self.info = MILPSymbInfo(currdir+"sucasa1")
        self.info.read_mapfile()
        self.info.write_mapfile(currdir+"tmp.map",quiet=True)
        self.assertFileEqualsBaseline(currdir+"tmp.map",currdir+"sucasa1.map")

    def test_add1(self):
        """Add symbols directly, and verify that they are created"""
        self.info.add_symbol("set","a",dimen=0)
        self.info.add_symbol("set","b",index=['A','B'],tmpsets=True)
        self.info.add_symbol("set","c",index=['x in W','B'],tmpsets=True,quiet=True)
        self.info.add_symbol("set","d",index=['x in W'],superset=["a","b"],tmpsets=True,dimen=2)
        self.info.write_mapfile(currdir+"add1.out",quiet=True)
        self.assertFileEqualsBaseline(currdir+"add1.out",currdir+"add1.map")

    def test_generate(self):
        """Generate PICO wrapper code"""
        self.info.name = currdir+"generate"
        self.info.read_mapfile(filename=currdir+"sucasa1.map")
        self.info.generate_milp_symbol_code()
        os.remove(currdir+"generate_info.h")
        os.remove(currdir+"generate_info.cpp")

    def test_error1(self):
        """Parse empty expression"""
        try:
            ans = parse_mapfile(self.info,";")
            self.fail("test_error1")
        except IOError:
            pass

    def test_error2(self):
        """Parse duplicate declarations"""
        try:
            pyutilib.misc.setup_redirect(currdir+"error2.out")
            ans = parse_mapfile(self.info,"set a within integers dimen 1;\nset a within integers dimen 1;")
            self.fail("test_error2")
        except IOError:
            pass
        pyutilib.misc.reset_redirect()
        os.remove(currdir+"error2.out")

    def test_error3(self):
        """Read non-existent mapfile"""
        try:
            self.info.read_mapfile("unknown.map")
            self.fail("test_error3")
        except IOError:
            pass

    def test_error4(self):
        """Verify that an error occurs if you add an unknown index"""
        try:
            self.info.add_symbol("set","a",index=['A'],dimen=0,quiet=True)
            self.fail("test_error4")
        except IOError:
            pass

    def test_error5(self):
        """Verify that an error occurs if you specify a bad superset"""
        try:
            self.info.add_symbol("set","a",superset="A")
            self.fail("test_error5")
        except IOError:
            pass

    def test_error6(self):
        """Verify that an error occurs if you specify a bad superset list"""
        try:
            self.info.add_symbol("set","a",superset=["A","B"])
            self.fail("test_error6")
        except IOError:
            pass

if __name__ == "__main__":
    unittest.main()
