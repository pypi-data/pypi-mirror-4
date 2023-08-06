#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

import pyutilib.component.core

pyutilib.component.core.PluginGlobals.push_env( "coopr.pysp" )

import coopr.pysp.log_config
#import coopr.pysp.log_config as _config_
from coopr.pysp.scenariotree import *
from coopr.pysp.convergence import *
from coopr.pysp.ph import *
from coopr.pysp.phextension import *
from coopr.pysp.phutils import *
from coopr.pysp.ef import *
from coopr.pysp.ef_writer_script import *
from coopr.pysp.phinit import *
from coopr.pysp.phobjective import *
from coopr.pysp.solutionwriter import *
from coopr.pysp.phsolverserverutils import *

pyutilib.component.core.PluginGlobals.pop_env()

try:
    import pkg_resources
    #
    # Load modules associated with Plugins that are defined in
    # EGG files.
    #
    for entrypoint in pkg_resources.iter_entry_points('coopr.pysp'):
        plugin_class = entrypoint.load()
except:
    pass
