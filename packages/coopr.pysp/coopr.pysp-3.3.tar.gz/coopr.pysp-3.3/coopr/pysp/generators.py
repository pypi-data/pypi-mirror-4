#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2012 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

from six import iteritems

# the intent of this file is to provide a collection of generator (iterables) functions, which
# embody certain highly repeated patterns of nested iteration in PySP. these generators should
# allow for simplification of the code base, and should generally improve maintainability.

# iterates over each stage (minus possibly the last, depending on the keyword arguments),
# each tree node in each stage, each variable in each tree node, and each component of 
# each variable. returns a six-tuple, including:
# - the stage
# - the tree node
# - the variable (Var) object associated with the stage (this is *not* an instance variable).
# - the index of the variable.
# - a boolean indicating whether the variable/index is fixed in all scenario instance.
#   NOTE: We don't actually check for agreement, but we should.
# - a boolean indicating whether the variable/index is stale in all scenario instances.

def scenario_tree_node_variables_generator(scenario_tree, instances, includeLastStage=True):

    if includeLastStage is False:
        stages_to_iterate = scenario_tree._stages[:-1] 
    else:
        stages_to_iterate = scenario_tree._stages

    for stage in stages_to_iterate:

        for variable_name, (variable, index_template) in iteritems(stage._variables):

            for tree_node in stage._tree_nodes:

                # create a cache of all instance variables (with name variable_name) 
                # for scenarios participating in this tree node. avoids excessive calls to
                # the find_component method of a block.
                instance_variables = tuple(((instances[scenario._name].find_component(variable_name), scenario._probability) for scenario in tree_node._scenarios))

                for index in tree_node._variable_indices[variable_name]:

                    # implicit assumption is that if a variable value is fixed / stale in 
                    # one scenario, it is fixed / stale in all scenarios.

                    # until proven otherwise
                    is_stale = False
                    is_fixed = False 

                    instance_fixed_count = 0

                    for instance_variable, scenario_probability in instance_variables:
                        var_value = instance_variable[index]
                        if var_value.stale is True:
                            is_stale = True
                        if var_value.fixed is True:
                            instance_fixed_count += 1
                            is_fixed = True

                    if ((instance_fixed_count > 0) and (instance_fixed_count < len(tree_node._scenarios))):
                        raise RuntimeError("Variable="+variable_name+str(index)+" is fixed in "+str(instance_fixed_count)+" scenarios, which is less than the number of scenarios at tree node="+tree_node._name)
                    
                    yield stage, tree_node, variable, index, is_fixed, is_stale
