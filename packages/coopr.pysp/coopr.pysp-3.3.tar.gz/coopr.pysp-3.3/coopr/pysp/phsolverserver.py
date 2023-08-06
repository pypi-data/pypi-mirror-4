#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2010 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________


import gc         # garbage collection control.
import os
import pickle
import pstats     # for profiling
import sys
import time
import traceback

from optparse import OptionParser
import itertools
from six import iterkeys, itervalues, iteritems, advance_iterator

try:
    import cProfile as profile
except ImportError:
    import profile

from coopr.opt.base import SolverFactory
from coopr.pysp.scenariotree import *

from pyutilib.misc import import_file, PauseGC
from pyutilib.services import TempfileManager

import Pyro.core
import Pyro.naming
from Pyro.errors import PyroError, NamingError

from coopr.pysp.phinit import *
from coopr.pysp.phutils import *
from coopr.pysp.phobjective import *
from coopr.pysp.ph import _PHBase

import pyutilib.pyro


class PHSolverServer(pyutilib.pyro.TaskWorker, _PHBase):

    def __init__(self, **kwds):

        pyutilib.pyro.TaskWorker.__init__(self)
        _PHBase.__init__(self)
        
        # only one of these will be != None, following initialization.
        self._scenario_name = None
        self._bundle_name = None
        self._bundle_scenario_tree = None
        self._original_bundle_objective = None

        # the TaskWorker base uses the "type" option to determine the name
        # of the queue from which to request work, via the dispatch server.
        # 
        # the default type is "initialize", which is the queue to which the
        # runph client will transmit initialization to. once initialized,
        # the queue name will be changed to the scenario/bundle name for
        # which this solver server is responsible.
        self.type = "initialize"

    # 
    # Overloading from _PHBase to add a few extra print statements
    #

    def form_standard_objective(self):

        if self._verbose:
           print("Received request to enable standard objective for scenario(s)="+str(list(iterkeys(self._instances))))

        if self._initialized is False:
            raise RuntimeError("***PH solver server has not been initialized!")

        if self._verbose:
            print("Forming standard objective function")

        _PHBase.form_standard_objective(self)

    # 
    # Overloading from _PHBase to add a few extra print statements
    #

    def add_ph_objective_weight_terms(self):

        if self._verbose:
            print("Received request to add PH objective weight terms for scenario(s)="+str(list(iterkeys(self._instances))))

        if self._initialized is False:
            raise RuntimeError("***PH solver server has not been initialized!")

        _PHBase.add_ph_objective_weight_terms(self)

        if self._verbose:
            print("Adding PH objective weight terms")

    # 
    # Overloading from _PHBase to add a few extra print statements
    #

    def add_ph_objective_proximal_terms(self):

        if self._verbose:
            print("Received request to add PH objective proximal terms for scenario(s)="+str(list(iterkeys(self._instances))))

        if self._initialized is False:
            raise RuntimeError("***PH solver server has not been initialized!")

        _PHBase.add_ph_objective_proximal_terms(self)

        if self._verbose:
            print("Adding PH objective proximal terms")

    def initialize(self,
                   model_directory, 
                   instance_directory, 
                   object_name,
                   solver_type, 
                   solver_io,
                   scenario_bundle_specification,
                   create_random_bundles, 
                   scenario_tree_random_seed,
                   default_rho, 
                   linearize_nonbinary_penalty_terms, 
                   retain_quadratic_binary_terms,
                   drop_proximal_terms,
                   breakpoint_strategy,
                   integer_tolerance,
                   verbose):

        if verbose:
            print("Received request to initialize PH solver server")
            print("")
            print("Model directory: "+model_directory)
            print("Instance directory: "+instance_directory)
            print("Solver type: "+solver_type)
            print("Scenario or bundle name: "+object_name)
            if scenario_bundle_specification != None:
                print("Scenario tree bundle specification: "+scenario_bundle_specification)
            if create_random_bundles != None:
                print("Create random bundles: "+str(create_random_bundles))
            if scenario_tree_random_seed != None:
                print("Scenario tree random seed: "+ str(scenario_tree_random_seed))
            print("Linearize non-binary penalty terms: "+ str(linearize_nonbinary_penalty_terms))

        if self._initialized:
            raise RuntimeError("***PH solver servers cannot currently be re-initialized")

        self._verbose = verbose
        self._rho = default_rho
        self._linearize_nonbinary_penalty_terms = linearize_nonbinary_penalty_terms
        self._retain_quadratic_binary_terms = retain_quadratic_binary_terms
        self._drop_proximal_terms = drop_proximal_terms
        self._breakpoint_strategy = breakpoint_strategy
        self._integer_tolerance = integer_tolerance

        # the solver instance is persistent, applicable to all instances here.
        self._solver_type = solver_type
        self._solver_io = solver_io
        if self._verbose:
            print("Constructing solver type="+solver_type)
        self._solver = SolverFactory(solver_type,solver_io=self._solver_io)
        if self._solver == None:
            raise ValueError("Unknown solver type=" + solver_type + " specified")

        # we need the base model (not so much the reference instance, but that
        # can't hurt too much - until proven otherwise, that is) to construct
        # the scenarios that this server is responsible for.
        # TBD - revisit the various "weird" scenario tree arguments
        self._model, self._model_instance, self._scenario_tree, _ = load_reference_and_scenario_models(model_directory,
                                                                                                       instance_directory,
                                                                                                       scenario_bundle_specification,
                                                                                                       None,
                                                                                                       scenario_tree_random_seed,
                                                                                                       create_random_bundles,
                                                                                                       solver_type,
                                                                                                       self._verbose)
                                                                                                                                                
                                                                                                                                                
          
        if self._model is None or self._model_instance is None or self._scenario_tree is None:
             raise RuntimeError("***Unable to launch PH solver server.")

        scenarios_to_construct = []

        if self._scenario_tree.contains_bundles():
            self._bundle_name = object_name

            # validate that the bundle actually exists. 
            if self._scenario_tree.contains_bundle(object_name) is False:
                raise RuntimeError("***Bundle="+object_name+" does not exist.")
    
            if self._verbose:
                print("Loading scenarios for bundle="+object_name)

            # bundling should use the local or "mini" scenario tree - and 
            # then enable the flag to load all scenarios for this instance.
            scenario_bundle = self._scenario_tree.get_bundle(object_name)
            scenarios_to_construct = scenario_bundle._scenario_names

        else:
            self._scenario_name = object_name
            scenarios_to_construct.append(object_name)

        self._problem_states = ProblemStates(scenarios_to_construct)

        for scenario_name in scenarios_to_construct:

            print("Creating instance for scenario="+scenario_name)

            if self._scenario_tree.contains_scenario(scenario_name) is False:
                raise RuntimeError("***Unable to launch PH solver server - unknown scenario specified with name="+scenario_name+".")

            # create the baseline scenario instance
            scenario_instance = construct_scenario_instance(self._scenario_tree,
                                                            instance_directory,
                                                            scenario_name,
                                                            self._model,
                                                            self._verbose,
                                                            preprocess=False,
                                                            linearize=False)

            self._problem_states.objective_updated[scenario_name] = True
            self._problem_states.user_constraints_updated[scenario_name] = True

            # IMPT: disable canonical representation construction for ASL solvers.
            #       this is a hack, in that we need to address encodings and
            #       the like at a more general level.
            if self._solver.problem_format() == ProblemFormat.nl:
                scenario_instance.skip_canonical_repn = True
                # We will take care of these manually within _preprocess_scenario_instance
                # This will also prevent regenerating the ampl_repn when forming the
                # bundle_ef's
                scenario_instance.gen_obj_ampl_repn = False
                scenario_instance.gen_con_ampl_repn = False

            if scenario_instance is None:
                raise RuntimeError("***Unable to launch PH solver server - failed to create instance for scenario="+scenario_name)

            self._instances[scenario_name] = scenario_instance
            self._instances[scenario_name].name = scenario_name

        # with the scenario instances now available, have the scenario tree 
        # compute the variable match indices at each node.
        self._scenario_tree.defineVariableIndexSets(self._model_instance)

        # augment the instance with PH-specific parameters (weights, rhos, etc).
        # this value and the linearization parameter as a command-line argument.
        self._create_scenario_ph_parameters()

        self._preprocess_scenario_instances()

        # create the bundle extensive form, if bundling.
        if self._bundle_name is not None:
            self._bundle_scenario_tree = self._scenario_tree.get_bundle(self._bundle_name)._scenario_tree

            # WARNING: THIS IS A PURE HACK - WE REALLY NEED TO CALL THIS WHEN WE CONSTRUCT THE BUNDLE 
            #          SCENARIO TREE. AS IT STANDS, THIS MUST BE DONE BEFORE CREATING THE EF INSTANCE.
            self._bundle_scenario_tree.defineVariableIndexSets(self._model_instance)
    
            # create the bundle EF instance, and cache the original EF objective.
            # **Note: create_ef_instance assumes the scenario instances have been preprocessed (not required)
            #         and only preprocesses the required components that have been added to the subinstances or 
            #         the binding instance. So no further preprocessing is required.
            self._bundle_ef_instance = create_ef_instance(self._bundle_scenario_tree, 
                                                          self._instances, 
                                                          verbose_output=self._verbose)

            self._original_bundle_objective = find_active_objective(self._bundle_ef_instance).expr


        # the objective functions are modified throughout the course of PH iterations.
        # save the original, as a baseline to modify in subsequent iterations. reserve
        # the original objectives, for subsequent modification.
        for instance_name, instance in iteritems(self._instances):
            expr = find_active_objective(instance,safety_checks=True).expr
            if isinstance(expr, Expression) is False:
                expr = _IdentityExpression(expr)
            self._problem_states.original_objective_expression[instance_name] = expr.clone()

        # the TaskWorker base uses the "type" option to determine the name
        # of the queue from which to request work, via the dispatch server.
        self.type = object_name

        # we're good to go!
        self._initialized = True

    def solve(self, 
              object_name, 
              tee,
              keepfiles,
              symbolic_solver_labels,
              solver_options, 
              solver_suffixes):

      if self._verbose:
          if self._bundle_name is not None:
              print("Received request to solve scenario bundle="+object_name)
          else:
              print("Received request to solve scenario instance="+object_name)

      if self._initialized is False:
          raise RuntimeError("***PH solver server has not been initialized!")

      # process input solver options - they will be persistent across to the  next solve. 
      # TBD: we might want to re-think a reset() of the options, or something.
      for key,value in iteritems(solver_options):
          if self._verbose:
              print("Processing solver option="+key+", value="+str(value))
          self._solver.options[key] = value

      # with the introduction of piecewise linearization, the form of the
      # penalty-weighted objective is no longer fixed. thus, when linearizing,
      # we need to construct (or at least modify) the constraints used to
      # compute the linearized cost terms.
      if (self._linearize_nonbinary_penalty_terms > 0):
          # These functions will do nothing if ph proximal terms are not 
          # present on the model
          self.form_ph_linearized_objective_constraints()
          # if linearizing, clear the values of the PHQUADPENALTY* variables.
          # if they have values, this can intefere with warm-starting due to
          # constraint infeasibilities.
          self._reset_instance_linearization_variables()

      # preprocess all scenario instances as needed - if bundling, we take care of the specifics below.
      self._preprocess_scenario_instances()

      solve_method_result = None

      if self._bundle_name is not None:

          if object_name != self._bundle_name:
              print("Requested scenario bundle to solve not known to PH solver server!")
              return None

          preprocess_bundle_constraints = self._problem_states.has_fixed_variables() or self._problem_states.has_freed_variables()
          # In the case of bundles, clearing these statuses was delayed in _preprocess_scenario_instance so we would no when to preprocess
          # the bundle constraints. Go ahead and clear them now
          self._problem_states.clear_fixed_variables()
          self._problem_states.clear_freed_variables()

          solving_standard_objective = True
          for scenario_name in self._instances:
              if (self._problem_states.has_ph_objective_weight_terms[scenario_name]) or \
                 (self._problem_states.has_ph_objective_proximal_terms[scenario_name]):
                  solving_standard_objective = False
                  break

          if solving_standard_objective is False:
              
              # restore the original EF objective.
              bundle_ef_objective_data = find_active_objective(self._bundle_ef_instance) 
              bundle_ef_objective_data.expr = self._original_bundle_objective

              # augment the EF objective with the PH penalty terms for each composite scenario.
              scenario_bundle = self._scenario_tree.get_bundle(self._bundle_name)
              for scenario_name in scenario_bundle._scenario_names:
                  scenario = self._scenario_tree.get_scenario(scenario_name)
                  new_lin_terms = self._problem_states.ph_linear_objective_expressions[scenario_name] 
                  new_quad_terms = self._problem_states.ph_quadratic_objective_expressions[scenario_name]
                  scenario = self._scenario_tree._scenario_map[scenario_name]
                  # TBD: THIS SHOULD NOT HAVE TO BE DONE EACH ITERATION - THE OBJECTIVE STRUCTURE DOES NOT CHANGE, AND THE LINEARIZATION 
                  #      CONSTRAINTS ARE ON THE SCENARIO INSTANCES.
                  bundle_ef_objective_data.expr += (scenario._probability / scenario_bundle._probability) * (new_lin_terms)
                  bundle_ef_objective_data.expr += (scenario._probability / scenario_bundle._probability) * (new_quad_terms)

              if self._solver.problem_format == ProblemFormat.nl:
                  ampl_preprocess_block_objectives(self._bundle_ef_instance)
                  if preprocess_bundle_constraints:
                      ampl_preprocess_block_constraints(self._bundle_ef_instance)
              else:
                  var_id_map = {}
                  canonical_preprocess_block_objectives(self._bundle_ef_instance, var_id_map)
                  if preprocess_bundle_constraints:
                      canonical_preprocess_block_constraints(self._bundle_ef_instance, var_id_map)

          results = self._solver.solve(self._bundle_ef_instance, 
                                       tee=tee, 
                                       keepfiles=keepfiles, 
                                       symbolic_solver_labels=symbolic_solver_labels, 
                                       suffixes=solver_suffixes)

          if self._verbose:
              print("Successfully solved scenario bundle="+object_name)

          if len(results.solution) == 0:
              results.write()
              raise RuntimeError("Solve failed for bundle="+object_name+"; no solutions generated")

          # load the results into the instances on the server side. this is non-trivial
          # in terms of computation time, for a number of reasons. plus, we don't want
          # to pickle and return results - rather, just variable-value maps.
          self._bundle_ef_instance.load(results)

          if self._verbose:
              print("Successfully loaded solution for bundle="+object_name)

          result = {}
          for scenario_name, scenario_instance in iteritems(self._instances):
              # extract the variable values into one big dictionary - one for each instance.
              variable_values = {}
              # TODO: This needs to recurse all blocks (i.e., use a recursive form of the generators)
              for variable_name, variable in iteritems(scenario_instance.active_subcomponents(Var)):
                  variable_values[variable_name] = variable.extract_values()
              result[scenario_name] = variable_values

          solve_method_result = (result, {})

      else:

          if object_name not in self._instances:
              print("Requested instance to solve not in PH solver server instance collection!")
              return None

          scenario_instance = self._instances[object_name]

          # the PH objective being enabled is a proxy for having a solution available from which to warm-start.
          if self._solver.warm_start_capable() and \
             ((self._problem_states.has_ph_objective_weight_terms[object_name]) or \
             (self._problem_states.has_ph_objective_proximal_terms[object_name])): 
             results = self._solver.solve(scenario_instance, 
                                          tee=tee, 
                                          warmstart=True, 
                                          keepfiles=keepfiles, 
                                          symbolic_solver_labels=symbolic_solver_labels, 
                                          suffixes=solver_suffixes) 
          else:
             results = self._solver.solve(scenario_instance, 
                                          tee=tee, 
                                          keepfiles=keepfiles, 
                                          symbolic_solver_labels=symbolic_solver_labels, 
                                          suffixes=solver_suffixes)

          if self._verbose:
              print("Successfully solved scenario instance="+object_name)

          if len(results.solution) == 0:
              results.write()
              raise RuntimeError("Solve failed for scenario="+object_name+"; no solutions generated")

          # load the results into the instances on the server side. this is non-trivial
          # in terms of computation time, for a number of reasons. plus, we don't want
          # to pickle and return results - rather, just variable-value maps.
          scenario_instance.load(results)

          if self._verbose:
              print("Successfully loaded solution for scenario="+object_name)

          # extract the variable values into one big dictionary. the dictionary
          # maps variable names to dictionaries of (index,value) pairs
          variable_values = {}
          for variable_name, variable in iteritems(scenario_instance.active_subcomponents(Var)):
              variable_values[variable_name] = variable.extract_values()

          # extract suffixes into a dictionary, mapping suffix names to dictionaries that in
          # turn map constraint names to (index, suffix-value) pairs.
          suffix_values = {}

          # NOTE: We are only presently extracting suffix values for constraints, as this whole
          #       interface is experimental. And probably inefficient. But it does work.
          for suffix_name in solver_suffixes:
              this_suffix_map = {}
              suffix = getattr(scenario_instance, suffix_name)
              # TODO: This needs to be over all blocks
              for constraint_name, constraint in iteritems(scenario_instance.active_subcomponents(Constraint)):
                  this_constraint_suffix_map = {}
                  for index, constraint_data in iteritems(constraint):
                      this_constraint_suffix_map[index] = suffix.getValue(constraint_data)
                  this_suffix_map[constraint_name] = this_constraint_suffix_map
              suffix_values[suffix_name] = this_suffix_map

          solve_method_result = (variable_values, suffix_values)

      return solve_method_result

    #
    # updating xbars only applies to scenarios - not bundles.
    #
    def update_xbars(self, scenario_name, new_xbars):

        if self._verbose:
            print("Received request to update xbars for scenario="+scenario_name)

        if self._initialized is False:
            raise RuntimeError("***PH solver server has not been initialized!")

        if scenario_name not in self._instances:
            print("ERROR: Received request to update weights for instance not in PH solver server instance collection!")
            return None
        scenario_instance = self._instances[scenario_name]

        # Flag the preprocessor if necessary
        if self._problem_states.has_ph_objective_proximal_terms[scenario_name]:
            self._problem_states.objective_updated[scenario_name] = True

        # Update the xbar paramter
        for xbar_parameter_name, xbar_update in iteritems(new_xbars):
            instance_xbar_parameter = scenario_instance.find_component(xbar_parameter_name)
            for index, new_value in iteritems(xbar_update):
                instance_xbar_parameter[index].value = new_value

    #
    # updating weights only applies to scenarios - not bundles.
    #
    def update_weights(self, scenario_name, new_weights):

        if self._verbose:
            print("Received request to update weights and averages for scenario="+scenario_name)

        if self._initialized is False:
            raise RuntimeError("***PH solver server has not been initialized!")

        if scenario_name not in self._instances:
            print("ERROR: Received request to update weights for instance not in PH solver server instance collection!")
            return None
        scenario_instance = self._instances[scenario_name]

        # Flag the preprocessor if necessary
        if self._problem_states.has_ph_objective_weight_terms[scenario_name]:
            self._problem_states.objective_updated[scenario_name] = True

        # Update the weights parameter
        for weight_parameter_name, weight_update in iteritems(new_weights):
            instance_weight_parameter = scenario_instance.find_component(weight_parameter_name)
            for index, new_value in iteritems(weight_update):
                instance_weight_parameter[index].value = new_value

    #
    # updating bounds is only applicable to scenarios.
    #
    def update_bounds(self, scenario_name, new_bounds):

        if self._verbose:
            print("Received request to update variable bounds for scenario="+scenario_name)

        if self._initialized is False:
            raise RuntimeError("***PH solver server has not been initialized!")

        if scenario_name not in self._instances:
            print("ERROR: Received request to update variable bounds for instance not in PH solver server instance collection!")
            return None
        scenario_instance = self._instances[scenario_name]

        for variable_name, bounds_update in iteritems(new_bounds):

            instance_variable = scenario_instance.find_component(variable_name)

            for index, new_value in iteritems(bounds_update):
                instance_variable[index].setlb(new_value[0])
                instance_variable[index].setub(new_value[1])                

    #
    # updating rhos is only applicable to scenarios.
    #
    def update_rhos(self, scenario_name, new_rhos):

        if self._verbose:
            print("Received request to update rhos for scenario="+scenario_name)

        if self._initialized is False:
            raise RuntimeError("***PH solver server has not been initialized!")

        if scenario_name not in self._instances:
            print("ERROR: Received request to update rhos for instance not in PH solver server instance collection!")
            return None
        scenario_instance = self._instances[scenario_name]

        # Flag the preprocessor if necessary
        if self._problem_states.has_ph_objective_proximal_terms[scenario_name]:
            self._problem_states.objective_updated[scenario_name] = True

        # update the rho parameters
        for rho_parameter_name, rho_update in iteritems(new_rhos):
            instance_rho_parameter = scenario_instance.find_component(rho_parameter_name)
            for index, new_value in iteritems(rho_update):
                instance_rho_parameter[index].value = new_value

    #
    # updating tree node statistics is bundle versus scenario agnostic.
    #

    def update_tree_node_statistics(self, scenario_name, new_node_minimums, new_node_maximums):

        if self._verbose:
            if self._bundle_name is not None:
                print("Received request to update tree node statistics for bundle="+self._bundle_name)
            else:
                print("Received request to update tree node statistics for scenario="+scenario_name)

        if self._initialized is False:
            raise RuntimeError("***PH solver server has not been initialized!")

        for tree_node_name, tree_node_minimums in iteritems(new_node_minimums):

            tree_node = self._scenario_tree._tree_node_map[tree_node_name]
            tree_node._minimums = tree_node_minimums

        for tree_node_name, tree_node_maximums in iteritems(new_node_maximums):

            tree_node = self._scenario_tree._tree_node_map[tree_node_name]
            tree_node._maximums = tree_node_maximums

    #
    # define the indicated suffix on my scenario instance. not dealing with bundles right now.
    #

    def define_import_suffix(self, scenario_name, suffix_name):

        if self._verbose:
            print("Received request to define import suffix="+suffix_name+" for scenario="+scenario_name)

        if self._initialized is False:
            raise RuntimeError("***PH solver server has not been initialized!")

        if scenario_name not in self._instances:
            print("ERROR: Received request to update rhos for instance not in PH solver server instance collection!")
            return None
        scenario_instance = self._instances[scenario_name]

        scenario_instance.add_component(suffix_name, Suffix(direction=Suffix.IMPORT))

    #
    # fix variables as instructed by the PH client.
    #
    def fix_variables(self, scenario_name, variables_to_fix):

        if self._verbose:
            print("Received request to fix variables for scenario="+scenario_name)

        if self._initialized is False:
            raise RuntimeError("***PH solver server has not been initialized!")

        if scenario_name not in self._instances:
            print("ERROR: Received request to update rhos for instance not in PH solver server instance collection!")
            return None
        scenario_instance = self._instances[scenario_name]

        self._problem_states.fixed_variables[scenario_name].extend(variables_to_fix)

        for variable_name, index in variables_to_fix:
           if self._verbose is True:
               print("Fixing variable="+variable_name+indexToString(index)+" on instance="+scenario_name)
           scenario_instance.find_component(variable_name)[index].fixed = True

    #
    # free variables as instructed by the PH client.
    #
    def free_variables(self, scenario_name, variables_to_free):

        if self._verbose:
            print("Received request to free variables for scenario="+scenario_name)

        if self._initialized is False:
            raise RuntimeError("***PH solver server has not been initialized!")

        if scenario_name not in self._instances:
            print("ERROR: Received request to update rhos for instance not in PH solver server instance collection!")
            return None
        scenario_instance = self._instances[scenario_name]

        self._problem_states.freed_variables[scenario_name].extend(variables_to_free)

        for variable_name, index in variables_to_free:
           if self._verbose is True:
               print("Freeing variable="+variable_name+indexToString(index)+" on instance="+scenario_name)
           # NOTE: If a variable was previously fixed, then by definition it had a valid value.
           #       Thus, whe we free the variable, we assign the value as not stale
           scenario_instance.find_component(variable_name)[index].fixed = False
           scenario_instance.find_component(variable_name)[index].stale = False

    def process(self, data):

        suspend_gc = PauseGC()

        result = None
        if data.action == "initialize":
           result = self.initialize(data.model_directory, 
                                    data.instance_directory, 
                                    data.object_name,
                                    data.solver_type, 
                                    data.solver_io,
                                    data.scenario_bundle_specification,
                                    data.create_random_bundles, 
                                    data.scenario_tree_random_seed,
                                    data.default_rho, 
                                    data.linearize_nonbinary_penalty_terms, 
                                    data.retain_quadratic_binary_terms,
                                    data.drop_proximal_terms,
                                    data.breakpoint_strategy,
                                    data.integer_tolerance,
                                    data.verbose)
        elif data.action == "solve":
            result = self.solve(data.name,
                                data.tee,
                                data.keepfiles,
                                data.symbolic_solver_labels,
                                data.solver_options, 
                                data.solver_suffixes)
        elif data.action == "add_ph_objective_proximal_terms":
            self.add_ph_objective_proximal_terms()
            result = True
        elif data.action == "add_ph_objective_weight_terms":
            self.add_ph_objective_weight_terms()
            result = True
        elif data.action == "form_standard_objective":
            self.form_standard_objective()
            result = True
        elif data.action == "load_bounds":
           if self._bundle_name is not None:
               for scenario_name, scenario_instance in iteritems(self._instances):
                   self.update_bounds(scenario_name, 
                                      data.new_bounds[scenario_name])
           else:
               self.update_bounds(data.name, 
                                  data.new_bounds)
           result = True           
        elif data.action == "load_rhos":
           if self._bundle_name is not None:
               for scenario_name, scenario_instance in iteritems(self._instances):
                   self.update_rhos(scenario_name, 
                                    data.new_rhos[scenario_name])
           else:
               self.update_rhos(data.name, 
                                data.new_rhos)
           result = True
        elif data.action == "fix_variables":
           if self._bundle_name is not None:
               for scenario_name, scenario_instance in iteritems(self._instances):
                   self.fix_variables(scenario_name, 
                                      data.fixed_variables[scenario_name])
           else:
               self.fix_variables(data.name, 
                                  data.fixed_variables)
           result = True
        elif data.action == "free_variables":
           if self._bundle_name is not None:
               for scenario_name, scenario_instance in iteritems(self._instances):
                   self.free_variables(scenario_name,
                                       data.freed_variables[scenario_name])
           else:
               self.free_variables(data.name, 
                                   data.freed_variables)
           result = True
        elif data.action == "load_weights":
           if self._bundle_name is not None:
               for scenario_name, scenario_instance in iteritems(self._instances):
                   self.update_weights(scenario_name, 
                                       data.new_weights[scenario_name])
           else:
               self.update_weights(data.name, 
                                   data.new_weights)
           result = True
        elif data.action == "load_xbars":
           if self._bundle_name is not None:
               for scenario_name, scenario_instance in iteritems(self._instances):
                   self.update_xbars(scenario_name, 
                                     data.new_xbars[scenario_name])
           else:
               self.update_xbars(data.name,
                                 data.new_xbars)
           result = True
        elif data.action == "load_tree_node_stats":
           self.update_tree_node_statistics(data.name, 
                                            data.new_mins, 
                                            data.new_maxs)
           result = True
        elif data.action == "define_import_suffix":
           self.define_import_suffix(data.name, 
                                     data.suffix_name)
           result = True
        else:
           raise RuntimeError("ERROR: Unknown action="+str(data.action)+" received by PH solver server")

        # a bit goofy - the Coopr Pyro infrastructure 
        return pickle.dumps(result)

#
# utility method to construct an option parser for ph arguments, to be
# supplied as an argument to the runph method.
#

def construct_options_parser(usage_string):

    parser = OptionParser()
    parser.add_option("--verbose",
                      help="Generate verbose output for both initialization and execution. Default is False.",
                      action="store_true",
                      dest="verbose",
                      default=False)
    parser.add_option("--profile",
                      help="Enable profiling of Python code.  The value of this option is the number of functions that are summarized.",
                      action="store",
                      dest="profile",
                      type="int",
                      default=0)
    parser.add_option("--disable-gc",
                      help="Disable the python garbage collecter. Default is False.",
                      action="store_true",
                      dest="disable_gc",
                      default=False)

    parser.usage=usage_string

    return parser

#
# Execute the PH solver server daemon.
#

def run_server(options):

    # just spawn the daemon!
    pyutilib.pyro.TaskWorkerServer(PHSolverServer)

def run(args=None):

    #
    # Top-level command that executes the ph solver server daemon.
    # This is segregated from phsolverserver to faciliate profiling.
    #

    #
    # Parse command-line options.
    #
    try:
        options_parser = construct_options_parser("phsolverserver [options]")
        (options, args) = options_parser.parse_args(args=args)
    except SystemExit:
        # the parser throws a system exit if "-h" is specified - catch
        # it to exit gracefully.
        return

    # for a one-pass execution, garbage collection doesn't make
    # much sense - so it is disabled by default. Because: It drops
    # the run-time by a factor of 3-4 on bigger instances.
    if options.disable_gc:
        gc.disable()
    else:
        gc.enable()

    if options.profile > 0:
        #
        # Call the main PH routine with profiling.
        #
        tfile = TempfileManager.create_tempfile(suffix=".profile")
        tmp = profile.runctx('run_server(options)',globals(),locals(),tfile)
        p = pstats.Stats(tfile).strip_dirs()
        p.sort_stats('time', 'cum')
        p = p.print_stats(options.profile)
        p.print_callers(options.profile)
        p.print_callees(options.profile)
        p = p.sort_stats('cum','calls')
        p.print_stats(options.profile)
        p.print_callers(options.profile)
        p.print_callees(options.profile)
        p = p.sort_stats('calls')
        p.print_stats(options.profile)
        p.print_callers(options.profile)
        p.print_callees(options.profile)
        TempfileManager.clear_tempfiles()
        ans = [tmp, None]
    else:
        #
        # Call the main PH routine without profiling.
        #
        ans = run_server(options)

    gc.enable()

    return ans

def main():
    try:
        run()
    except IOError:
        str = sys.exc_info()[1]
        print("IO ERROR:")
        print(str)
    except pyutilib.common.ApplicationError:
        str = sys.exc_info()[1]
        print("APPLICATION ERROR:")
        print(str)
    except RuntimeError:
        str = sys.exc_info()[1]
        print("RUN-TIME ERROR:")
        print(str)
    # pyutilib.pyro tends to throw SystemExit exceptions if things cannot be found or hooked
    # up in the appropriate fashion. the name is a bit odd, but we have other issues to worry 
    # about. we are dumping the trace in case this does happen, so we can figure out precisely
    # who is at fault.
    except SystemExit:
        str = sys.exc_info()[1]
        print("PH solver server encountered system error")
        print("Error: "+ str)
        print("Stack trace:")
        traceback.print_exc()
    except:
        print("Encountered unhandled exception")
        traceback.print_exc()

