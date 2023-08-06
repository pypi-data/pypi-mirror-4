#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2012 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

# the intent of this module is to provide functions to interface from a 
# PH client to a set of PH solver servers.

import time
from coopr.pyomo import *

from six import iteritems

def extract_weight_maps(ph, scenario_instance):

    # dictionaries of dictionaries. the first key is the parameter name. 
    # the second key is the index for the parameter. the value is the value.
    weights_to_transmit = {}

    for stage in ph._scenario_tree._stages[:-1]: # no blending over the final stage, so no weights to worry about.

        for variable_name, (variable, index_templates) in iteritems(stage._variables):

            # the parameters we are transmitting have a fully populated index set - by
            # construction, there are no unused indices. thus, we can simple extract
            # the values in bulk, with no filtering.
            weight_parameter_name = "PHWEIGHT_"+variable_name
            weight_parameter = scenario_instance.find_component(weight_parameter_name)
            weights_to_transmit[weight_parameter_name] = weight_parameter.extract_values()

    return weights_to_transmit


def transmit_weights(ph):

    start_time = time.time()

    if ph._verbose:
        print("Transmitting instance weights to PH solver servers")

    action_handles = []

    if ph._scenario_tree.contains_bundles():

        for bundle in ph._scenario_tree._scenario_bundles:

            weights_to_transmit = {}  # map from scenario name to the corresponding weight map

            for scenario_name in bundle._scenario_names:

                scenario_instance = ph._instances[scenario_name]

                weights_to_transmit[scenario_name] = extract_weight_maps(ph, scenario_instance)

            action_handles.append( ph._solver_manager.queue(action="load_weights",
                                                            name=bundle._name, 
                                                            new_weights=weights_to_transmit) )

    else:

        for scenario_name, scenario_instance in iteritems(ph._instances):

            action_handles.append( ph._solver_manager.queue(action="load_weights",
                                                            name=scenario_name, 
                                                            new_weights=extract_weight_maps(ph, scenario_instance)) )

    ph._solver_manager.wait_all(action_handles)

    end_time = time.time()

    if ph._output_times:
        print("Weight transmission time=%.2f seconds" % (end_time - start_time))

def extract_xbar_maps(ph, scenario_instance):

    # dictionaries of dictionaries. the first key is the parameter name. 
    # the second key is the index for the parameter. the value is the value.
    xbars_to_transmit = {}

    for stage in ph._scenario_tree._stages[:-1]: # no blending over the final stage, so no xbars to worry about.

        for variable_name, (variable, index_templates) in iteritems(stage._variables):

            # the parameters we are transmitting have a fully populated index set - by
            # construction, there are no unused indices. thus, we can simple extract
            # the values in bulk, with no filtering.
            xbar_parameter_name = "PHXBAR_"+variable_name
            xbar_parameter = scenario_instance.find_component(xbar_parameter_name)
            xbars_to_transmit[xbar_parameter_name] = xbar_parameter.extract_values()
                
    return xbars_to_transmit

def transmit_xbars(ph):

    start_time = time.time()

    if ph._verbose:
        print("Transmitting instance xbars to PH solver servers")

    action_handles = []

    if ph._scenario_tree.contains_bundles():

        for bundle in ph._scenario_tree._scenario_bundles:

            xbars_to_transmit = {}  # map from scenario name to the corresponding xbar map

            for scenario_name in bundle._scenario_names:

                scenario_instance = ph._instances[scenario_name]

                xbars_to_transmit[scenario_name] = extract_xbar_maps(ph, scenario_instance)

            action_handles.append( ph._solver_manager.queue(action="load_xbars", 
                                                            name=bundle._name, 
                                                            new_xbars=xbars_to_transmit) )

    else:

        for scenario_name, scenario_instance in iteritems(ph._instances):

            action_handles.append( ph._solver_manager.queue(action="load_xbars",
                                                            name=scenario_name, 
                                                            new_xbars=extract_xbar_maps(ph, scenario_instance)) )

    ph._solver_manager.wait_all(action_handles)

    end_time = time.time()

    if ph._output_times:
        print("Xbar transmission time=%.2f seconds" % (end_time - start_time))


def initialize_ph_solver_servers(ph):

    start_time = time.time()

    if ph._verbose:
        print("Transmitting initialization information to PH solver servers")

    action_handles = []

    # both the dispatcher queue for initialization and the action name are "initialize" - might be confusing, but hopefully not so much.

    if ph._scenario_tree.contains_bundles():

        for bundle in ph._scenario_tree._scenario_bundles:

            action_handles.append( ph._solver_manager.queue(action="initialize", 
                                                            name="initialize",
                                                            model_directory=ph._model_directory_name, 
                                                            instance_directory=ph._scenario_data_directory_name,
                                                            object_name=bundle._name, 
                                                            solver_type=ph._solver_type,
                                                            solver_io=ph._solver_io,
                                                            scenario_bundle_specification=ph._scenario_bundle_specification,
                                                            create_random_bundles=ph._create_random_bundles,
                                                            scenario_tree_random_seed=ph._scenario_tree_random_seed,
                                                            default_rho=ph._rho, 
                                                            linearize_nonbinary_penalty_terms=ph._linearize_nonbinary_penalty_terms,
                                                            retain_quadratic_binary_terms=ph._retain_quadratic_binary_terms,
                                                            drop_proximal_terms=ph._drop_proximal_terms,
                                                            breakpoint_strategy=ph._breakpoint_strategy,
                                                            integer_tolerance=ph._integer_tolerance,
                                                            verbose=ph._verbose) )
    else:

        for scenario_name in ph._instances:

            action_handles.append( ph._solver_manager.queue(action="initialize", 
                                                            name="initialize",
                                                            model_directory=ph._model_directory_name, 
                                                            instance_directory=ph._scenario_data_directory_name,
                                                            object_name=scenario_name, 
                                                            solver_type=ph._solver_type,
                                                            solver_io=ph._solver_io,
                                                            scenario_bundle_specification=None,
                                                            create_random_bundles=ph._create_random_bundles,
                                                            scenario_tree_random_seed=ph._scenario_tree_random_seed,
                                                            default_rho=ph._rho, 
                                                            linearize_nonbinary_penalty_terms=ph._linearize_nonbinary_penalty_terms,
                                                            retain_quadratic_binary_terms=ph._retain_quadratic_binary_terms,
                                                            drop_proximal_terms=ph._drop_proximal_terms,
                                                            breakpoint_strategy=ph._breakpoint_strategy,
                                                            integer_tolerance=ph._integer_tolerance,
                                                            verbose=ph._verbose) )

    # TBD - realistically need a time-out here - look into possibilities.
    ph._solver_manager.wait_all(action_handles)

    end_time = time.time()

    if ph._output_times:
        print("Initialization transmission time=%.2f seconds" % (end_time - start_time))

#
# a utility to extract the bounds for all variables in an instance.
#

def extract_bounds_map(ph, scenario_instance):

    # a dictionary of dictionaries. the first key is the variable name, the
    # second key is a variable index. the value is a (lb,ub) pair, where None
    # can be supplied for either.
    bounds_to_transmit = {}

    for tree_node in ph._scenario_tree.get_scenario(scenario_instance.name)._node_list:

        for variable_name, variable_indices in iteritems(tree_node._variable_indices):

            bounds_map = bounds_to_transmit.setdefault(variable_name,{})

            variable = scenario_instance.find_component(variable_name)

            for index in variable_indices:
                bounds_map[index] = (value(variable[index].lb), value(variable[index].ub))
            
    return bounds_to_transmit

#
# a utility to transmit - across the PH solver manager - the current rho values for each problem instance. 
#

def transmit_bounds(ph):

    start_time = time.time()

    if ph._verbose:
        print("Transmitting instance variable bounds to PH solver servers")

    action_handles = []

    if ph._scenario_tree.contains_bundles():

        for bundle in ph._scenario_tree._scenario_bundles:

            bounds_to_transmit = {} # map from scenario name to the corresponding bounds map

            for scenario_name in bundle._scenario_names:

                scenario_instance = ph._instances[scenario_name]                    

                bounds_to_transmit[scenario_name] = extract_bounds_map(ph, scenario_instance)

            action_handles.append( ph._solver_manager.queue(action="load_bounds", 
                                                            name=bundle._name, 
                                                            new_bounds=bounds_to_transmit) )

    else:

        for scenario_name, scenario_instance in iteritems(ph._instances):

            action_handles.append( ph._solver_manager.queue(action="load_bounds", 
                                                            name=scenario_name,
                                                            new_bounds=extract_bounds_map(ph, scenario_instance)) )

    ph._solver_manager.wait_all(action_handles)

    end_time = time.time()

    if ph._output_times:
        print("Variable bound transmission time=%.2f seconds" % (end_time - start_time))

#
#
#

def extract_rho_map(ph, scenario_instance):

    # a dictionary of dictionaries. the first key is the variable name.
    # the second key is the index for the particular rho. the value is the rho.
    rhos_to_transmit = {} 

    # TBD: I think we have a problem below with over-riding in situations where a variable is shared 
    #      across multiple stages - we probably need to do some kind of collect. same goes for 
    #      weight/xbar transmission logic above.
    for stage in ph._scenario_tree._stages[:-1]: # no blending over the final stage, so no rhos to worry about.

        for variable_name, (variable, index_templates) in iteritems(stage._variables):

            rho_parameter_name = "PHRHO_"+variable_name
            rho_parameter = scenario_instance.find_component(rho_parameter_name)
            rhos_to_transmit[rho_parameter_name] = rho_parameter.extract_values()

    return rhos_to_transmit

#
# a utility to transmit - across the PH solver manager - the current rho values for each problem instance. 
#

def transmit_rhos(ph):

    start_time = time.time()

    if ph._verbose:
        print("Transmitting instance rhos to PH solver servers")

    action_handles = []

    if ph._scenario_tree.contains_bundles():

        for bundle in ph._scenario_tree._scenario_bundles:

            rhos_to_transmit = {} # map from scenario name to the corresponding rho map

            for scenario_name in bundle._scenario_names:

                scenario_instance = ph._instances[scenario_name]                    

                rhos_to_transmit[scenario_name] = extract_rho_map(ph, scenario_instance)

            action_handles.append( ph._solver_manager.queue(action="load_rhos", 
                                                            name=bundle._name, 
                                                            new_rhos=rhos_to_transmit) )

    else:

        for scenario_name, scenario_instance in iteritems(ph._instances):

            action_handles.append( ph._solver_manager.queue(action="load_rhos", 
                                                            name=scenario_name, 
                                                            new_rhos=extract_rho_map(ph, scenario_instance)) )

    ph._solver_manager.wait_all(action_handles)

    end_time = time.time()

    if ph._output_times:
        print("Rho transmission time=%.2f seconds" % (end_time - start_time))

#
# a utility to transmit - across the PH solver manager - the current scenario
# tree node statistics to each of my problem instances. done prior to each
# PH iteration k.
#

def transmit_tree_node_statistics(ph):

    # NOTE: A lot of the information here is redundant, as we are currently
    #       transmitting all information for all nodes to all solver servers,
    #       rather than information for the tree nodes associated with 
    #       scenarios for which a solver server is responsible.
    

    start_time = time.time()

    if ph._verbose:
        print("Transmitting tree node statistics to PH solver servers")

    action_handles = []

    if ph._scenario_tree.contains_bundles():

        for bundle in ph._scenario_tree._scenario_bundles:

            tree_node_minimums = {}
            tree_node_maximums = {}                

            # iterate over the tree nodes in the bundle scenario tree - but
            # there aren't any statistics there - be careful!
            for bundle_tree_node in ph._scenario_tree._tree_nodes:

                primary_tree_node = ph._scenario_tree._tree_node_map[bundle_tree_node._name]

                tree_node_minimums[primary_tree_node._name] = primary_tree_node._minimums
                tree_node_maximums[primary_tree_node._name] = primary_tree_node._maximums

            action_handles.append( ph._solver_manager.queue(action="load_tree_node_stats", 
                                                            name=bundle._name, 
                                                            new_mins=tree_node_minimums, 
                                                            new_maxs=tree_node_maximums) )

    else:

        for scenario_name in ph._instances:

            tree_node_minimums = {}
            tree_node_maximums = {}

            scenario = ph._scenario_tree._scenario_map[scenario_name]

            for tree_node in scenario._node_list:

                tree_node_minimums[tree_node._name] = tree_node._minimums
                tree_node_maximums[tree_node._name] = tree_node._maximums

            action_handles.append( ph._solver_manager.queue(action="load_tree_node_stats",
                                                            name=scenario_name, 
                                                            new_mins=tree_node_minimums, 
                                                            new_maxs=tree_node_maximums) )

    ph._solver_manager.wait_all(action_handles)

    end_time = time.time()

    if ph._output_times:
        print("Tree node statistics transmission time=%.2f seconds" % (end_time - start_time))

#
# a utility to enable - across the PH solver manager - weighted penalty objectives.
#

def enable_ph_objective_weight_terms(ph):

    if ph._verbose:
        print("Transmitting request to form PH objectives to PH solver servers")

    action_handles = []

    if ph._scenario_tree.contains_bundles():

        for bundle in ph._scenario_tree._scenario_bundles:
            action_handles.append( ph._solver_manager.queue(action="add_ph_objective_weight_terms", 
                                                            name=bundle._name) )
            
    else:

        for scenario_name in ph._instances:
            action_handles.append( ph._solver_manager.queue(action="add_ph_objective_weight_terms", 
                                                            name=scenario_name) )
        
    ph._solver_manager.wait_all(action_handles)

#
# a utility to enable - across the PH solver manager - proximal penalty objectives.
#

def enable_ph_objective_proximal_terms(ph):

    if ph._verbose:
        print("Transmitting request to form PH objectives to PH solver servers")

    action_handles = []

    if ph._scenario_tree.contains_bundles():

        for bundle in ph._scenario_tree._scenario_bundles:
            action_handles.append( ph._solver_manager.queue(action="add_ph_objective_proximal_terms", 
                                                            name=bundle._name) )
            
    else:

        for scenario_name in ph._instances:
            action_handles.append( ph._solver_manager.queue(action="add_ph_objective_proximal_terms", 
                                                            name=scenario_name) )
        
    ph._solver_manager.wait_all(action_handles)

def transmit_fixed_variables(ph):

    start_time = time.time()

    if ph._verbose:
        print("Transmitting fixed variable status to PH solver servers")

    action_handles = []

    if ph._scenario_tree.contains_bundles():

        for bundle in ph._scenario_tree._scenario_bundles:

            fixed_variables_to_transmit = {} # map from scenario name to the corresponding list of fixed variables

            for scenario_name in bundle._scenario_names:

                scenario_instance = ph._instances[scenario_name]                    

                fixed_variables_to_transmit[scenario_name] = ph._problem_states.fixed_variables[scenario_name]

            action_handles.append( ph._solver_manager.queue(action="fix_variables", 
                                                            name=bundle._name, 
                                                            fixed_variables=fixed_variables_to_transmit) )

    else:

        for scenario_name in ph._instances:

            action_handles.append( ph._solver_manager.queue(action="fix_variables", 
                                                            name=scenario_name,
                                                            fixed_variables=ph._problem_states.fixed_variables[scenario_name]) )

    ph._solver_manager.wait_all(action_handles)

    end_time = time.time()

    if ph._output_times:
        print("Fixed variable transmission time=%.2f seconds" % (end_time - start_time))

def transmit_freed_variables(ph):

    start_time = time.time()

    if ph._verbose:
        print("Transmitting freed variable status to PH solver servers")

    action_handles = []

    if ph._scenario_tree.contains_bundles():

        for bundle in ph._scenario_tree._scenario_bundles:

            freed_variables_to_transmit = {} # map from scenario name to the corresponding list of freed variables

            for scenario_name in bundle._scenario_names:

                scenario_instance = ph._instances[scenario_name]                    

                freed_variables_to_transmit[scenario_name] = ph._problem_states.freed_variables[scenario_name]

            action_handles.append( ph._solver_manager.queue(action="free_variables", 
                                                            name=bundle._name, 
                                                            freed_variables=freed_variables_to_transmit) )

    else:

        for scenario_name in ph._instances:

            action_handles.append( ph._solver_manager.queue(action="free_variables", 
                                                            name=scenario_name, 
                                                            freed_variables=ph._problem_states.freed_variables[scenario_name]) )

    ph._solver_manager.wait_all(action_handles)

    end_time = time.time()

    if ph._output_times:
        print("Freed variable transmission time=%.2f seconds" % (end_time - start_time))

#
# load results coming back from the Pyro PH solver server into the input instance.
# the input results are a dictionary of dictionaries, mapping variable name to
# dictionaries the first level; mapping indices to new values at the second level.
#

def load_variable_values(scenario_instance, variable_values):

    for variable_name, values in iteritems(variable_values):
        variable = scenario_instance.find_component(variable_name)
        variable.store_values(values)

#
# a utility to define model-level import suffixes - across the PH solver manager, on all instances.
#

def define_import_suffix(ph, suffix_name):

    if ph._verbose:
        print("Transmitting request to define suffix="+str(suffix_name)+" to PH solver servers")

    action_handles = []

    if ph._scenario_tree.contains_bundles():

        for bundle in ph._scenario_tree._scenario_bundles:
            action_handles.append( ph._solver_manager.queue(action="define_import_suffix", 
                                                            name=bundle._name) )
            
    else:

        for scenario_name in ph._instances:
            action_handles.append( ph._solver_manager.queue(action="define_import_suffix", 
                                                            name=scenario_name, 
                                                            suffix_name = suffix_name) )
        
    ph._solver_manager.wait_all(action_handles)
