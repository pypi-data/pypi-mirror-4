
#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

import sys
import random

from math import fabs, ceil

from coopr.pyomo import *
from coopr.pysp.phutils import *

from six import iterkeys, iteritems, itervalues, advance_iterator
from six.moves import xrange


class ScenarioTreeNode(object):

    #
    # initialize the _solutions attribute of a tree node, from scratch.
    #

    def _initialize_solution_map(self, scenario_instance_map):

        # clear whatever was there before.
        self._solutions = {}

        # NOTE: Given the expense, this should really be optional - don't
        #       construct unless we're actually going to use!
        # for each variable referenced in the stage, clone the variable
        # for purposes of storing solutions. we are being wasteful in
        # terms copying indices that may not be referenced in the stage.
        # this is something that we might revisit if space/performance
        # is an issue (space is the most likely issue)
        for variable_name in self._stage._variables:
            self._solutions[variable_name] = dict((index,None) for index in self._variable_indices[variable_name])

        self._solution_map_initialized = True


    """ Constructor
    """
    def __init__(self, name, conditional_probability, stage, initialize_solution=False, scenario_instance_map=None):

        self._name = name
        self._stage = stage
        self._parent = None
        self._children = [] # a collection of ScenarioTreeNodes
        self._conditional_probability = conditional_probability # conditional on parent
        self._scenarios = [] # a collection of all Scenarios passing through this node in the tree
        self._variable_indices = {} # a map from a variable name to the indices blended at this node.

        # general use statistics for the variables at each node.
        # each attribute is a map between the variable name and a
        # parameter (over the same index set) encoding the corresponding
        # statistic computed over all scenarios for that node. the
        # parameters are named as the source variable name suffixed
        # by one of: "NODEMIN", "NODEAVG", and "NODEMAX".
        # NOTE: the averages are probability_weighted - the min/max
        #       values are not.
        # NOTE: the parameter names are basically irrelevant, and the
        #       convention is assumed to be enforced by whoever populates
        #       these parameters.
        self._minimums = {}
        self._averages = {}
        self._maximums = {}
        self._xbars = {} # NODEXBAR
        self._wbars = {} # NODEWBAR

        # a flag indicating whether the _solutions attribute has been properly initialized.
        self._solution_map_initialized = False

        # solution (variable) values for this node. assumed to be distinct
        # from self._averages, as the latter are not necessarily feasible.
        # keys are variable names.
        self._solutions = {}

        if initialize_solution is True:
            if scenario_instance_map is None:
                scenario_instance_map = {}
            self._initialize_solution_map(scenario_instance_map)

    #
    # given a set of scenario instances, compute the set of indices being
    # blended for each variable at this node.
    #

    def defineVariableIndexSets(self, reference_instance):

        for variable_name, (reference_variable, match_templates) in iteritems(self._stage._variables):

            # the stage variable simply references the variable object in the
            # reference scenario instance - we need to grab the variable in the
            # scenario instance, as the index set might be different.
            instance_variable = reference_instance.find_component(variable_name)

            for match_template in match_templates:
                
                new_match_indices = extractVariableIndices(instance_variable, match_template)
                
                # there may be existing match indices for this variable, e.g., if
                # the scenario tree specifies non-anticipative variables by listing
                # each index element explicitly (as opposed as through the use of slices).
                existing_indices = self._variable_indices.setdefault(variable_name,[])
                existing_indices.extend(new_match_indices)

    #
    # copies the parameter values values from the _averages attribute
    # into the _solutions attribute - only for active variable values.
    #

    def snapshotSolutionFromAverages(self, scenario_instance_map):

        if self._solution_map_initialized is False:
            self._initialize_solution_map(scenario_instance_map)

        for variable_name, var_dict in iteritems(self._solutions):

            # try and grab the corresponding averages parameter - if it
            # doesn't exist, throw an exception.
            average_parameter = None
            try:
                average_parameter = self._averages[variable_name]
            except:
                raise RuntimeError("No averages parameter present on tree node="+self._name+" for variable="+variable_name)

            for index in var_dict:
                    var_dict[index] = average_parameter[index]

    #
    # computes the solution values from the composite scenario instances at this tree node.
    # the input scenario_instance_map is a map from scenario name to instance objects.
    #

    def snapshotSolutionFromInstances(self, scenario_instance_map):

        if self._solution_map_initialized is False:
            self._initialize_solution_map(scenario_instance_map)

        for variable_name, var_dict in iteritems(self._solutions):
            for index in var_dict:
                node_probability = 0.0
                avg = 0.0
                num_scenarios_with_index = 0
                for scenario in self._scenarios:
                    scenario_instance = scenario_instance_map[scenario._name]
                    node_probability += scenario._probability
                    scenario_variable = scenario_instance.find_component(variable_name)
                    if index in scenario_variable:
                        num_scenarios_with_index = num_scenarios_with_index + 1
                        var = scenario_variable[index]
                        if (var.stale is True) and (var.fixed is False): # a variable that is fixed will be flagged as unused.
                            print("CAUTION: Encountered variable="+var.name+" that is not in use within scenario="+scenario._name+", but the scenario tree specification indicates that non-anticipativity is to be enforced; the variable should either be eliminated from the model or from the scenario tree specification.")
                        else:
                            var_value = value(var)
                            avg += (scenario._probability * var_value)
                # the node probability is allowed to be zero in the scenario tree specification.
                # this is useful in cases where one wants to temporarily ignore certain scenarios.
                # in this case, just skip reporting of variables for that node.
                            
                if (num_scenarios_with_index > 0) and (node_probability > 0.0):
                    var_dict[index] = avg / node_probability

    #
    # a utility to compute the cost of the current node plus the expected costs of child nodes.
    #

    def computeExpectedNodeCost(self, scenario_instance_map):

        # IMPT: This implicitly assumes convergence across the scenarios - if not, garbage results.
        instance = scenario_instance_map[self._scenarios[0]._name]
        stage_cost_variable = instance.active_subcomponents(Var)[self._stage._cost_variable[0].name][self._stage._cost_variable[1]]
        if stage_cost_variable.value is not None:
            my_cost = stage_cost_variable.value
        else:
            # depending on the situation (and the model), the stage cost variables might not have values.
            my_cost = 0.0
        child_cost = 0.0
        for child in self._children:
            child_cost += (child._conditional_probability * child.computeExpectedNodeCost(scenario_instance_map))
        return my_cost + child_cost


class Stage(object):

    """ Constructor
    """
    def __init__(self, *args, **kwds):

        self._name = ""

        # a collection of ScenarioTreeNode objects associated with this stage.
        self._tree_nodes = []

        # a map between a variable name and a pair (tuple) consisting of:
        # 1) a Var in the reference scenario instance
        # 2) a list of original index match templates, given as strings. we want to maintain these
        #    for a variety of reasons, perhaps the most important being that for output purposes. 
        #    specific indices that match belong to the tree node, as that may be specific to a tree 
        #    node (although we don't do anything with that quite yet).
        #    IMPT: the match templates are *not* full tuples, but rather tuple representations of the
        #          original match template strings provided by the user, e.g., a list of strings, one
        #          for each dimension. each dimension may be a wildcard.
        self._variables = {}

        # a tuple consisting of (1) a reference to a pyomo model Var that computes the stage-specific cost and (2) the corresponding
        # index. the index *is* the sole index in the cost variable, as the cost variable refers to a single variable index.
        self._cost_variable = (None, None)

    #
    # add a new variable to the stage, which will include updating the solution maps for each associated ScenarioTreeNode.
    # the input variable is a Pyomo Var object - not just a name.
    #
    def add_variable(self, variable, new_match_template, scenario_instance_map):
   
        existing_match_templates = self._variables.setdefault(variable.name, (variable, []))[1]
        existing_match_templates.append(new_match_template)

        match_indices = extractVariableIndices(variable, new_match_template)

        for tree_node in self._tree_nodes:
            tree_node._variable_indices[variable.name] = match_indices 
            tree_node._solutions[variable.name] = dict((index,None) for index in match_indices)

class Scenario(object):

    """ Constructor
    """
    def __init__(self, *args, **kwds):

        self._name = None
        self._leaf_node = None  # allows for construction of node list
        self._node_list = []    # sequence from parent to leaf of ScenarioTreeNodes
        self._probability = 0.0 # the unconditional probability for this scenario, computed from the node list

class ScenarioTreeBundle(object):

     def __init__(self, *args, **kwds):
       
         self._name = None
         self._scenario_names = []
         self._scenario_tree = None # This is a compressed scenario tree, just for the bundle.
         self._probability = 0.0 # the absolute probability of scenarios associated with this node in the scenario tree.

class ScenarioTree(object):

    # a utility to construct scenario bundles.
    def _construct_scenario_bundles(self, scenario_tree_instance):

        for bundle_name in scenario_tree_instance.Bundles:
           scenario_list = []
           bundle_probability = 0.0
           for scenario_name in scenario_tree_instance.BundleScenarios[bundle_name]:
              scenario_list.append(scenario_name)              
              bundle_probability += self._scenario_map[scenario_name]._probability

           scenario_tree_instance.Bundling[None] = False # to stop recursion!
           
           scenario_tree_for_bundle = ScenarioTree(scenarioinstance=self._reference_instance,
                                                   scenariotreeinstance=scenario_tree_instance,
                                                   scenariobundlelist=scenario_list)
           scenario_tree_instance.Bundling[None] = True

           if scenario_tree_for_bundle.validate() is False:
               raise RuntimeError("***ERROR: Bundled scenario tree is invalid!!!")

           new_bundle = ScenarioTreeBundle()
           new_bundle._name = bundle_name
           new_bundle._scenario_names = scenario_list
           new_bundle._scenario_tree = scenario_tree_for_bundle
           new_bundle._probability = bundle_probability

           self._scenario_bundles.append(new_bundle)
           self._scenario_bundle_map[new_bundle._name] = new_bundle

    # a utility to construct the stage objects for this scenario tree.
    # operates strictly by side effects, initializing the self
    # _stages and _stage_map attributes.
    def _construct_stages(self, stage_names, stage_variable_names, stage_cost_variable_names):

        # construct the stage objects, which will leave them
        # largely uninitialized - no variable information, in particular.
        for stage_name in stage_names:
            new_stage = Stage()
            new_stage._name = stage_name
            self._stages.append(new_stage)
            self._stage_map[stage_name] = new_stage

        # initialize the variable collections (blended and cost) for each stage.
        # the variables refer to variables (Pyomo Var objects) in the reference scenarioinstance.
        for stage_name in stage_variable_names:

            if stage_name not in self._stage_map:
                raise ValueError("Unknown stage=" + stage_name + " specified in scenario tree constructor (stage->variable map)")
            stage = self._stage_map[stage_name]

            variable_names = stage_variable_names[stage_name]

            for variable_string in variable_names:

                if isVariableNameIndexed(variable_string) is True:

                    variable_name, match_template = extractVariableNameAndIndex(variable_string)

                    variable = self._reference_instance.find_component(variable_name)

                    assert variable.is_indexed()
                    assert variable.name == variable_name

                    # validate that the variable exists in the reference scenario instance
                    if variable is None:
                        raise ValueError("Variable=" + variable_name + " associated with stage=" + stage_name + " is not present in model=" + self._reference_instance.name+"; scenario tree construction failed")

                    if not variable.type() is Var:
                        raise RuntimeError("The component=" + variable_string + " associated with stage=" + stage_name + " is present in model=" + self._reference_instance.name + " but is not a variable - type="+str(type(variable)) + "!")

                    # validate that at least one of the indices in the variable matches to the template - otherwise, the template is bogus.
                    if len(extractVariableIndices(variable, match_template)) == 0:
                        raise ValueError("No indices match template="+str(match_template)+" for variable=" + variable_name + " associated with stage=" + stage_name)

                    # update the stage variable map.
                    existing_match_templates = stage._variables.setdefault(variable.name, (variable, []))[1]
                    existing_match_templates.append(match_template)

                else:

                    # verify that the variable exists.
                    variable = self._reference_instance.find_component(variable_string)
                    
                    assert variable.name == variable_string

                    if variable is None:
                        raise RuntimeError("Unknown variable=" + variable_string + " associated with stage=" + stage_name + " is not present in model=" + self._reference_instance.name)

                    if not variable.type() is Var:
                        raise RuntimeError("The component=" + variable_string + " associated with stage=" + stage_name + " is present in model=" + self._reference_instance.name + " but is not a variable - type="+str(type(variable)) + "!")

                    if not variable.active:
                        raise RuntimeError("The variable=" + variable_string + " associated with stage=" + stage_name + " in model=" + self._reference_instance.name + "is not active!")

                    # 9/14/2009 - now forcing the user to explicit specify the full
                    # match template (e.g., "foo[*,*]") instead of just the variable
                    # name (e.g., "foo") to represent the set of all indices.

                    # if the variable is a singleton - that is, non-indexed - no brackets is fine.
                    # we'll just tag the var[None] variable value with the (suffix,value) pair.
                    if variable.is_indexed():
                        raise RuntimeError("Variable="+variable_string+" is an indexed variable, and templates must specify an index match; encountered in scenario tree specification for model="+self._reference_instance.name)

                    # update the stage variable map.
                    existing_match_templates = stage._variables.setdefault(variable.name, (variable, []))[1]
                    existing_match_templates.append("")

        for stage_name in stage_cost_variable_names:

            if stage_name not in self._stage_map:
                raise ValueError("Unknown stage=" + stage_name + " specified in scenario tree constructor (stage->cost variable map)")
            stage = self._stage_map[stage_name]

            cost_variable_string = value(stage_cost_variable_names[stage_name]) # de-reference is required to access the parameter value

            # to be extracted from the string.
            cost_variable_name = None
            cost_variable = None
            cost_variable_index = None

            # do the extraction.
            if isVariableNameIndexed(cost_variable_string) is True:

                cost_variable_name, match_template = extractVariableNameAndIndex(cost_variable_string)

                cost_variable = self._reference_instance.find_component(cost_variable_name)

                assert cost_variable.is_indexed()
                assert cost_variable.name == cost_variable_name

                # validate that the variable exists and extract the reference.
                if cost_variable is None:
                    raise ValueError("Variable=" + cost_variable_name + " associated with stage=" + stage_name + " is not present in model=" + self._reference_instance.name)

                if not cost_variable.type() is Var:
                    raise RuntimeError("The component=" + cost_variable_string + " associated with stage=" + stage_name + " is present in model=" + self._reference_instance.name + " but is not a variable - type="+str(cost_variable.type()) + "!")

                # extract all "real", i.e., fully specified, indices matching the index template.
                match_indices = extractVariableIndices(cost_variable, match_template)

                # only one index can be supplied for a stage cost variable.
                if len(match_indices) > 1:
                    msg = 'Only one index can be specified for a stage cost '     \
                          'variable - %s match template "%s" for variable "%s" ;' \
                          ' encountered in scenario tree specification for model' \
                          ' "%s"'
                    raise RuntimeError(msg % (
                      len(match_indices),
                      match_template,
                      cost_variable_name,
                      self._reference_instance.name)
                    )
                elif len(match_indices) == 0:
                    msg = 'Stage cost index not found: %s[%s]\n'                  \
                          'Do you have an off-by-one miscalculation, or did you ' \
                          'forget to specify it in ReferenceModel.dat?'
                    raise RuntimeError(msg % ( cost_variable_name, match_template ))

                cost_variable_index = match_indices[0]

            else:

                cost_variable_name = cost_variable_string

                # verify that the variable exists.
                cost_variable = self._reference_instance.find_component(cost_variable_name)

                assert cost_variable.name == cost_variable_name

                if cost_variable is None:
                    raise RuntimeError("Cost variable=" + cost_variable_name + " associated with stage=" + stage_name + " is not present in model=" + self._reference_instance.name)

                if not cost_variable.type() is Var:
                    raise RuntimeError("The component=" + cost_variable_string + " associated with stage=" + stage_name + " is present in model=" + self._reference_instance.name + " but is not a variable - type="+str(cost_variable.type()) + "!")

                if not cost_variable.active:
                    raise RuntimeError("Cost variable=" + cost_variable_string + " associated with stage=" + stage_name + " in model=" + self._reference_instance.name + "is not active!")
                
                # if the variable is a singleton - that is, non-indexed - no brackets is fine.
                # we'll just tag the var[None] variable value with the (suffix,value) pair.
                if cost_variable.is_indexed():
                    raise RuntimeError("Cost Variable="+variable_string+" is an indexed variable, and templates must specify an index match; encountered in scenario tree specification for model="+self._reference_instance.name)

            # store the validated info.
            stage._cost_variable = (cost_variable, cost_variable_index)

    """ Constructor
        Arguments:
            scenarioinstance     - the reference (deterministic) scenario instance.
            scenariotreeinstance - the pyomo model specifying all scenario tree (text) data.
            scenariobundlelist   - a list of scenario names to retain, i.e., cull the rest to create a reduced tree!
    """
    def __init__(self, *args, **kwds):

        self._name = None # some arbitrary identifier
        self._reference_instance = kwds.pop( 'scenarioinstance', None ) # the reference (deterministic) base model

        # the core objects defining the scenario tree.
        self._tree_nodes = [] # collection of ScenarioTreeNodes
        self._stages = [] # collection of Stages - assumed to be in time-order. the set (provided by the user) itself *must* be ordered.
        self._scenarios = [] # collection of Scenarios
        self._scenario_bundles = [] # collection of ScenarioTreeBundles

        # dictionaries for the above.
        self._tree_node_map = {}
        self._stage_map = {}
        self._scenario_map = {}
        self._scenario_bundle_map = {}

        # a boolean indicating how data for scenario instances is specified.
        # possibly belongs elsewhere, e.g., in the PH algorithm.
        self._scenario_based_data = None

        scenario_tree_instance = kwds.pop( 'scenariotreeinstance', None )
        scenario_bundle_list = kwds.pop( 'scenariobundlelist', None )

        # process the keyword options
        for key in kwds:
            sys.stderr.write("Unknown option '%s' specified in call to ScenarioTree constructor\n" % key)

        if self._reference_instance is None:
            raise ValueError("A reference scenario instance must be supplied in the ScenarioTree constructor")

        if scenario_tree_instance is None:
            raise ValueError("A scenario tree instance must be supplied in the ScenarioTree constructor")

        node_ids = scenario_tree_instance.Nodes
        node_child_ids = scenario_tree_instance.Children
        node_stage_ids = scenario_tree_instance.NodeStage
        node_probability_map = scenario_tree_instance.ConditionalProbability
        stage_ids = scenario_tree_instance.Stages
        stage_variable_ids = scenario_tree_instance.StageVariables
        stage_cost_variable_ids = scenario_tree_instance.StageCostVariable
        scenario_ids = scenario_tree_instance.Scenarios
        scenario_leaf_ids = scenario_tree_instance.ScenarioLeafNode
        scenario_based_data = scenario_tree_instance.ScenarioBasedData

        # save the method for instance data storage.
        self._scenario_based_data = scenario_based_data()

        # the input stages must be ordered, for both output purposes and knowledge of the final stage.
        if stage_ids.ordered is False:
            raise ValueError("An ordered set of stage IDs must be supplied in the ScenarioTree constructor")

        #
        # construct the actual tree objects
        #

        # construct the stage objects w/o any linkages first; link them up
        # with tree nodes after these have been fully constructed.
        self._construct_stages(stage_ids, stage_variable_ids, stage_cost_variable_ids)

        # construct the tree node objects themselves in a first pass,
        # and then link them up in a second pass to form the tree.
        # can't do a single pass because the objects may not exist.
        for tree_node_name in node_ids:

            if tree_node_name not in node_stage_ids:
                raise ValueError("No stage is assigned to tree node=" + tree_node._name)

            stage_name = value(node_stage_ids[tree_node_name])
            if stage_name not in iterkeys(self._stage_map):
                raise ValueError("Unknown stage=" + stage_name + " assigned to tree node=" + tree_node._name)

            new_tree_node = ScenarioTreeNode(tree_node_name,
                                             value(node_probability_map[tree_node_name]),
                                             self._stage_map[stage_name])

            self._tree_nodes.append(new_tree_node)
            self._tree_node_map[tree_node_name] = new_tree_node
            self._stage_map[stage_name]._tree_nodes.append(new_tree_node)

        # link up the tree nodes objects based on the child id sets.
        for this_node in self._tree_nodes:
            this_node._children = []
            if this_node._name in node_child_ids: # otherwise, you're at a leaf and all is well.
                child_ids = node_child_ids[this_node._name]
                for child_id in child_ids:
                    if child_id in self._tree_node_map:
                        child_node = self._tree_node_map[child_id]
                        this_node._children.append(child_node)
                        if child_node._parent is None:
                            child_node._parent = this_node
                        else:
                            raise ValueError("Multiple parents specified for tree node="+child_id+"; existing parent node="+child_node._parent._name+"; conflicting parent node="+this_node._name)
                    else:
                        raise ValueError("Unknown child tree node=" + child_id + " specified for tree node=" + this_node._name)

        # at this point, the scenario tree nodes and the stages are set - no
        # two-pass logic necessary when constructing scenarios.
        for scenario_name in scenario_ids:

            # IMPT: the name of the scenario is assumed to have no '_' (underscore) characters in the identifier.
            #       this is required when writing the extensive form, e.g., the scenario is used in the extensive
            #       form as a prefix on variable and constraint names. this convention simplifies parsing on the
            #       back end; if the underscore isn't used as a reserved character, then some other separator
            #       symbol would be required, or we would have to engage in some complex prefix matching with
            #       all possible scenario names.
            if scenario_name.count("_") != 0:
                raise ValueError("By convention, scenario names in PySP cannot contain underscore (_) characters; the scenario in violation="+scenario_name)

            new_scenario = Scenario()
            new_scenario._name=scenario_name

            if scenario_name not in iterkeys(scenario_leaf_ids):
                raise ValueError("No leaf tree node specified for scenario=" + scenario_name)
            else:
                scenario_leaf_node_name = value(scenario_leaf_ids[scenario_name])
                if scenario_leaf_node_name not in self._tree_node_map:
                    raise ValueError("Uknown tree node=" + scenario_leaf_node_name + " specified as leaf of scenario=" + scenario_name)
                else:
                    new_scenario._leaf_node = self._tree_node_map[scenario_leaf_node_name]

            current_node = new_scenario._leaf_node
            probability = 1.0
            while current_node is not None:
                new_scenario._node_list.append(current_node)
                current_node._scenarios.append(new_scenario) # links the scenarios to the nodes to enforce necessary non-anticipativity
                probability *= current_node._conditional_probability
                current_node = current_node._parent
            new_scenario._node_list.reverse()
            new_scenario._probability = probability

            self._scenarios.append(new_scenario)
            self._scenario_map[scenario_name] = new_scenario

        # for output purposes, it is useful to known the maximal length of identifiers
        # in the scenario tree for any particular category. I'm building these up
        # incrementally, as they are needed. 0 indicates unassigned.
        self._max_scenario_id_length = 0

        # does the actual traversal to populate the members.
        self.computeIdentifierMaxLengths()

        # if a sub-bundle of scenarios has been specified, mark the
        # active scenario tree components and compress the tree.
        if scenario_bundle_list is not None:
            self.compress(scenario_bundle_list)

        # NEW SCENARIO BUNDLING STARTS HERE
        if value(scenario_tree_instance.Bundling[None]) is True:
           self._construct_scenario_bundles(scenario_tree_instance)

    #
    # given a set of scenario instances, compute the set of variable indices being blended at each node.
    # this can't be done until the scenario instances are available, as different scenarios can have
    # different index sets.
    #

    def defineVariableIndexSets(self, reference_instance):

        for tree_node in self._tree_nodes:

            tree_node.defineVariableIndexSets(reference_instance)

    #
    # is the indicated scenario / bundle in the tree?
    #

    def contains_scenario(self, name):
        return name in self._scenario_map

    def contains_bundles(self):
        return len(self._scenario_bundle_map) > 0

    def contains_bundle(self, name):
        return name in self._scenario_bundle_map

    #
    # get the scenario / bundle object from the tree.
    #

    def get_scenario(self, name):
        return self._scenario_map[name]

    def get_bundle(self, name):
        return self._scenario_bundle_map[name]

    #
    # compute the scenario cost for the input instance, i.e.,
    # the sum of all stage cost variables.
    #

    def compute_scenario_cost(self, instance):
        aggregate_cost = 0.0
        for stage in self._stages:
            instance_cost_variable = instance.active_subcomponents(Var)[stage._cost_variable[0].name][stage._cost_variable[1]]
            if instance_cost_variable.value is not None:
                    # depending on the situation (and the model), the stage cost variables might not have values.
                aggregate_cost += instance_cost_variable
        return aggregate_cost

    #
    # utility for compressing or culling a scenario tree based on
    # a provided list of scenarios (specified by name) to retain -
    # all non-referenced components are eliminated. this particular
    # method compresses *in-place*, i.e., via direct modification
    # of the scenario tree structure.
    #

    def compress(self, scenario_bundle_list):

        # scan for and mark all referenced scenarios and
        # tree nodes in the bundle list - all stages will
        # obviously remain.
        for scenario_name in scenario_bundle_list:
            if scenario_name not in self._scenario_map:
                raise ValueError("Scenario="+scenario_name+" selected for bundling not present in scenario tree")
            scenario = self._scenario_map[scenario_name]
            scenario.retain = True

            # chase all nodes comprising this scenario,
            # marking them for retention.
            for node in scenario._node_list:
                node.retain = True

        # scan for any non-retained scenarios and tree nodes.
        scenarios_to_delete = []
        tree_nodes_to_delete = []
        for scenario in self._scenarios:
            if hasattr(scenario, "retain") is True:
                delattr(scenario, "retain")
            else:
                scenarios_to_delete.append(scenario)
                del self._scenario_map[scenario._name]

        for tree_node in self._tree_nodes:
            if hasattr(tree_node, "retain") is True:
                delattr(tree_node, "retain")
            else:
                tree_nodes_to_delete.append(tree_node)
                del self._tree_node_map[tree_node._name]

        # JPW does not claim the following routines are
        # the most efficient. rather, they get the job
        # done while avoiding serious issues with
        # attempting to remove elements from a list that
        # you are iterating over.

        # delete all references to unmarked scenarios
        # and child tree nodes in the scenario tree node
        # structures.
        for tree_node in self._tree_nodes:
            for scenario in scenarios_to_delete:
                if scenario in tree_node._scenarios:
                    tree_node._scenarios.remove(scenario)
            for node_to_delete in tree_nodes_to_delete:
                if node_to_delete in tree_node._children:
                    tree_node._children.remove(node_to_delete)

        # delete all references to unmarked tree nodes
        # in the scenario tree stage structures.
        for stage in self._stages:
            for tree_node in tree_nodes_to_delete:
                if tree_node in stage._tree_nodes:
                    stage._tree_nodes.remove(tree_node)

        # delete all unreferenced entries from the core scenario
        # tree data structures.
        for scenario in scenarios_to_delete:
            self._scenarios.remove(scenario)
        for tree_node in tree_nodes_to_delete:
            self._tree_nodes.remove(tree_node)


        # re-normalize the conditional probabilities of the
        # children at each tree node.
        for tree_node in self._tree_nodes:
            sum_child_probabilities = 0.0
            for child_node in tree_node._children:
                sum_child_probabilities += child_node._conditional_probability
            for child_node in tree_node._children:
                child_node._conditional_probability = child_node._conditional_probability / sum_child_probabilities

        # re-compute the absolute scenario probabilities based
        # on the re-normalized conditional node probabilities.
        for scenario in self._scenarios:
            probability = 1.0
            for tree_node in scenario._node_list:
                probability = probability * tree_node._conditional_probability
            scenario._probability = probability

    #
    # utility for automatically selecting a proportion of scenarios from the
    # tree to retain, eliminating the rest.
    #

    def downsample(self, fraction_to_retain, random_seed, verbose=False):

        random.seed(random_seed)

        random_sequence=range(len(self._scenarios))
        random.shuffle(random_sequence)

        number_to_retain = max(int(round(float(len(random_sequence)*fraction_to_retain))), 1)

        scenario_bundle_list = []
        for i in xrange(number_to_retain):
            scenario_bundle_list.append(self._scenarios[random_sequence[i]]._name)

        if verbose is True:
            print("Downsampling scenario tree - retained scenarios: "+str(scenario_bundle_list))

        self.compress(scenario_bundle_list)


    #
    # returns the root node of the scenario tree
    #

    def findRootNode(self):

        for tree_node in self._tree_nodes:
            if tree_node._parent is None:
                return tree_node
        return None

    #
    # a utility function to compute, based on the current scenario tree content,
    # the maximal length of identifiers in various categories.
    #

    def computeIdentifierMaxLengths(self):

        self._max_scenario_id_length = 0
        for scenario in self._scenarios:
            if len(scenario._name) > self._max_scenario_id_length:
                self._max_scenario_id_length = len(scenario._name)

    #
    # a utility function to (partially, at the moment) validate a scenario tree
    #

    def validate(self):

        # for any node, the sum of conditional probabilities of the children should sum to 1.
        for tree_node in self._tree_nodes:
            sum_probabilities = 0.0
            if len(tree_node._children) > 0:
                for child in tree_node._children:
                    sum_probabilities += child._conditional_probability
                if abs(1.0 - sum_probabilities) > 0.000001:
                    print("The child conditional probabilities for tree node=" + tree_node._name + " sum to " + str(sum_probabilities))
                    return False

        # ensure that there is only one root node in the tree
        num_roots = 0
        root_ids = []
        for tree_node in self._tree_nodes:
            if tree_node._parent is None:
                num_roots += 1
                root_ids.append(tree_node._name)

        if num_roots != 1:
            print("Illegal set of root nodes detected: " + str(root_ids))
            return False

        # there must be at least one scenario passing through each tree node.
        for tree_node in self._tree_nodes:
            if len(tree_node._scenarios) == 0:
                print("There are no scenarios associated with tree node=" + tree_node._name)
                return False

        return True

    #
    # copies the parameter values stored in any tree node _averages attribute
    # into any tree node _solutions attribute - only for active variable values.
    #

    def snapshotSolutionFromAverages(self, scenario_instance_map):

        for tree_node in self._tree_nodes:

            tree_node.snapshotSolutionFromAverages(scenario_instance_map)

    #
    # computes the variable values at each tree node from the input scenario instances.
    #

    def snapshotSolutionFromInstances(self, scenario_instance_map):

        for tree_node in self._tree_nodes:

            tree_node.snapshotSolutionFromInstances(scenario_instance_map)

    #
    # a utility to determine the stage to which the input variable belongs.
    # this is horribly inefficient, in the absence of an inverse map. fortunately,
    # it isn't really called that often (yet). stage membership is determined
    # by comparing the input variable name with the reference instance
    # variable name (which is what the scenario tree refers to) and the
    # associated indices.
    #

    def variableStage(self, variable, index):

        # NOTE: The logic below is bad, in the sense that the looping should
        #       really be over tree nodes - a stage in isolation doesn't make
        #       any sense at all. ultimately, this will involve by-passing the
        #       extractVariableIndices logic, and moving toward iteration over
        #       the tree nodes within a stage.
        for stage in self._stages:
            for variable_name, (stage_var, match_template) in iteritems(stage._variables):
                if (variable.name == stage_var.name):
                    match_indices = extractVariableIndices(variable, match_template[0])
                    if ((index is None) and (len(match_indices)==0)) or (index in match_indices):
                        return stage

            # IMPT: this is a temporary hack - the real fix is to force users to
            # have every variable assigned to some stage in the model, either
            # automatically or explicitly.
            if (variable.name == stage._cost_variable[0].name):
                return stage

        raise RuntimeError("The variable="+str(variable.name)+", index="+str(index)+" does not belong to any stage in the scenario tree")

    #
    # a utility to determine the stage to which the input constraint "belongs".
    # a constraint belongs to the latest stage in which referenced variables
    # in the constraint appears in that stage.
    # input is a constraint is of type "Constraint", and an index of that
    # constraint - which might be None in the case of singleton constraints.
    # currently doesn't deal with SOS constraints, for no real good reason.
    # returns an instance of a Stage object.
    # IMPT: this method works on the canonical representation ("repn" attribute)
    #       of a constraint. this implies that pre-processing of the instance
    #       has been performed.
    # NOTE: there is still the issue of whether the contained variables really
    #       belong to the same model, but that is a different issue we won't
    #       address right now (e.g., what does it mean for a constraint in an
    #       extensive form binding instance to belong to a stage?).
    #

    def constraintStage(self, constraint, index):

        largest_stage_index = -1
        largest_stage = None

        canonical_repn = constraint.parent().repn.getValue(constraint[index])

        if isinstance(canonical_repn, GeneralCanonicalRepn):
            raise RuntimeError("***ERROR: Method constraintStage in class ScenarioTree encountered a constraint with a general canonical encoding - only linear canonical encodings are expected!")

        for id, var_value in iteritems(canonical_repn.variables):

            var_stage = self.variableStage(var_value.component(), var_value.index)
            var_stage_index = self._stages.index(var_stage)

            if var_stage_index > largest_stage_index:
                largest_stage_index = var_stage_index
                largest_stage = var_stage

        return largest_stage

    #
    # method to create random bundles of scenarios - like the name says!
    #

    def create_random_bundles(self, scenario_tree_instance, num_bundles, random_seed):

        random.seed(random_seed)

        num_scenarios = len(self._scenarios)

        sequence = range(num_scenarios)
        random.shuffle(sequence)

        scenario_tree_instance.Bundling[None] = True

        bundle_size = int(ceil(num_scenarios / num_bundles))

        next_scenario_index = 0

        scenario_tree_instance.Bundles = Set()
        for i in xrange(1, num_bundles+1):
            bundle_name = "Bundle"+str(i)
            scenario_tree_instance.Bundles.add(bundle_name)

        scenario_tree_instance.BundleScenarios = Set(scenario_tree_instance.Bundles)

        for i in xrange(1, num_bundles+1):
            bundle_name = "Bundle"+str(i)
            scenario_tree_instance.BundleScenarios[bundle_name] = Set()
            for j in xrange(1,bundle_size+1):
                scenario_name = self._scenarios[sequence[next_scenario_index]]._name
                scenario_tree_instance.BundleScenarios[bundle_name].add(scenario_name)
                next_scenario_index+=1
        for i in xrange(next_scenario_index, num_scenarios):
            scenario_name = self._scenarios[sequence[next_scenario_index]]._name
            scenario_tree_instance.BundleScenarios[bundle_name].add(scenario_name)
            next_scenario_index+=1

        self._construct_scenario_bundles(scenario_tree_instance)

    #
    # a utility function to pretty-print the static/non-cost information associated with a scenario tree
    #

    def pprint(self):

        print("Scenario Tree Detail")

        print("----------------------------------------------------")
        if self._reference_instance is not None:
            print("Model=" + self._reference_instance.name)
        else:
            print("Model=" + "Unassigned")
        print("----------------------------------------------------")
        print("Tree Nodes:")
        print("")
        for tree_node_name in sorted(iterkeys(self._tree_node_map)):
            tree_node = self._tree_node_map[tree_node_name]
            print("\tName=" + tree_node_name)
            if tree_node._stage is not None:
                print("\tStage=" + str(tree_node._stage._name))
            else:
                print("\t Stage=None")
            if tree_node._parent is not None:
                print("\tParent=" + tree_node._parent._name)
            else:
                print("\tParent=" + "None")
            if tree_node._conditional_probability is not None:
                print("\tConditional probability=%4.4f" % tree_node._conditional_probability)
            else:
                print("\tConditional probability=" + "***Undefined***")
            print("\tChildren:")
            if len(tree_node._children) > 0:
                for child_node in sorted(tree_node._children, key=lambda x: x._name):
                    print("\t\t" + child_node._name)
            else:
                print("\t\tNone")
            print("\tScenarios:")
            if len(tree_node._scenarios) == 0:
                print("\t\tNone")
            else:
                for scenario in sorted(tree_node._scenarios, key=lambda x: x._name):
                    print("\t\t" + scenario._name)
            print("")
        print("----------------------------------------------------")
        print("Stages:")
        for stage_name in sorted(iterkeys(self._stage_map)):
            stage = self._stage_map[stage_name]
            print("\tName=" + str(stage_name))
            print("\tTree Nodes: ")
            for tree_node in sorted(stage._tree_nodes, key=lambda x: x._name):
                print("\t\t" + tree_node._name)
            print("\tVariables: ")
            for variable_name in sorted(iterkeys(stage._variables)):
                (variable, match_templates) = stage._variables[variable_name]
                sys.stdout.write("\t\t "+variable.name+" : ")
                for match_template in match_templates:
                   sys.stdout.write(indexToString(match_template)+' ')
                print("")
            print("\tCost Variable: ")
            if stage._cost_variable[1] is None:
                print("\t\t" + stage._cost_variable[0].name)
            else:
                print("\t\t" + stage._cost_variable[0].name + indexToString(stage._cost_variable[1]))
            print("")
        print("----------------------------------------------------")
        print("Scenarios:")
        for scenario_name in sorted(iterkeys(self._scenario_map)):
            scenario = self._scenario_map[scenario_name]
            print("\tName=" + scenario_name)
            print("\tProbability=%4.4f" % scenario._probability)
            if scenario._leaf_node is None:
                print("\tLeaf node=None")
            else:
                print("\tLeaf node=" + scenario._leaf_node._name)
            print("\tTree node sequence:")
            for tree_node in scenario._node_list:
                print("\t\t" + tree_node._name)
            print("")
        print("----------------------------------------------------")
        if len(self._scenario_bundles) > 0:
            print("Scenario Bundles:")
            for bundle_name in sorted(iterkeys(self._scenario_bundle_map)):
                scenario_bundle = self._scenario_bundle_map[bundle_name]
                print("\tName=" + bundle_name)
                print("\tProbability=%4.4f" % scenario_bundle._probability            )
                sys.stdout.write("\tScenarios:  ")
                for scenario_name in sorted(scenario_bundle._scenario_names):
                    sys.stdout.write(scenario_name+' ')
                sys.stdout.write("\n")
                print("")
            print("----------------------------------------------------")

    #
    # a utility function to pretty-print the solution associated with a scenario tree
    #

    def pprintSolution(self, epsilon=1.0e-5):

        print("----------------------------------------------------")
        print("Tree Nodes:")
        print("")
        for tree_node_name in sorted(iterkeys(self._tree_node_map)):
            tree_node = self._tree_node_map[tree_node_name]
            print("\tName=" + tree_node_name)
            if tree_node._stage is not None:
                print("\tStage=" + tree_node._stage._name)
            else:
                print("\t Stage=None")
            if tree_node._parent is not None:
                print("\tParent=" + tree_node._parent._name)
            else:
                print("\tParent=" + "None")
            print("\tVariables: ")
            for variable_name, (variable, match_template) in iteritems(tree_node._stage._variables):
                indices = sorted(tree_node._variable_indices[variable.name])
                solution_var_dict = tree_node._solutions[variable.name]
                for index in indices:
                    value = solution_var_dict[index]
                    if (value is not None) and (fabs(value) > epsilon):
                        print("\t\t"+variable_name+indexToString(index)+"="+str(value))
            print("")

    #
    # a utility function to pretty-print the cost information associated with a scenario tree
    #

    def pprintCosts(self, scenario_instance_map):

        print("Scenario Tree Costs")
        print("***CAUTION***: Assumes full (or nearly so) convergence of scenario solutions at each node in the scenario tree - computed costs are invalid otherwise")

        print("----------------------------------------------------")
        if self._reference_instance is not None:
            print("Model=" + self._reference_instance.name)
        else:
            print("Model=" + "Unassigned")

        print("----------------------------------------------------")
        print("Tree Nodes:")
        print("")
        for tree_node_name in sorted(iterkeys(self._tree_node_map)):
            tree_node = self._tree_node_map[tree_node_name]
            print("\tName=" + tree_node_name)
            if tree_node._stage is not None:
                print("\tStage=" + tree_node._stage._name)
            else:
                print("\t Stage=None")
            if tree_node._parent is not None:
                print("\tParent=" + tree_node._parent._name)
            else:
                print("\tParent=" + "None")
            if tree_node._conditional_probability is not None:
                print("\tConditional probability=%4.4f" % tree_node._conditional_probability)
            else:
                print("\tConditional probability=" + "***Undefined***")
            print("\tChildren:")
            if len(tree_node._children) > 0:
                for child_node in sorted(tree_node._children, key=lambda x: x._name):
                    print("\t\t" + child_node._name)
            else:
                print("\t\tNone")
            print("\tScenarios:")
            if len(tree_node._scenarios) == 0:
                print("\t\tNone")
            else:
                for scenario in sorted(tree_node._scenarios, key=lambda x: x._name):
                    print("\t\t" + scenario._name)
            print("\tExpected node cost=%10.4f" % tree_node.computeExpectedNodeCost(scenario_instance_map))
            print("")

        print("----------------------------------------------------")
        print("Scenarios:")
        print("")
        for scenario_name, scenario in sorted(iteritems(self._scenario_map)):
            instance = scenario_instance_map[scenario_name]

            print("\tName=" + scenario_name)
            print("\tProbability=%4.4f" % scenario._probability)

            if scenario._leaf_node is None:
                print("\tLeaf Node=None")
            else:
                print("\tLeaf Node=" + scenario._leaf_node._name)

            print("\tTree node sequence:")
            for tree_node in scenario._node_list:
                print("\t\t" + tree_node._name)

            aggregate_cost = 0.0
            for stage in self._stages:
                instance_cost_variable = instance.active_subcomponents(Var)[stage._cost_variable[0].name][stage._cost_variable[1]]
                if instance_cost_variable.value is not None:
                    print("\tStage=%20s     Cost=%10.4f" % (stage._name, instance_cost_variable.value))
                    cost = instance_cost_variable.value
                else:
                    print("\tStage=%20s     Cost=%10s" % (stage._name, "Not Rprted."))
                    cost = 0.0
                aggregate_cost += cost
            print("\tTotal scenario cost=%10.4f" % aggregate_cost)
            print("")
        print("----------------------------------------------------")
