#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2010 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

from pyutilib.component.core import *
from coopr.pysp import solutionwriter
from coopr.pysp.scenariotree import *

from six import iteritems
#
# a simple utility to munge the index name into something a bit more csv-friendly and
# in general more readable. at the current time, we just eliminate any leading and trailing
# parantheses and change commas to colons - the latter because it's a csv file!
#

def index_to_string(index):

    result = str(index)
    result = result.lstrip('(').rstrip(')')
    result = result.replace(',',':')
    result = result.replace(' ','')

    return result

class CSVSolutionWriter(SingletonPlugin):

    implements (solutionwriter.ISolutionWriterExtension)

    def write(self, scenario_tree, instance_dictionary, output_file_prefix):

        if not isinstance(scenario_tree, ScenarioTree):
            raise RuntimeError("CSVSolutionWriter write method expects ScenarioTree object - type of supplied object="+str(type(scenario_tree)))

        output_filename = output_file_prefix + ".csv"
        output_file = open(output_filename,"w")

        for stage in scenario_tree._stages:
            stage_name = stage._name
            for tree_node in stage._tree_nodes:
                tree_node_name = tree_node._name
                for var_name, var in iteritems(tree_node._solutions):
                    for idx in var:
                        output_file.write(str(stage_name)+" , "+str(tree_node_name)+" , "+str(var_name)+" , "+str(index_to_string(idx))+" , "+str(var[idx].value)+"\n")

        output_file.close()

        print("Scenario tree solution written to file="+output_filename)
