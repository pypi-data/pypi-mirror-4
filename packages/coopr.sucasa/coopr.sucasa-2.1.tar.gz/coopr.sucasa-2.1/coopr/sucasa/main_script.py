#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

#
# This defines the 'run()' function, which is the main
# script for sucasa.
#

import re
import sys
import os
from optparse import OptionParser
import traceback

import coopr.sucasa.run_ampl
import pyutilib.subprocess
from coopr.sucasa.ampl_parser import parse_ampl
from coopr.sucasa.symb_info import MILPSymbInfo
import coopr.sucasa.sucasa_PICO


#
#
# Setup command-line options
#
#
parser = OptionParser()
parser.add_option("-k","--keepfiles",
        help="Keep temporary files",
        action="store_true",
        dest="keepfiles",
        default=False)
parser.add_option("--acro",
        help="The directory of the acro installation that will be used to build the customized PICO optimizer.",
        action="store",
        dest="acro",
        default="../..")
parser.add_option("--name",
        help="The name of the customized solver application",
        action="store",
        dest="name",
        default=None)
parser.add_option("-v","--verbose",
        help="Make output verbose",
        action="store_true",
        dest="verbose",
        default=False)
parser.add_option("-q","--quiet",
        help="Make output quiet",
        action="store_true",
        dest="quiet",
        default=False)
parser.add_option("-p","--parse",
        help="Parse the AMPL *.mod file, and return immediately",
        action="store_true",
        dest="only_parse",
        default=False)
parser.add_option("-m","--keep-mapfile",
        help="Keep the mapfile, if it already exists",
        action="store_false",
        dest="overwrite_mapfile",
        default=True)
parser.add_option("--mps",
        help="When specified, SUCASA writes the MILP instances to an MPS file.  By default, it writes an NL file",
        action="store_true",
        dest="using_mps",
        default=False)
parser.add_option("--protected-vars",
        help="If this flag is not specified, then the symbols for the variables and arguments are included in the PICO application classes, which may cause symbol conflicts with existing PICO data.  This flag ensures that no symbol classes will occur.",
        action="store_true",
        dest="protected",
        default=False)
parser.add_option("--without-presolve",
        help="Disables presolving in AMPL",
        action="store_false",
        dest="presolve",
        default=True)
parser.add_option("--without-main",
        help="By default, sucasa includes a main() function in the <app>MILP.cpp file.  This option excludes the main() function.",
        action="store_false",
        dest="main",
        default=True)
parser.add_option("--solver-options",
        help="Options for the solver run by SUCASA",
        action="store",
        dest="solver_options",
        default="")
parser.add_option("-g","--generate",
        help="Generate the customized IP source files",
        action="store_true",
        dest="generate",
        default=False)
parser.add_option("-a","--ampl-only",
        help="Generate the AMPL script, but terminate without calling AMPL.",
        action="store_true",
        dest="ampl",
        default=False)
parser.add_option("-i","--instance-only",
        help="Generate a problem instance, and then terminate without calling PICO.",
        action="store_true",
        dest="instance",
        default=False)
parser.add_option("--np",
        help="Launch PICO with mpirun if this is specified",
        action="store",
        dest="np",
        default=0)
parser.usage="sucasa [options] <model.mod> [<model.dat>]"
parser.description="A utility to generate a customized the PICO integer programming solver that uses application-specific symbolic mapping of the set, parameter, variable and constraint names into the actual data used by the application."
parser.epilog="""By default, sucasa will extract the variable, objective and constraint names from the AMPL model, and these symbols will be exported to the customized PICO optimizer.  Additionally, sucasa will also export set and parameter symbols declared on lines that contain "SUCASA SYMBOLS".
"""


def run(args=None):
    #
    #
    # Parse command-line options
    #
    #
    (options, args) = parser.parse_args(args=args)
    print("Running SUCASA")
    #
    # Process arguments
    #
    if options.quiet and options.verbose:
        print("ERROR: cannot have both verbose and quiet output!")
        return
    if len(args) == 0:
        print("ERROR: expected AMPL model file!")
        print("")
        parser.print_help()
        return
    if len(args) > 2:
        print("ERROR: expect one or two arguments!")
        print("Arguments: " + " ".join(args))
        return
    if options.name is None:
        (path,filename) = os.path.split(args[0])
        (basename,ext) = os.path.splitext(filename)
        options.name = basename
    if "-" in options.name:
        print("  WARNING: replacing '-' in application name with '_'")
        options.name = "_".join(options.name.split('-'))

    #
    # Parse model file, and generate customized solver
    #
    parse_info = None
    print("  . Parsing AMPL model '"+args[0]+"'")
    try:
        if options.verbose:
            debug=100
        else:
            debug=0
        parse_info = parse_ampl(filename=args[0],debug=debug)
    except IOError:
        err = sys.exc_info()[1]
        print("      Error parsing file "+args[0])
        print("      "+str(err))
        return
    #
    # Print parser info and return
    #
    if options.only_parse:
        print("SUCASA Parse Info")
        print(str(parse_info))
        return
    #
    # Setup the symbolic information class
    #
    print("  . Processing model information")
    symbolic_info = MILPSymbInfo()
    symbolic_info.name = options.name
    symbolic_info.verbose = options.verbose
    try:
        parse_info.initialize(symbolic_info)
    except IOError:
        err = sys.exc_info()[1]
        print("Caught an IO exception: "+str(err))
        return

    #
    # Generate the customized solver
    #
    if options.generate:
        #
        # Write the *.map file and source files
        #
        if options.overwrite_mapfile or not os.path.exists(symbolic_info.name+".map"):
            filename = symbolic_info.write_mapfile()
            print("  . Created mapfile '"+filename+"'")
        else:
            print("  . Using existing mapfile: "+symbolic_info.name+".map")
            symbolic_info = MILPSymbInfo()
            symbolic_info.name = options.name
            symbolic_info.read_mapfile(symbolic_info.name+".map")
            #
            # Perform consistency check between symbolic_info and parse_info
            #
            if parse_info.check(symbolic_info):
                print("      Consistency check with parse information is OK")
            else:
                print("      Consistency check with parse information has FAILED!")
                return
            parse_info.update_exports()
        #
        # Generate source files
        #
        print("  . Generating source code for customized optimizer:")
        symb_files = symbolic_info.generate_milp_symbol_code()
        opt_files = sucasa_PICO.create_customized_files(app_label=symbolic_info.name, create_main=options.main, protected=options.protected, acro_dir=options.acro)
        for file in symb_files+opt_files:
            print("      "+file)
        return

    #
    # Apply the customized solver to a dataset
    #
    (path,filename) = os.path.split(args[0])
    (basename,ext) = os.path.splitext(filename)
    if ext != ".mod":
        print("ERROR: Expecting first argument to be an AMPL model: "+args[0])
        return
    if len(args)==2:
        (path,filename) = os.path.split(args[1])
        (basename,ext) = os.path.splitext(filename)
        if ext != ".dat":
            print("ERROR: Expecting second argument to be an AMPL data file: "+args[1])
            return
        datafile=args[1]
    else:
        datafile=None
    #
    # Run AMPL
    #
    try:
        symbols=[]
        for item in parse_info.items:
            if item[0] in ("set","param") and parse_info.concrete[item[1]] and ('*' in parse_info.exported_symbols or item[1] in parse_info.exported_symbols):
                symbols.append(item[1])
        run_ampl.run_ampl(symbols=symbols, app_label=options.name, model_file=args[0], data_file=datafile, presolve=options.presolve, keepfiles=options.keepfiles, using_mps=options.using_mps, only_script=options.ampl)
    except IOError:
        err = sys.exc_info()[1]
        print("      "+str(err))
        return
    if options.ampl:
        print("  . Terminated after generating AMPL script")
        return
    #
    # Run PICO
    #
    if not options.instance:
        cmd=""
        if options.np > 0:
            cmd = "mpirun -np "+str(options.np)+" "
        else:
            cmd = "./"
        cmd+="PICO_"+options.name+" "+options.solver_options+" "+options.name
        if options.using_mps:
            cmd += ".mps"
        else:
            cmd += ".nl"
        print("  . PICO Command: "+cmd)
        sys.stdout.write("  . Running PICO ...")
        pyutilib.subprocess.run(cmd,"PICO.out")
        sys.stdout.write("done.")
        if options.quiet:
            print("    Output in file 'PICO.out'")
        else:
            INPUT = open("PICO.out")
            for line in INPUT:
                sys.stdout.write(line)
            INPUT.close()

def main():
    if sys.version_info[0:2] < (2,4):
        print("")
        print("ERROR: Pyomo requires Python 2.4 or newer")
        sys.exit(1)
    from os.path import abspath, dirname
    sys.path.append(".")
    run()
