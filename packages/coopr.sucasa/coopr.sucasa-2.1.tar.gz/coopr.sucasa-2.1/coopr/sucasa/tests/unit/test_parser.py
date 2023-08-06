#
# Unit Tests for ampl_info
#


import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+os.sep+".."+os.sep+"..")
currdir = dirname(abspath(__file__))+os.sep

from nose.tools import nottest
from coopr.sucasa import parse_ampl,MILPSymbInfo
import pyutilib.misc
import pyutilib.th as unittest

class ParserTester(pyutilib.th.TestCase):

    def tearDown(self):
        if os.path.exists(currdir+"parsetab.py"):
            os.remove(currdir+"parsetab.py")
        if os.path.exists(currdir+"parsetab.pyc"):
            os.remove(currdir+"parsetab.pyc")

    def test_parse1(self):
        """Parser empty string"""
        ans = parse_ampl("")
        tmp = str(ans)
        self.assertEqual(tmp,"")

    def test_parse2(self):
        """Parser None"""
        ans = parse_ampl(None)
        self.assertEqual(ans,None)


    def test_parse3(self):
        """Parser simple set"""
        ans = parse_ampl("set a;")
        tmp = str(ans)
        self.assertEqual(tmp,"set a [] None")

    def test_parse4(self):
        """Parser simple param"""
        ans = parse_ampl("param a;")
        tmp = str(ans)
        self.assertEqual(tmp,"param a [] reals")

    def test_parse5(self):
        """Parser simple var"""
        ans = parse_ampl("var a;")
        tmp = str(ans)
        self.assertEqual(tmp,"var a [] None")

    def test_parse6(self):
        """Parser simple objective"""
        ans = parse_ampl("minimize a: 0;")
        tmp = str(ans)
        self.assertEqual(tmp,"min a [] None")

    def test_parse7(self):
        """Parser simple objective"""
        ans = parse_ampl("maximize a: 0;")
        tmp = str(ans)
        self.assertEqual(tmp,"max a [] None")

    def test_parse8(self):
        """Parser simple constraint"""
        ans = parse_ampl("subject to a: 0;")
        tmp = str(ans)
        self.assertEqual(tmp,"con a [] None")


    def test_parse3a(self):
        """Parser indexed set"""
        ans = parse_ampl("set a {b};")
        tmp = str(ans)
        self.assertEqual(tmp,"set a ['b'] None")

    def test_parse4a(self):
        """Parser indexed param"""
        ans = parse_ampl("param a {b};")
        tmp = str(ans)
        self.assertEqual(tmp,"param a ['b'] reals")

    def test_parse5a(self):
        """Parser indexed var"""
        ans = parse_ampl("var a {b};")
        tmp = str(ans)
        self.assertEqual(tmp,"var a ['b'] None")

    def test_parse6a(self):
        """Parser indexed objective"""
        ans = parse_ampl("minimize a {b}: 0;")
        tmp = str(ans)
        self.assertEqual(tmp,"min a ['b'] None")

    def test_parse7a(self):
        """Parser indexed objective"""
        ans = parse_ampl("maximize a {b}: 0;")
        tmp = str(ans)
        self.assertEqual(tmp,"max a ['b'] None")

    def test_parse8a(self):
        """Parser indexed constraint"""
        ans = parse_ampl("subject to a {b}: 0;")
        tmp = str(ans)
        self.assertEqual(tmp,"con a ['b'] None")


    def test_parse3b(self):
        """Parser indexed set"""
        ans = parse_ampl("set a {b,c};")
        tmp = str(ans)
        self.assertEqual(tmp,"set a ['b', 'c'] None")

    def test_parse4b(self):
        """Parser indexed param"""
        ans = parse_ampl("param a {b,c};")
        tmp = str(ans)
        self.assertEqual(tmp,"param a ['b', 'c'] reals")

    def test_parse5b(self):
        """Parser indexed var"""
        ans = parse_ampl("var a {b,c};")
        tmp = str(ans)
        self.assertEqual(tmp,"var a ['b', 'c'] None")

    def test_parse6b(self):
        """Parser indexed objective"""
        ans = parse_ampl("minimize a {b,c}: 0;")
        tmp = str(ans)
        self.assertEqual(tmp,"min a ['b', 'c'] None")

    def test_parse7b(self):
        """Parser indexed objective"""
        ans = parse_ampl("maximize a {b,c}: 0;")
        tmp = str(ans)
        self.assertEqual(tmp,"max a ['b', 'c'] None")

    def test_parse8b(self):
        """Parser indexed constraint"""
        ans = parse_ampl("subject to a {b,c}: 0;")
        tmp = str(ans)
        self.assertEqual(tmp,"con a ['b', 'c'] None")


    def test_parse3c(self):
        """Parser indexed set"""
        ans = parse_ampl("set a {b,c,d};")
        tmp = str(ans)
        self.assertEqual(tmp,"set a ['b', 'c', 'd'] None")

    def test_parse4c(self):
        """Parser indexed param"""
        ans = parse_ampl("param a {b,c,d};")
        tmp = str(ans)
        self.assertEqual(tmp,"param a ['b', 'c', 'd'] reals")

    def test_parse5c(self):
        """Parser indexed var"""
        ans = parse_ampl("var a {b,c,d};")
        tmp = str(ans)
        self.assertEqual(tmp,"var a ['b', 'c', 'd'] None")

    def test_parse6c(self):
        """Parser indexed objective"""
        ans = parse_ampl("minimize a {b,c,d}: 0;")
        tmp = str(ans)
        self.assertEqual(tmp,"min a ['b', 'c', 'd'] None")

    def test_parse7c(self):
        """Parser indexed objective"""
        ans = parse_ampl("maximize a {b,c,d}: 0;")
        tmp = str(ans)
        self.assertEqual(tmp,"max a ['b', 'c', 'd'] None")

    def test_parse8c(self):
        """Parser indexed constraint"""
        ans = parse_ampl("subject to a {b,c,d}: 0;")
        tmp = str(ans)
        self.assertEqual(tmp,"con a ['b', 'c', 'd'] None")


    def test_parse10(self):
        """Parse comments"""
        ans = parse_ampl("# a comment line")
        tmp=str(ans)
        self.assertEqual(tmp,"")
        ans = parse_ampl("# SUCASA SYMBOLS: a b")
        tmp=str(ans)
        self.assertEqual(tmp,"")
        ans = parse_ampl("#SUCASA SYMBOLS: a b")
        tmp=str(ans)
        self.assertEqual(tmp,"")
        ans = parse_ampl("# SUCASA set A")
        tmp=str(ans)
        self.assertEqual(tmp,"set A None None")
        ans = parse_ampl("#SUCASA set a")
        tmp=str(ans)
        self.assertEqual(tmp,"set a None None")

    def test_parse11(self):
        """Parse check statement"""
        ans = parse_ampl("check : i >= 1;")
        tmp=str(ans)
        self.assertEqual(tmp,"")

    def test_parse12(self):
        """Parse comma-separated values for parameter declaration"""
        ans = parse_ampl("param i >= 1, <= 2 := 0;")
        tmp=str(ans)
        self.assertEqual(tmp,"param i [] reals")

    def test_parse13a(self):
        """Parse index declaration that involves a set expression"""
        ans = parse_ampl("param i{ a in A };")
        tmp=str(ans)
        self.assertEqual(tmp,"param i ['A'] reals")

    def test_parse13b(self):
        """Parse index declaration that involves a set expression"""
        ans = parse_ampl("param i{ a in A[j] };")
        tmp=str(ans)
        self.assertEqual(tmp,"param i ['A [ j ]'] reals")

    def test_parse13c(self):
        """Parse index declaration that involves a set expression"""
        ans = parse_ampl("param i{ a in A[j] : a>0 };")
        tmp=str(ans)
        self.assertEqual(tmp,"param i ['A [ j ]'] reals")

    def test_data1(self):
        """Parse data"""
        pyutilib.misc.setup_redirect(currdir+"data1.out")
        ans = parse_ampl("data;",debug=1)
        pyutilib.misc.reset_redirect()
        os.remove(currdir+"data1.out")
        tmp=str(ans)
        self.assertEqual(tmp,"")
        ans = parse_ampl("data; set a := (1,2) (3,4);")
        tmp=str(ans)
        self.assertEqual(tmp,"")

    def test_ampl1(self):
        """Test parser with ampl1.mod"""
        ans = parse_ampl(filename=currdir+"ampl1.mod")
        pyutilib.misc.setup_redirect(currdir+"ampl1.out")
        print(str(ans))
        pyutilib.misc.reset_redirect()
        self.assertFileEqualsBaseline(currdir+"ampl1.out",currdir+"ampl1.txt")

    def test_ampl1_map(self):
        """Test mapfile generation with ampl1.mod"""
        ans = parse_ampl(filename=currdir+"ampl1.mod")
        info = MILPSymbInfo()
        ans.initialize(info)
        info.write_mapfile(filename=currdir+"ampl1.out",quiet=True)
        self.assertFileEqualsBaseline(currdir+"ampl1.out",currdir+"ampl1.map")

    def test_ampl2(self):
        """Test mapfile generation with ampl2.mod"""
        ans = parse_ampl(filename=currdir+"ampl2.mod")
        info = MILPSymbInfo()
        ans.initialize(info)
        info.write_mapfile(filename=currdir+"ampl2.out",quiet=True)
        self.assertFileEqualsBaseline(currdir+"ampl2.out",currdir+"ampl2.map")

    def test_ampl3(self):
        """Test mapfile generation with ampl3.mod"""
        ans = parse_ampl(filename=currdir+"ampl3.mod")
        info = MILPSymbInfo()
        ans.initialize(info)
        info.write_mapfile(filename=currdir+"ampl3.out",quiet=True)
        self.assertFileEqualsBaseline(currdir+"ampl3.out",currdir+"ampl3.map")

    def test_error1(self):
        """Parse empty expression"""
        try:
            ans = parse_ampl(";")
            self.fail("test_error1")
        except IOError:
            pass

    def test_error2(self):
        """Parse illegal character"""
        try:
            ans = parse_ampl("set ^ ;")
            self.fail("test_error2")
        except IOError:
            pass

if __name__ == "__main__":
    unittest.main()
