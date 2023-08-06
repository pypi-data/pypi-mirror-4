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
# Sucasa does not import any modules directly.
#
from coopr.sucasa.ampl_parser import parse_ampl
from coopr.sucasa.symb_info import *
from coopr.sucasa.ampl_info import *


try:
    import pkg_resources
    #
    # Load modules associated with Plugins that are defined in
    # EGG files.
    #
    for entrypoint in pkg_resources.iter_entry_points('coopr.sucasa'):
        plugin_class = entrypoint.load()
except:
    pass
