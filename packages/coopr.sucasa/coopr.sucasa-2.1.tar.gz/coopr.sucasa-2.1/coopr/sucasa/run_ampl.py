#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________


import os
from string import Template
import pyutilib.subprocess


ampl_script=Template("""
##
## AMPL script that creates ${app_label}.nl (or ${app_label}.mps),
## ${app_label}.col, ${app_label}.row and ${app_label}.val
##
## The output of this script is used to create ${app_label}.val
##
#
# Read in the model and data files
#
model ${model_file} ;
${data_line}
#
# Tells ampl to create *.row and *.col files
#
option auxfiles rc;
#
# Manage whether AMPL preprocesses the model.
#
option presolve ${presolve};
#
# Write out an *.nl or *.mps file
#
write ${file_type}${app_label};
#
# Print end-of-job tag
#
print "# SUCCESSFUL_TERMINATION";
""")


def run_ampl(symbols=[], app_label="undefined", model_file="undefined", data_file="undefined", presolve=0, keepfiles=False, using_mps=False, only_script=False):
    """
    Run AMPL on a customized script
    """
    print("  . Running AMPL to generate application instance")
    if using_mps is False:
        file_type="b"
    else:
        file_type="m"
    if presolve == True:
        presolve=1
    elif presolve == False:
        presolve=0
    if data_file is None:
        data_line="#"
    else:
        data_line=" data "+data_file+";"
    cmd = ampl_script.substitute(app_label=app_label, model_file=model_file, data_line=data_line, presolve=presolve, file_type=file_type)
    for symbol in symbols:
        cmd += "print \""+symbol+"\";"
        cmd += "_display "+symbol+";"
        cmd += "print \";\";"
    OUTPUT=open("ampl_script.in","w")
    OUTPUT.write(cmd+'\n')
    OUTPUT.close()
    #
    # Return if the script does not need to be executed
    #
    if only_script:
        return
    #
    # Run AMPL
    #
    sys.stdout.write("  . Running AMPL ...")
    pyutilib.subprocess.run("ampl ampl_script.in",app_label+".val")
    sys.stdout.write("done.\n")
    #
    # Check for errors
    #
    errmsg="      SUCASA ran 'ampl ampl_script.in', and the output is in '"+app_label+".val'"
    if not "SUCCESSFUL_TERMINATION" in file(app_label+".val").read():
        print(errmsg)
        raise IOError("ERROR: sucasa called AMPL, which failed to terminate successfully!")
    if "Error executing" in file(app_label+".val").read():
        print(errmsg)
        raise IOError("ERROR: sucasa called AMPL, which had an error executing a command!")
    if using_mps:
        if not os.path.exists(app_label+".mps"):
            print(errmsg)
            raise IOError("ERROR: sucasa failed to generate MPS file for "+app_label+" using AMPL!")
    elif not os.path.exists(app_label+".nl"):
        print(errmsg)
        raise IOError("ERROR: sucasa failed to generate NL file for "+app_label+" using AMPL!")
    if not keepfiles:
        os.remove("ampl_script.in")
