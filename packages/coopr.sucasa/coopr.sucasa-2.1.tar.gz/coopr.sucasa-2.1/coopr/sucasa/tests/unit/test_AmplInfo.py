#
# Unit Tests for ampl_info
#


import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+os.sep+".."+os.sep+"..")
currdir = dirname(abspath(__file__))+os.sep

import pyutilib.misc
import pyutilib.th as unittest
from nose.tools import nottest
from coopr.sucasa.ampl_info import AmplInfo
from coopr.sucasa.symb_info import MILPSymbInfo

class AmplInfoTester(unittest.TestCase):

    def setUp(self):
        self.info = AmplInfo()

    def test_add(self):
        """Check that add inserts the appropriate information"""
        self.info.add('con','f',['a'])
        self.info.add('param','b',['a'])
        self.info.add('var','c',['a','a'])
        self.info.add('min','d',['a'])
        self.info.add('set','a',[])
        self.info.add('max','e',['a','a'])
        tmp = str(self.info)
        target = "con f ['a'] None\nparam b ['a'] None\nvar c ['a', 'a'] None\nmin d ['a'] None\nset a [] None\nmax e ['a', 'a'] None"
        self.assertEqual(tmp,target)
        #
        # Check order of the insertions
        #
        tmp=[]
        for i in self.info:
            tmp.append(i[1])
        self.assertEqual(tmp,['f','b','c','d','a','e'])

    def test_initialize1(self):
        """ Check that initialize correctly fills a SymbInfo object"""
        self.info.add('con','f',['a'])
        self.info.add('param','b',['a'])
        self.info.add('var','c',['a','a'])
        self.info.add('min','d',['a'])
        self.info.add('set','a1',[])
        self.info.add('set','a2',[],superset=['a1','a1'], dimen=2)
        self.info.add('max','e',['a','a'])
        #
        # Initialize a SymbInfo object
        #
        sinfo = MILPSymbInfo()
        self.info.initialize(sinfo,quiet=True)
        pyutilib.misc.setup_redirect(currdir+"initialize1.out")
        print(str(sinfo))
        pyutilib.misc.reset_redirect()
        self.assertFileEqualsBaseline(currdir+"initialize1.out",currdir+"initialize1.txt")

    def test_initialize2(self):
        """ Check that initialize correctly fills a SymbInfo object, when all symbols are exported"""
        self.info.add('con','f',['a'])
        self.info.add('param','b',['a'])
        self.info.add('var','c',['a','a'])
        self.info.add('min','d',['a'])
        self.info.add('set','a1',[])
        self.info.add('set','a2',[],superset=['a1','a1'], dimen=2)
        self.info.add('max','e',['a','a'])
        self.info.exported_symbols.add("*")
        #
        # Initialize a SymbInfo object
        #
        sinfo = MILPSymbInfo()
        self.info.initialize(sinfo,quiet=True)
        pyutilib.misc.setup_redirect(currdir+"initialize2.out")
        print(str(sinfo))
        pyutilib.misc.reset_redirect()
        self.assertFileEqualsBaseline(currdir+"initialize2.out",currdir+"initialize2.txt")

    def test_initialize3(self):
        """ Check that initialize correctly fills a SymbInfo object, when symbols are defined by SUCASA declarations"""
        self.info.add_mapfile_declaration("a","set a within literals dimen 1")
        self.info.add('set','a',[])
        self.info.add('con','f',['a'])
        self.info.add_mapfile_declaration("b","param b[a] in literals")
        self.info.add('param','b',['a'])
        self.info.add('var','c',['a','a'])
        self.info.add('min','d',['a'])
        self.info.add_mapfile_declaration("a2","set a2 within literals cross a dimen 2")
        self.info.add('set','a2',[],superset=['a1','a1'], dimen=2)
        self.info.add('max','e',['a','a'])
        self.info.exported_symbols.add("a")
        self.info.exported_symbols.add("b")
        self.info.exported_symbols.add("a2")
        #
        # Initialize a SymbInfo object
        #
        sinfo = MILPSymbInfo()
        self.info.initialize(sinfo,quiet=True)
        pyutilib.misc.setup_redirect(currdir+"initialize3.out")
        print(str(sinfo))
        pyutilib.misc.reset_redirect()
        self.assertFileEqualsBaseline(currdir+"initialize3.out",currdir+"initialize3.txt")

    def test_initialize_err1(self):
        """ Check that initialize correctly identifies an invalid exported symbol"""
        self.info.add('con','f',['a'])
        self.info.add('param','b',['a'])
        self.info.add('var','c',['a','a'])
        self.info.add('min','d',['a'])
        self.info.add('set','a1',[])
        self.info.add('set','a2',[],superset=['a1','a1'], dimen=2)
        self.info.add('max','e',['a','a'])
        self.info.exported_symbols.add("a1")
        self.info.exported_symbols.add("b1")
        #
        # Initialize a SymbInfo object
        #
        sinfo = MILPSymbInfo()
        try:
            pyutilib.misc.setup_redirect(currdir+"initialize_err1.out")
            self.info.initialize(sinfo,quiet=True)
            pyutilib.misc.reset_redirect()
            self.fail("Expected IOError")
        except IOError:
            pyutilib.misc.reset_redirect()
            os.remove(currdir+"initialize_err1.out")

    def test_check(self):
        self.info.add('set','a',[])
        self.info.add('set','a1',[])
        self.info.add('set','a2',[],superset=['a1','a1'], dimen=2)
        self.info.add('param','b',['a'])
        self.info.add('var','c',['a','a'])
        self.info.add('min','d',['a'])
        self.info.add('max','e',['a','a'])
        self.info.add('con','f',['a'])
        self.info.exported_symbols.add("a")
        self.info.exported_symbols.add("a1")
        self.info.exported_symbols.add("a2")
        self.info.exported_symbols.add("b")
        sinfo = MILPSymbInfo()
        self.info.initialize(sinfo,quiet=True)
        self.info.check(sinfo)
        #
        # Create errors
        #
        sinfo.add_symbol('param','SXb')
        sinfo.add_symbol('set','Xa')
        sinfo.add_symbol('param','Xb')
        sinfo.add_symbol('var','Xc')
        sinfo.add_symbol('min','Xd')
        sinfo.add_symbol('max','Xe')
        sinfo.add_symbol('con','Xf')
        pyutilib.misc.setup_redirect(currdir+"check.out")
        self.info.check(sinfo)
        pyutilib.misc.reset_redirect()
        self.assertFileEqualsBaseline(currdir+"check.out",currdir+"check.txt")

if __name__ == "__main__":
    unittest.main()
