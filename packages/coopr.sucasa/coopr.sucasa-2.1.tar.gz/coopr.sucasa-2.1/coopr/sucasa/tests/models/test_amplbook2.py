#
# Unit Tests for complete examples
#

import os
import sys
from os.path import abspath, dirname
topdir = dirname(dirname(abspath(__file__)))+os.sep+".."+os.sep+".."
sys.path.insert(0, topdir)
currdir = dirname(abspath(__file__))+os.sep

from coopr.sucasa import parse_mapfile,MILPSymbInfo,parse_ampl
import pyutilib.misc
import pyutilib.th as unittest
import glob

#
# Test class
#
class TestAmplbook2(unittest.TestCase): pass
#
# The directory with the test data
#
data_dir=topdir+os.sep+"example"+os.sep+"pyomo"+os.sep+"amplbook2"+os.sep
#
# Function used to generate a *.map output file, which is compared against a baseline
#
def create_map(name):
    prefix=data_dir+name
    pyutilib.misc.setup_redirect(prefix+".out")
    ans = parse_ampl(filename=data_dir+name+".mod")
    sinfo = MILPSymbInfo()
    ans.exported_symbols.add("*")
    ans.initialize(sinfo,quiet=True)
    sinfo.write_mapfile(prefix+".out.map")
    pyutilib.misc.reset_redirect()
    return [prefix+".out.map",[prefix+".out"]]
#
# Iterate over all files to populate the test class
#
files = glob.glob(data_dir+"*.mod")
for file in files:
    bname=os.path.basename(file)
    name=bname.split('.')[0]
    TestAmplbook2.add_baseline_test(fn=create_map, baseline=data_dir+name+".map", name=name)

#
# Execute tests when run from the command line
#
if __name__ == "__main__":
    unittest.main()
