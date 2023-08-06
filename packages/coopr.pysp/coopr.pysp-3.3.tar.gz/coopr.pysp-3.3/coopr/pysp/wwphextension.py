#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2009 Sandia Corporation.
#  this software is distributed under the bsd license.
#  under the terms of contract de-ac04-94al85000 with sandia corporation,
#  the u.s. government retains certain rights in this software.
#  for more information, see the coopr readme.txt file.
#  _________________________________________________________________________

import math
import os
import types

from pyutilib.component.core import *
from pyutilib.misc import flatten_tuple

from coopr.pysp import phextension
from coopr.pysp.phutils import *
from coopr.pysp.generators import scenario_tree_node_variables_generator
from coopr.pyomo.base import *

from coopr.pyomo.base.set_types import *

from six import iteritems, iterkeys
from six.moves import xrange

#=========================
class slam_priority_descend_compare(object):
    
    def __init__(self,suffix):
        assert suffix.type() is Suffix
        self._SlammingPriority = suffix

    def __call__(self,a, b):
        # used to sort the variable-suffix map for slamming priority
        value_a = self._SlammingPriority.getValue(a)
        value_b = self._SlammingPriority.getValue(b)
        return cmp(value_b, value_a)

#==================================================
class wwphextension(SingletonPlugin):

    implements (phextension.IPHExtension)

    def __init__(self, *args, **kwds):

        # TBD - migrate all of the self attributes defined on-the-fly
        #       in the post-post-initialization routine here!

        self._configuration_filename = None
        self._suffix_filename = None
        self._annotation_filename = None

#=========================
    def process_suffix_file(self, ph):

        # for each suffix, maintain an inverse map from the suffix name to a list of
        # objects with that suffix. an object could be a variable (Var) or a
        # variable value, depending on the resolution of the object for which the
        # suffix is defined.
        self._suffix_to_variable_map = {}

        self.slam_list = []

        if self._suffix_filename is None:
            return

        if os.path.exists(self._suffix_filename) is False:
            raise RuntimeError("***WW PH Extension: The suffix file "+self._suffix_filename+" either does not exist or cannot be read")

        print("WW PH Extension: Loading variable suffixes from file="+self._suffix_filename)

        reference_instance = ph._model_instance

        suffix_file = open(self._suffix_filename,'r')
        for line in suffix_file.readlines():
            line = line.strip()
            if len(line) > 0 and line[0] != '#':
                pieces = line.split()
                if len(pieces) != 3:
                    raise RuntimeError("Illegal line=["+line+"] encountered in ww ph extension suffix file="+self._suffix_filename+"; format is variable, suffix, suffix-value.")

                variable_string = pieces[0]
                suffix_name = pieces[1]
                suffix_value = pieces[2]

                # if the suffix isn't already an attribute of the instance, add it
                suffix_component = reference_instance.subcomponent(suffix_name)
                if (suffix_component is None) or (not suffix_component.type() is Suffix) or (not suffix_component.active is True):
                    setattr(reference_instance,suffix_name,Suffix(direction=Suffix.LOCAL,datatype=None))
                    suffix_component = getattr(reference_instance,suffix_name)

                # decide what type of suffix value we're dealing with.
                is_int = False
                is_bool = False
                converted_value = None
                try:
                    converted_value = bool(suffix_value)
                    is_bool = True
                except valueerror:
                    pass
                try:
                    converted_value = int(suffix_value)
                    is_int = True
                except ValueError:
                    pass

                if (is_int is False) and (is_bool is False):
                    raise RuntimeError("WW PH Extension unable to deduce type of data referenced in ww ph extension suffix file="+self._suffix_filename+"; value="+suffix_value+" for "+variable_name)

                # determine if we're dealing with complete variables or indexed variables.
                if isVariableNameIndexed(variable_string) is True:

                    variable_name, index_template = extractVariableNameAndIndex(variable_string)

                    # verify that the root variable exists and grab it.
                    if variable_name not in iterkeys(reference_instance.active_subcomponents(Var)):
                        raise RuntimeError("Unknown variable="+variable_name+" referenced in ww ph extension suffix file="+self._suffix_filename)
                    variable = reference_instance.active_subcomponents(Var)[variable_name]

                    # extract all "real", i.e., fully specified, indices matching the index template.
                    match_indices = extractVariableIndices(variable, index_template)

                    # there is a possibility that no indices match the input template.
                    # if so, let the user know about it.
                    if len(match_indices) == 0:
                        raise RuntimeError("No indices match template="+str(index_template)+" for variable="+variable_name)

                    # add the suffix to all variable values identified.
                    suffix_component.updateValues(((variable[index],converted_value) for index in match_indices))
                    for index in match_indices:

                        variable_value = variable[index]

                        # place the variable value in the suffix->variable map, for easy searching elsewhere in this plugin.
                        if suffix_name not in self._suffix_to_variable_map:
                            self._suffix_to_variable_map[suffix_name] = []
                        self._suffix_to_variable_map[suffix_name].append(variable_value)

                else:

                    # verify that the variable exists.
                    if variable_string not in iterkeys(reference_instance.active_subcomponents(Var)):
                        raise RuntimeError("Unknown variable="+variable_string+" referenced in ww ph extension suffix file="+self._suffix_filename)

                    variable = reference_instance.active_subcomponents(Var)[variable_string]

                    # 9/14/2009 - now forcing the user to explicit specify the full
                    # match template (e.g., "foo[*,*]") instead of just the variable
                    # name (e.g., "foo") to represent the set of all indices.

                    # if the variable is a singleton - that is, non-indexed - no brackets is fine.
                    # we'll just tag the var[None] variable value with the (suffix,value) pair.
                    if None not in variable._index:
                        raise RuntimeError("Illegal match template="+variable_string+" specified in ww ph extension suffix file="+self._suffix_filename)

                    # set the suffix on all variable values.
                    for index in variable:

                        variable_value = variable[index]

                        # set the suffix on the variable value.
                        suffix_component.setValue(variable_value, converted_value)

                        # place the variable in the suffix->variable map, for easy searching elsewhere in this plugin.
                        if suffix_name not in self._suffix_to_variable_map:
                            self._suffix_to_variable_map[suffix_name] = []
                        self._suffix_to_variable_map[suffix_name].append(variable_value)

#      print "pre-sort suffix->variable map:"
#      for key,value_list in self._suffix_to_variable_map.items():
#         print "key=",key,":",
#         for value in value_list:
#            print value.name,"",
#         print ""

        if "SlammingPriority" in self._suffix_to_variable_map:
            self.slam_list = self._suffix_to_variable_map["SlammingPriority"]

        if self.slam_list != []:
            suffix_component = reference_instance.subcomponent("SlammingPriority")
            if (suffix_component is None) or (not suffix_component.type() is Suffix) or (not suffix_component.active is True):
                raise ValueError("Unable to find Suffix component with name 'SlammingPriority' on reference instance %s" % (reference_instance.cname(True)))
            self.slam_list.sort(slam_priority_descend_compare(suffix_component))

#=========================
    def process_annotation_file(self, ph):
        # note: these suffixes can have a string value
        # very similar to suffixes, except for the following:
        # annotation names are from a restricted list, and
        # annotations can have various types that might depend on the name of the annotation
        # not all type checking will be done here, but some might be

        # note: "variable_value" is a misnomer: this thing is the variable

        self._annotation_to_variable_map = {}
        # obj effect families are special
        self._obj_family_to_variable_map = {}
        self._obj_family_normalized_rho = {}

        if self._annotation_filename is None:
            return

        AnnotationTypes = {}
        AnnotationTypes['going_price'] = None # Real
        AnnotationTypes['obj_effect_family_name'] = None # String
        AnnotationTypes['obj_effect_family_factor'] = None # Real
        AnnotationTypes['decision_hierarchy_level'] = None # non-negative int
        AnnotationTypes['feasibility_direction'] = ['down', 'up', 'either', 'None']
        AnnotationTypes['relax_int'] = None # int
        AnnotationTypes['reasonable_int'] = None # int
        AnnotationTypes['low_int'] = None # int

        if os.path.exists(self._annotation_filename) is False:
            raise RuntimeError("***WW PH Extension: The annotation file "+self._annotation_filename+" either does not exist or cannot be read")

        print("WW PH Extension: Loading variable annotations from file="+self._annotation_filename)

        reference_instance = ph._model_instance

        annotation_file = open(self._annotation_filename,'r')
        for line in annotation_file.readlines():
            line = line.strip()
            if len(line) > 0 and line[0] != '#':
                pieces = line.split()
                if len(pieces) != 3:
                    raise RuntimeError("Illegal line=["+line+"] encountered in ww ph extension annotation file="+self._annotation_filename+"; format is variable, annotation, annotation-value.")

                variable_string = pieces[0]
                annotation_name = pieces[1]
                annotation_value = pieces[2]

                # if the suffix isn't already an attribute of the instance, add it
                suffix_component = reference_instance.subcomponent(annotation_name)
                if (suffix_component is None) or (not suffix_component.type() is Suffix) or (not suffix_component.active is True):
                    setattr(reference_instance,annotation_name,Suffix(direction=Suffix.LOCAL,datatype=None))
                    suffix_component = getattr(reference_instance,annotation_name)

                # check for some input errors
                if annotation_name not in AnnotationTypes:
                    print("Error encountered.")
                    print("Here are the annotations that can be given (they are case sensitive):")
                    for i in AnnotationTypes:
                        print(i)
                    raise RuntimeError("Line=["+line+"] in ww ph extension annotation file="+self._annotation_filename+"; contains unknown annotation: "+annotation_name)

                # check for some more input errors
                if AnnotationTypes[annotation_name] is not None:
                    if annotation_value not in AnnotationTypes[annotation_name]:
                        raise RuntimeError("Line=["+line+"] in ww ph extension annotation file="+self._annotation_filename+"; contains unknown annotation value="+annotation_value+" for: "+annotation_name)

                # if this is a new obj effect family, then we need new maps
                if annotation_name == 'obj_effect_family_name':
                    if annotation_value not in self._obj_family_to_variable_map:
                        self._obj_family_to_variable_map[annotation_value] = []
                        self._obj_family_normalized_rho[annotation_value] = 0.0
                

                # determine if we're dealing with complete variables or indexed variables.
                if isVariableNameIndexed(variable_string) is True:

                    variable_name, index_template = extractVariableNameAndIndex(variable_string)

                    # verify that the root variable exists and grab it.
                    if variable_name not in iterkeys(reference_instance.active_subcomponents(Var)):
                        raise RuntimeError("Unknown variable="+variable_name+" referenced in ww ph extension annotation file="+self._annotation_filename)
                    variable = reference_instance.active_subcomponents(Var)[variable_name]

                    # extract all "real", i.e., fully specified, indices matching the index template.
                    match_indices = extractVariableIndices(variable, index_template)

                    # there is a possibility that no indices match the input template.
                    # if so, let the user know about it.
                    if len(match_indices) == 0:
                        raise RuntimeError("No indices match template="+str(index_template)+" for variable="+variable_name)

                    # add the annotation to all variable values identified.
                    for index in match_indices:

                        variable_value = variable[index]

                        # set the annotation on the variable value.
                        suffix_component.setValue(variable_value, annotation_value)

                        # place the variable value in the annotation->variable map, for easy searching elsewhere in this plugin.
                        if annotation_name not in self._annotation_to_variable_map:
                            self._annotation_to_variable_map[annotation_name] = []
                        self._annotation_to_variable_map[annotation_name].append(variable_value)
                        # if this is an obj effect family annotation, then we need a special map
                        if annotation_name == 'obj_effect_family_name':
                            self._obj_family_to_variable_map[annotation_value].append(variable_value)
                else:

                    # verify that the variable exists.
                    if variable_string not in iterkeys(reference_instance.active_subcomponents(Var)):
                        raise RuntimeError("Unknown variable="+variable_string+" referenced in ww ph extension annotation file="+self._annotation_filename)

                    variable = reference_instance.active_subcomponents(Var)[variable_string]

                    # 9/14/2009 - now forcing the user to explicit specify the full
                    # match template (e.g., "foo[*,*]") instead of just the variable
                    # name (e.g., "foo") to represent the set of all indices.

                    # if the variable is a singleton - that is, non-indexed - no brackets is fine.
                    # we'll just tag the var[None] variable value with the (annotation,value) pair.
                    if None not in variable._index:
                        raise RuntimeError("Illegal match template="+variable_string+" specified in ww ph extension annotation file="+self._annotation_filename)

                    # set the annotation on all variable values.
                    suffix_component.updateValues(((variable[index], annotation_value) for index in variable))
                    for index in variable:

                        variable_value = variable[index]

                        # place the variable in the annotation->variable map, for easy searching elsewhere in this plugin.
                        if annotation_name not in self._annotation_to_variable_map:
                            self._annotation_to_variable_map[annotation_name] = []
                        self._annotation_to_variable_map[annotation_name].append(variable_value)
                        # if this is an obj effect family annotation, then we need a special map
                        if annotation_name == 'obj_effect_family_name':
                            self._obj_family_to_variable_map[annotation_value].append(variable_value)

#==================================================
    def pre_ph_initialization(self,ph):
        # we don't need to intefere with PH initialization.
        pass
#==================================================

#==================================================
    def post_instance_creation(self, ph):
        # we don't muck with the instances.
        pass

#==================================================
    def post_ph_initialization(self, ph):

        # set up "global" record keeping.
        self.cumulative_discrete_fixed_count = 0
        self.cumulative_continuous_fixed_count = 0

        # we always track convergence of continuous variables, but we may not want to fix/slam them.
        self.fix_continuous_variables = False

        # there are occasions where we might want to fix any values at the end of the
        # run if the scenarios agree - even if the normal fixing criterion (e.g.,
        # converged for N iterations) don't apply. one example is when the term-diff
        # is 0, at which point you really do have a solution. currently only applies
        # to discrete variables.
        self.fix_converged_discrete_variables_at_exit = False

        # set up the mipgap parameters (zero means ignore)
        # note: because we lag one iteration, the final will be less than requested
        # initial and final refer to PH iteration 1 and PH iteration X, where
        # X is the iteration at which the convergence metric hits 0.
        self.Iteration0MipGap = 0.0
        self.InitialMipGap = 0.10
        self.FinalMipGap = 0.001

        # "Read" the defaults for parameters that control fixing
        # (these defaults can be overridden at the variable level)
        # for all six of these, zero means don't do it.
        self.Iter0FixIfConvergedAtLB = 0 # 1 or 0
        self.Iter0FixIfConvergedAtUB = 0  # 1 or 0
        self.Iter0FixIfConvergedAtNB = 0  # 1 or 0 (converged to a non-bound)
        # TBD: check for range errors for all six of these
        self.FixWhenItersConvergedAtLB = 10
        self.FixWhenItersConvergedAtUB = 10
        self.FixWhenItersConvergedAtNB = 12  # converged to a non-bound
        self.FixWhenItersConvergedContinuous = 0

        # "default" slamming parms:
        # TBD: These should get ovverides from suffixes
        # notice that for a particular var, all could be False
        self.CanSlamToLB = False
        self.CanSlamToMin = False
        self.CanSlamToAnywhere = True
        self.CanSlamToMax = False
        self.CanSlamToUB = False
        self.PH_Iters_Between_Cycle_Slams = 1  # zero means "slam at will"
        self.SlamAfterIter = len(ph._scenario_tree._stages[-1]._tree_nodes)

        # default params associated with fixing due to weight vector oscillation.
        self.CheckWeightOscillationAfterIter = 0
        self.FixIfWeightOscillationCycleLessThan = 10        

        # flags enabling various rho computation schemes.
        self.ComputeRhosWithSEP = False

        self.CycleLengthSlamThreshold = len(ph._scenario_tree._stages[-1]._tree_nodes)
        self.W_hash_history_len = max(100, self.CycleLengthSlamThreshold+1)

        self.ReportPotentialCycles = 0 # do I report potential cycles, i.e., those too short to base slamming on?

        # end of parms

        self._last_slam_iter = -1    # dynamic

        # constants for W vector hashing (low cost rand() is all we need)
        # note: July 09, dlw is planning to eschew pre-computed random vector
        # another note: the top level reset is OK, but really it should
        #   done way down at the index level with a serial number (stored)
        #   to avoid correlated hash errors
        # the hash seed was deleted in 1.1 and we seed with the
        self.W_hash_seed = 17  # we will reset for dynamic rand vector generation
        self.W_hash_rand_val = self.W_hash_seed # current rand
        self.W_hash_a = 1317       # a,b, and c are for a simple generator
        self.W_hash_b = 27699
        self.W_hash_c = 131072  # that period should be usually long enough for us!
                                # (assuming fewer than c scenarios)

        reference_instance = ph._model_instance
        # if the suffix isn't already an attribute of the instance, add it
        suffix_component = reference_instance.subcomponent("my_stage")
        if (suffix_component is None) or (not suffix_component.type() is Suffix) or (not suffix_component.active is True):
            setattr(reference_instance,"my_stage",Suffix(direction=Suffix.LOCAL,datatype=None))
            suffix_component = getattr(reference_instance,"my_stage")

        # set up tree storage for statistics that we care about tracking.
        for stage in ph._scenario_tree._stages[:-1]:

            for tree_node in stage._tree_nodes:

                # we're adding a lot of statistics / tracking data to each tree node.
                # these are all maps from variable name to a parameter that tracks the corresponding information.
                tree_node._num_iters_converged = {}
                tree_node._last_converged_val = {}
                tree_node._w_hash = {}
                tree_node._w_sign_vector = {} # sign vector for weights at the last PH iteration
                tree_node._w_last_sign_flip_iter = {} # the number of iterations since the last flip in the sign (TBD - of any scenario in the vector)?                
                tree_node._fixed_var_flag = {}

                for variable_name, (reference_variable, index_template) in iteritems(stage._variables):

                    variable_indices = tree_node._variable_indices[variable_name]
                    tree_node._num_iters_converged[reference_variable.name] = dict((index,0) for index in variable_indices)
                    # need to know to what value we have most recently converged
                    # GAH: Why is this initialized to 0.5?
                    tree_node._last_converged_val[reference_variable.name] = dict((index,0.5) for index in variable_indices)
                    # need to know to what has been fixed
                    tree_node._fixed_var_flag[reference_variable.name] = dict((index,False) for index in variable_indices)
                    # now make the w hash value storage array
                    tree_node._w_hash[reference_variable.name] = dict(((index,ph_iter),0) for index in variable_indices \
                                                                                          for ph_iter in ph._iteration_index_set)

                    # the following are easier - we aren't maintaining history.
                    tree_node._w_sign_vector[reference_variable.name] = {}
                    tree_node._w_last_sign_flip_iter[reference_variable.name] = {}
                    tree_node._w_sign_vector[reference_variable.name] = dict((index,[]) for index in variable_indices)
                    tree_node._w_last_sign_flip_iter[reference_variable.name] = dict((index,0) for index in variable_indices)

                    # JPW has no idea why the following code block is here, or if it is necessary.
                        # IMPT: it has bitten us before in this plug-in, so I'll state the obvious:
                        #       variable values in the last stage of a stochastic program will *not*
                        #       have a defined _stage attribute.
                        # NOTE: the use of the reference variable here, in contrast to a instance-specific
                        #       variable, is potentially dangerous.
                    suffix_component.updateValues(((reference_variable[index],stage) for index in variable_indices))


        if self._configuration_filename is not None:
            if os.path.exists(self._configuration_filename) is True:
                print("WW PH Extension: Loading user-specified configuration from file=" + self._configuration_filename)
                try:
                    # TODO: execfile is gone in py3k, but the following did not work in ph.py for load cfg files. It may or
                    #       may not work here
                    #exec(compile(open(self._configuration_filename).read(),self._configuration_filename,'exec'),globals(), locals())
                    execfile(self._configuration_filename)
                except:
                    raise RuntimeError("Failed to load WW PH configuration file="+self._configuration_filename)
            else:
                raise RuntimeError("***WW PH Extension: The configuration file "+self._configuration_filename+" either does not exist or cannot be read")
        else:
            print("WW PH Extension: No user-specified configuration file supplied - using defaults")

        # process any suffix and/or annotation data, if they exists.
        self.process_suffix_file(ph)
        self.process_annotation_file(ph)

        # set up the mip gap for iteration 0.
        if self.Iteration0MipGap > 0.0:
            print("Setting mipgap to "+str(self.Iteration0MipGap))
            ph._mipgap = self.Iteration0MipGap

#==================================================
    def post_iteration_0_solves(self, ph):

        # Collect possible existing Suffix components that we will check inside the next loop
        Iter0FixIfConvergedAtLB = ph._model_instance.subcomponent('Iter0FixIfConvergedAtLB')
        if (Iter0FixIfConvergedAtLB is None) or (not Iter0FixIfConvergedAtLB.type() is Suffix) or (not Iter0FixIfConvergedAtLB.active is True):
            Iter0FixIfConvergedAtLB = None
        Iter0FixIfConvergedAtUB = ph._model_instance.subcomponent('Iter0FixIfConvergedAtUB')
        if (Iter0FixIfConvergedAtUB is None) or (not Iter0FixIfConvergedAtUB.type() is Suffix) or (not Iter0FixIfConvergedAtUB.active is True):
            Iter0FixIfConvergedAtUB = None
        Iter0FixIfConvergedAtNB = ph._model_instance.subcomponent('Iter0FixIfConvergedAtNB')
        if (Iter0FixIfConvergedAtNB is None) or (not Iter0FixIfConvergedAtNB.type() is Suffix) or (not Iter0FixIfConvergedAtNB.active is True):
            Iter0FixIfConvergedAtNB = None
        CostForRho = ph._model_instance.subcomponent('CostForRho')
        if (CostForRho is None) or (not CostForRho.type() is Suffix) or (not CostForRho.active is True):
            CostForRho = None

        for stage in ph._scenario_tree._stages[:-1]:

            for tree_node in stage._tree_nodes:

                for variable_name, (variable, index_template) in iteritems(stage._variables):

                    variable_type = variable.domain

                    variable_indices = tree_node._variable_indices[variable_name]

                    for index in variable_indices:

                        # determine if this index is used - otherwise, don't waste time
                        # fixing and cycle checking. for one, the code will crash :-) with
                        # none values during the cycle checking computation!

                        is_used = True # until proven otherwise
                        node_average = tree_node._averages[variable_name][index]
                        deviation_from_average = 0.0
                        for scenario in tree_node._scenarios:
                            instance = ph._instances[scenario._name]
                            var_value = getattr(instance,variable_name)[index]
                            if var_value.stale is True:
                                is_used = False
                            # IMPT: This is wrong - we really need the absolute tree node probability for this to work in the multi-stage case.
                            scenario_probability = ph._scenario_tree._scenario_map[scenario._name]._probability
                            deviation_from_average += (scenario_probability * math.fabs(var_value.value - node_average))
                        deviation_from_average /= tree_node._conditional_probability

                        if is_used is True:

                            # unlikely, but variables might be fixed even at this stage, depending on
                            # what weirdness users do prior to the iteration 0 solves.
                            instance_fixed_count = 0
                            for scenario in tree_node._scenarios:
                                instance = ph._instances[scenario._name]
                                if getattr(instance,variable_name)[index].fixed is True:
                                    instance_fixed_count += 1
                            if ((instance_fixed_count > 0) and (instance_fixed_count < len(tree_node._scenarios))):
                                raise RuntimeError("Variable="+variable_name+str(index)+" is fixed in "+str(instance_fixed_count)+" scenarios, but less than the number of scenarios at tree node="+tree_node._name)

                            if instance_fixed_count == 0:

                                if isinstance(variable_type, IntegerSet) or isinstance(variable_type, BooleanSet):
                                    node_min = self.Int_If_Close_Enough(ph, tree_node._minimums[variable_name][index])
                                    node_max = self.Int_If_Close_Enough(ph, tree_node._maximums[variable_name][index])

                                    # update convergence prior to checking for fixing.
                                    self._int_convergence_tracking(ph, tree_node, variable_name, index, node_min, node_max)
                                    attrvariable = ph._model_instance.active_subcomponents(Var)[variable_name]
                                    attrvarvalue = attrvariable[index]

                                    lb = None
                                    if not Iter0FixIfConvergedAtLB is None:
                                        lb = Iter0FixIfConvergedAtLB.getValue(attrvarvalue)
                                    if lb is None:
                                        lb = self.Iter0FixIfConvergedAtLB

                                    ub = None
                                    if not Iter0FixIfConvergedAtUB is None:
                                        ub = Iter0FixIfConvergedAtUB.getValue(attrvarvalue)
                                    if ub is None:
                                        ub = self.Iter0FixIfConvergedAtUB

                                    nb = None
                                    if not Iter0FixIfConvergedAtNB is None:
                                        nb = Iter0FixIfConvergedAtNB.getValue(attrvarvalue)
                                    if nb is None:
                                        nb = self.Iter0FixIfConvergedAtNB

                                    if self._should_fix_discrete_due_to_conv(tree_node, variable, index, lb, ub, nb):
                                        self._fix_var(ph, tree_node, variable, index, node_min)
                                    elif self.W_hash_history_len > 0:   # if not fixed, then hash - no slamming at iteration 0
                                        self._w_history_accounting(ph, tree_node, variable_name, index) # obviously not checking for cycles at iteration 0!

                                else:

                                    node_min = tree_node._minimums[variable_name][index]
                                    node_max = tree_node._maximums[variable_name][index]

                                    self._continuous_convergence_tracking(ph, tree_node, variable_name, index, node_min, node_max)

                            if (self.ComputeRhosWithSEP is True) and (not CostForRho is None):

                                numerator = 1.0

                                node_min = self.Int_If_Close_Enough(ph, tree_node._minimums[variable_name][index])
                                node_max = self.Int_If_Close_Enough(ph, tree_node._maximums[variable_name][index])

                                if isinstance(variable_type, IntegerSet) or isinstance(variable_type, BooleanSet):
                                    denominator = max(node_max - node_min + 1, 1)
                                else:
                                    denominator = max(deviation_from_average, 1)

                                # CostForRho are the costs to be used as the numerator in the rho computation below.
                                reference_variable = getattr(ph._model_instance, variable_name)
                                rho_cost = CostForRho.getValue(reference_variable[index])
                                if rho_cost is not None:
                                    ph.setRhoAllScenarios(variable[index], rho_cost * numerator / denominator)

# jpw: not sure if we care about cycle detection in continuous variables?
#                           if self.W_hash_history_len > 0:
#                              self._w_history_accounting(ph, tree_node, variable_name, index)


#==================================================
    def post_iteration_0(self, ph):

        self._met0 = ph._converger.lastMetric()

        if (self.InitialMipGap > 0) and (self.FinalMipGap >= 0) and (self.InitialMipGap > self.FinalMipGap):
            gap = self.InitialMipGap
            print("Setting mipgap to "+str(gap))
            ph._mipgap = gap

#==================================================

    def pre_iteration_k_solves(self, ph):
        """ Called immediately before the iteration k solves!"""
        # we don't muck with the PH objectives
        pass

#==================================================
    def post_iteration_k_solves(self, ph):

        # Collect possible existing Suffix components that we will check inside the next loop
        FixWhenItersConvergedAtLB = ph._model_instance.subcomponent('FixWhenItersConvergedAtLB')
        if (FixWhenItersConvergedAtLB is None) or (not FixWhenItersConvergedAtLB.type() is Suffix) or (not FixWhenItersConvergedAtLB.active is True):
            FixWhenItersConvergedAtLB = None
        FixWhenItersConvergedAtUB = ph._model_instance.subcomponent('FixWhenItersConvergedAtUB')
        if (FixWhenItersConvergedAtUB is None) or (not FixWhenItersConvergedAtUB.type() is Suffix) or (not FixWhenItersConvergedAtUB.active is True):
            FixWhenItersConvergedAtUB = None
        FixWhenItersConvergedAtNB = ph._model_instance.subcomponent('FixWhenItersConvergedAtNB')
        if (FixWhenItersConvergedAtNB is None) or (not FixWhenItersConvergedAtNB.type() is Suffix) or (not FixWhenItersConvergedAtNB.active is True):
            FixWhenItersConvergedAtNB = None

        for stage, tree_node, variable, index, is_fixed, is_stale in scenario_tree_node_variables_generator(ph._scenario_tree, ph._instances, includeLastStage=False):

            # if the variable is stale, don't waste time fixing and cycle checking. for one,
            # the code will crash :-) due to None values observed during the cycle checking computation.
            if (is_stale is False) and (is_fixed is False):

                if isinstance(variable.domain, IntegerSet) or isinstance(variable.domain, BooleanSet):
                    node_min = self.Int_If_Close_Enough(ph, tree_node._minimums[variable.name][index])
                    node_max = self.Int_If_Close_Enough(ph, tree_node._maximums[variable.name][index])

                    # update convergence prior to checking for fixing.
                    self._int_convergence_tracking(ph, tree_node, variable.name, index, node_min, node_max)

                    # now check on permissions to converge to various placed (e.g., lb is lb permission)
                    attrvariable = ph._model_instance.active_subcomponents(Var)[variable.name]
                    attrvarvalue = attrvariable[index]

                    lb = None
                    if not FixWhenItersConvergedAtLB is None:
                        lb = FixWhenItersConvergedAtLB.getValue(attrvarvalue)
                    if lb is None:
                        lb = self.FixWhenItersConvergedAtLB

                    ub = None
                    if not FixWhenItersConvergedAtUB is None:
                        ub = FixWhenItersConvergedAtUB.getValue(attrvarvalue)
                    if ub is None:
                        ub = self.FixWhenItersConvergedAtUB

                    nb = None
                    if not FixWhenItersConvergedAtNB is None:
                        nb = FixWhenItersConvergedAtNB.getValue(attrvarvalue)
                    if nb is None:
                        nb = self.FixWhenItersConvergedAtNB

                    if self._should_fix_discrete_due_to_conv(tree_node, variable, index, lb, ub, nb):
                            
                        self._fix_var(ph, tree_node, variable, index, node_min)
                        
                    else: # if not fixed, then hash and slam as necessary.

                        if self.W_hash_history_len > 0:
                            self._w_history_accounting(ph, tree_node, variable.name, index)
                            computed_cycle_length,msg = self.hash_hit_len(ph, tree_node, variable.name, index, False)
                            if (computed_cycle_length >= self.CycleLengthSlamThreshold) and ((ph._current_iteration - self._last_slam_iter) > self.PH_Iters_Between_Cycle_Slams):
                                # TBD: we may not want to slam immediately - it may disappear on it's own after a few iterations, depending on what other variables do.
                                # note: we are *not* slamming the offending variable, but a selected variable
                                if index is None:
                                    print("Cycle issue detected with variable="+variable.name)
                                else:
                                    print("Cycle issue detected with variable="+variable.name+"["+str(index)+"]")
                                print(msg)
                                print("Cycle length exceeds iteration slamming threshold="+str(self.CycleLengthSlamThreshold)+"; choosing a variable to slam")

                                self._pick_one_and_slam_it(ph)
                            elif (computed_cycle_length > 1) and (computed_cycle_length < self.CycleLengthSlamThreshold):
                                # there was a (potential) cycle, but the slam threshold wasn't reached.
                                if self.ReportPotentialCycles is True:
                                    if index is None:
                                        print("Cycle issue detected with variable="+variable.name)
                                    else:
                                        print("Cycle issue detected with variable="+variable.name+"["+str(index)+"]")
                                    print(msg)
                                    print("Taking no action to break cycle - length="+str(computed_cycle_length)+" does not exceed slam threshold="+str(self.CycleLengthSlamThreshold))
                            elif (computed_cycle_length >= self.CycleLengthSlamThreshold) and ((ph._current_iteration - self._last_slam_iter) > self.PH_Iters_Between_Cycle_Slams):
                                # we could have slammed, but we recently did and are taking a break to see if things settle down on their own.
                                if index is None:
                                    print("Cycle issue detected with variable="+variable.name)
                                else:
                                    print("Cycle issue detected with variable="+variable.name+"["+str(index)+"]")
                                print(msg)
                                print("Taking no action to break cycle - length="+str(computed_cycle_length)+" does exceed slam threshold="+str(self.CycleLengthSlamThreshold)+ \
                                    ", but another variable was slammed within the past "+str(self.PH_Iters_Between_Cycle_Slams)+" iterations")
                else:

                    # obviously don't round in the continuous case.
                    node_min = tree_node._minimums[variable.name][index]
                    node_max = tree_node._maximums[variable.name][index]

                    # update w statistics for whatever nefarious purposes are enabled.
                    if self.W_hash_history_len > 0:   
                        self._w_history_accounting(ph, tree_node, variable.name, index)                                                               

                    # update convergence prior to checking for fixing.
                        self._continuous_convergence_tracking(ph, tree_node, variable.name, index, node_min, node_max)

                    if self._should_fix_continuous_due_to_conv(tree_node, variable, index):
                        # fixing to max value for safety (could only be an issue due to tolerances).
                        self._fix_var(ph, tree_node, variable, index, node_max)
                        # note: we currently don't slam continuous variables!

        # TBD: the 1 might need to be parameterized - TBD - the 1 should be the PH ITERATIONS BETWEEN CYCLE SLAMS
        if (ph._current_iteration > self.SlamAfterIter) and \
           ((ph._current_iteration - self._last_slam_iter) > self.PH_Iters_Between_Cycle_Slams) and \
           (ph._converger.isImproving(self.PH_Iters_Between_Cycle_Slams)):
            print("Slamming criteria are satisifed - accelerating convergence")
            self._pick_one_and_slam_it(ph)
            self._just_slammed_ = True
        else:
            self._just_slammed_ = False

        ### THIS IS EXPERIMENTAL - CODE MAY BELONG SOMEWHERE ELSE ###
        for stage, tree_node, variable, index, is_fixed, is_stale in scenario_tree_node_variables_generator(ph._scenario_tree, ph._instances, includeLastStage=False):

            last_flip_iter = tree_node._w_last_sign_flip_iter[variable.name][index]
            flip_duration = ph._current_iteration - last_flip_iter

            if (self.CheckWeightOscillationAfterIter > 0) and (ph._current_iteration >= self.CheckWeightOscillationAfterIter):
                if (last_flip_iter is 0) or (flip_duration >= self.FixIfWeightOscillationCycleLessThan): 
                    pass
                else:
                    if self._slam(ph, tree_node, variable, index) is True:
                        tree_node._w_last_sign_flip_iter[variable.name][index] = 0 
                        return            

#==================================================
    def post_iteration_k(self, ph):

        # note: we are lagging one iteration
        # linear
        if (self.InitialMipGap > 0 and self.FinalMipGap >= 0) and self.InitialMipGap > self.FinalMipGap:
            m0 = self._met0
            m = ph._converger.lastMetric()
            mlast = ph._converger._convergence_threshold
            g0 = self.InitialMipGap
            glast = self.FinalMipGap
            gap = ((m-m0)/(m0-mlast) + g0/(g0-glast))* (g0-glast)
            if gap > g0:
                print("***CAUTION: Setting mipgap to thresholded maximal initial mapgap value="+str(g0)+"; unthresholded value="+str(gap))
                gap = g0
            else:
                print("Setting mipgap to "+str(gap))
            ph._mipgap = gap


#==================================================
    def post_ph_execution(self, ph):

        if self.fix_converged_discrete_variables_at_exit is True:
            print("WW PH extension: Fixing all discrete variables that are converged at termination")
            self._fix_all_converged_discrete_variables(ph)

#=========================
    def Int_If_Close_Enough(self, ph, x):
        # if x is close enough to the nearest integer, return the integer
        # else return x
        if abs(round(x)-x) <= ph._integer_tolerance:
            return int(round(x))
        else:
            return x

#=========================
    def _int_convergence_tracking(self, ph, tree_node, variable_name, index, node_min, node_max):
        # keep track of cumulative iters of convergence to the same int
        if (node_min == node_max) and (type(node_min) is types.IntType):
            if node_min == tree_node._last_converged_val[variable_name][index]:
                tree_node._num_iters_converged[variable_name][index] = tree_node._num_iters_converged[variable_name][index] + 1
            else:
                tree_node._num_iters_converged[variable_name][index] = 1
                tree_node._last_converged_val[variable_name][index] = node_min
        else:
            tree_node._num_iters_converged[variable_name][index] = 0
            tree_node._last_converged_val[variable_name][index] = 0.5

#=========================
    def _continuous_convergence_tracking(self, ph, tree_node, variable_name, index, node_min, node_max):
        # keep track of cumulative iters of convergence to the same value within tolerance.
        if abs(node_max - node_min) <= ph._integer_tolerance:
            if abs(node_min - tree_node._last_converged_val[variable_name][index]) <= ph._integer_tolerance:
                tree_node._num_iters_converged[variable_name][index] = tree_node._num_iters_converged[variable_name][index] + 1
            else:
                tree_node._num_iters_converged[variable_name][index] = 1
                tree_node._last_converged_val[variable_name][index] = node_min
        else:
            tree_node._num_iters_converged[variable_name][index] = 0
            tree_node._last_converged_val[variable_name][index] = 0.2342343243223423 # TBD - avoid the magic constant!

#=========================
    def _w_history_accounting(self, ph, tree_node, variable_name, index):
        # do the w hash accounting work
        # we hash on the variable ph weights, and not the values; the latter may not shift for some time, while the former should.
        self.W_hash_rand_val = self.W_hash_seed

        new_sign_vector = []
        old_sign_vector = tree_node._w_sign_vector[variable_name][index]

        for scenario in tree_node._scenarios:
           instance = ph._instances[scenario._name]
           weight_parameter_name = "PHWEIGHT_"+variable_name
           weight_value = getattr(instance,weight_parameter_name)[index].value
           weight_sign = True
           if weight_value < 0.0:
               weight_sign = False
           tree_node._w_hash[variable_name][index,ph._current_iteration] = tree_node._w_hash[variable_name][index,ph._current_iteration] + weight_value * self.W_hash_rand_val
           new_sign_vector.append(weight_sign)
           self.W_hash_rand_val = (self.W_hash_b + self.W_hash_a * self.W_hash_rand_val) % self.W_hash_c

        num_flips = 0
        for i in xrange(0,len(old_sign_vector)):
           if new_sign_vector[i] != old_sign_vector[i]:
              num_flips += 1

        tree_node._w_sign_vector[variable_name][index] = new_sign_vector

        if num_flips >= 1:
           tree_node._w_last_sign_flip_iter[variable_name][index] = ph._current_iteration        

#=========================
    def dump_w_hash(self, ph, tree_node, stage):
        # debug code
        print("Stage= "+stage._name+"  tree node= "+tree_node._name)
        print("PH Iteration      Variable                          PH Weight Hash Value")
        for variable_name, (variable, index_template) in iteritems(stage._variables):

            variable_type = variable.domain

            variable_indices = tree_node._variable_indices[variable_name]

            # TBD - should we cycle-detect on continuous vars?
            if isinstance(variable_type, IntegerSet) or isinstance(variable_type, BooleanSet):
                for index in variable_index:
                    print("%4d        %50ls %20.5f" % (ph._current_iteration, tree_node._w_hash[variable_name][index,ph._current_iteration], tree_node._w_hash[variable_name][index,ph._current_iteration]))

#=========================
    def hash_hit_len(self, ph, tree_node, variable_name, index, report_possible_cycles):
        # return cycles back to closest hash hit for hashval or 0 if no hash hit

        # if the values are converged, then don't report a cycle - often, the weights at convergence are 0s, and even
        # if they aren't, they won't move if the values are uniform.
        if (tree_node._num_iters_converged[variable_name][index] == 0) and (tree_node._fixed_var_flag[variable_name][index] is False):
            current_hash_value = None
            current_hash_value = tree_node._w_hash[variable_name][index,ph._current_iteration]
            # scan starting from the farthest point back in history to the closest - this is required to
            # identify the longest possible cycles, which is what we want.
            for i in xrange(max(ph._current_iteration - self.W_hash_history_len - 1, 1), ph._current_iteration - 1, 1):
                this_hash_value = None
                this_hash_value = tree_node._w_hash[variable_name][index,i]
                if abs(this_hash_value - current_hash_value) <= ph._integer_tolerance:
                    if report_possible_cycles is True:
                        print("Possible cycle detected via PH weight hashing - variable="+variable_name+indexToString(index)+" node="+ tree_node._name)
                    msg = "Current hash value="+str(current_hash_value)+" matched (within tolerance) hash value="+str(this_hash_value)+" found at PH iteration="+str(i)+"; cycle length="+str(ph._current_iteration - i)
                    return ph._current_iteration - i, msg
        return 0, ""

#=========================
    def _fix_var(self, ph, tree_node, variable, index, fix_value):
        # fix the variable, account for it and maybe output some trace information
        # note: whether you fix at current values or not can severly impact feasibility later
        # in the game. my original thought was below - but that didn't work out. if you
        # make integers, well, integers, all appears to be well.
        # IMPT: we are leaving the values for individual variables alone, at potentially
        #       smallish and heterogeneous values. if we fix/round, we run the risk of
        #       infeasibilities due to numerical issues. the computed value below is
        #       strictly for output purposes. dlw note: as of aug 1 '09,
        #       node_min and node_max should be
        #       int if they should be (so to speak)

        fixing_reported = False # to track whether you have already output the fix message for one scenario.

        for scenario in tree_node._scenarios:

            instance = ph._instances[scenario._name]
            
            variable_data = getattr(instance,variable.name)[index]
            variable_data.fixed = True
            variable_data.value = fix_value
            tree_node._fixed_var_flag[variable.name][index] = True

            variable_type = variable.domain

            if fixing_reported is False:
                print("Fixing variable="+variable.name+indexToString(index)+" at tree node="+tree_node._name+" to value="+str(fix_value)+"; converged for "+str(tree_node._num_iters_converged[variable.name][index])+" iterations")
                fixing_reported = True
                if isinstance(variable_type, IntegerSet) or isinstance(variable_type, BooleanSet):
                    self.cumulative_discrete_fixed_count = self.cumulative_discrete_fixed_count + 1
                else:
                    self.cumulative_continuous_fixed_count = self.cumulative_continuous_fixed_count + 1

            # record the specific variable fixed for the PH client.
            ph._problem_states.fixed_variables[scenario._name].append((variable.name, index))

#=========================
    # the last 3 input arguments are the number of iterations the variable is required to
    # be at the respective bound (or lack thereof) before fixing can be initiated.
    def _should_fix_discrete_due_to_conv(self, tree_node, variable, index, lb_iters, ub_iters, nb_iters):
        # return True if this should be fixed due to convergence
        variable_name = variable.name

        # jpw: i don't think this logic is correct - shouldn't "non-bound" be moved after the lb/ub checks - this doesn't check a bound!
        # dlw reply: i meant it to mean "without regard to bound" so i have updated the document
        if nb_iters > 0 and tree_node._num_iters_converged[variable_name][index] >= nb_iters:
            return True
        else:
            # there is a possibility that the variable doesn't have a bound specified, in which
            # case we should obviously ignore the corresponding lb_iters/ub_iters/nb_iters - which
            # should be none as well!
            lb = None
            ub = None
            if variable[index].lb is not None:
                lb = value(variable[index].lb)
            if variable[index].ub is not None:
                ub = value(variable[index].ub)
            conval = tree_node._last_converged_val[variable_name][index]
            # note: if they are converged node_max == node_min
            if (lb is not None) and (lb_iters > 0) and (tree_node._num_iters_converged[variable_name][index] >= lb_iters) and (conval == lb):
                return True
            elif (ub is not None) and (ub_iters > 0) and (tree_node._num_iters_converged[variable_name][index] >= ub_iters) and (conval == ub):
                return True
        # if we are still here, nothing triggered fixing
        return False

#=========================
    def _should_fix_continuous_due_to_conv(self, tree_node, variable, index):

        if self.fix_continuous_variables is True:
            if self.FixWhenItersConvergedContinuous > 0 and tree_node._num_iters_converged[variable.name][index] >= self.FixWhenItersConvergedContinuous:
                return True

        # if we are still here, nothing triggered fixing
        return False

#=========================
    def _slam(self, ph, tree_node, variable, index):
        # this function returns a boolean indicating if it slammed
        # TBD in the distant future: also: slam it to somewhere it sort of wants to go
        # e.g., the anywhere case could be to the mode
        #   or if more than one dest is True, pick the one closest to the average
        #   as of sept 09, it is written with the implicit assumption that only one
        #   destination is True or that if not, then min/max trumps lb/ub and anywhere trumps all

        fix_value = False  # assume the worst
        variable_type = variable.domain
        variable_name = variable.name
        if isinstance(variable_type, IntegerSet) or isinstance(variable_type, BooleanSet):
            node_min = self.Int_If_Close_Enough(ph, tree_node._minimums[variable_name][index])
            node_max = self.Int_If_Close_Enough(ph, tree_node._maximums[variable_name][index])
            anywhere = round(tree_node._averages[variable.name][index])
        else:
            node_min = tree_node._minimums[variable_name][index]
            node_max = tree_node._maximums[variable_name][index]
            anywhere = tree_node._averages[variable.name][index]

        slam_basis_string = ""
        if self.CanSlamToLB is True:
            fix_value = value(variable[index].lb)
            slam_basis_string = "lower bound"
        if self.CanSlamToMin is True:
            fix_value = node_min
            slam_basis_string = "node minimum"
        if self.CanSlamToUB is True:
            fix_value = value(variable[index].ub)
            slam_basis_string = "upper bound"
        if self.CanSlamToMax is True:
            fix_value = node_max
            slam_basis_string = "node maximum"
        if self.CanSlamToAnywhere is True:
            fix_value = anywhere
            slam_basis_string = "node average (anywhere)"
        if fix_value is False:
            print("Warning: Not allowed to slam variable="+variable.name+str(index)+" at tree node="+tree_node._name)
            return False
        else:
            print("Slamming variable="+variable.name+indexToString(index)+" at tree node="+tree_node._name+" to value="+str(fix_value)+"; value="+slam_basis_string)
            self._fix_var(ph, tree_node, variable, index, fix_value)
            return True

#=========================
    def _pick_one_and_slam_it(self, ph):

        reference_instance = ph._model_instance
        my_stage_suffix = reference_instance.subcomponent("my_stage")
        if (my_stage_suffix is None) or (not my_stage_suffix.type() is Suffix) or (not my_stage_suffix.active is True):
            my_stage_suffix = None

        for vl in self.slam_list:
            variable_string = str(vl)
            full_index = None # JPW is not entirely sure of python scoping rules, so I'm declaring this outside of the if-then block.
            variable_name = None
            if isVariableNameIndexed(variable_string) is True:
                pieces = variable_string.split('[')
                variable_name = pieces[0].strip()
                full_index = pieces[1].rstrip(']')
                # the full_index is a string - tuplize it!
                full_index = tupleizeIndexString(full_index)
            else:
                variable_name = variable_string
                full_index = None

            # verify that the root variable exists and grab it.
            if variable_name not in iterkeys(reference_instance.active_subcomponents(Var)):
                raise RuntimeError("Unknown variable="+variable_name+" referenced while slamming. ")
            variable = reference_instance.active_subcomponents(Var)[variable_name]

            didone = False;   # did we find at least one node to slam in?
            # it is possible (even likely) that the slam list contains variable values that
            # reside in the final stage - which, because of the initialization loops in
            # the post_ph_initialization() method, will not have a _stage attribute defined.
            # check for the presence of this attribute and skip if not present, as it
            # doesn't make sense to slam variable values in the final stage anyway.
            variable_stage = None
            if my_stage_suffix is not None:
                variable_stage = my_stage_suffix.getValue(variable[full_index])
            if variable_stage is not None: # None => the variable isn't used.
                for tree_node in variable_stage._tree_nodes:
                    # determine if the variable is already fixed (the trusting version...).
                    if tree_node._fixed_var_flag[variable_name][full_index] is False:
                        didone = self._slam(ph, tree_node, variable, full_index)
                if didone:
                    self._last_slam_iter = ph._current_iteration
                    return

        print("Warning: Nothing free with a non-zero slam priority - no variable will be slammed")
        # DLW says: Hey, look at this: if we were to start deleting from the slam list this would be wrong."
        if len(self.slam_list) == 0:
            print("   (No Slamming Priorities were specified in a suffix file.)")

#==========================
# a simple utility to fix any discrete variables to their common value, assuming they
# are at a common value
#==========================

    def _fix_all_converged_discrete_variables(self, ph):

        num_variables_fixed = 0

        for stage, tree_node, variable, index, is_fixed, is_stale in scenario_tree_node_variables_generator(ph._scenario_tree, ph._instances, includeLastStage=False):

            # if the variable is stale, don't waste time fixing and cycle checking. for one,
            # the code will crash :-) due to None values observed during the cycle checking computation.
            if (is_stale is False) and (is_fixed is False):

                if isinstance(variable.domain, IntegerSet) or isinstance(variable.domain, BooleanSet):
                    node_min = self.Int_If_Close_Enough(ph, tree_node._minimums[variable.name][index])
                    node_max = self.Int_If_Close_Enough(ph, tree_node._maximums[variable.name][index])

                    if node_min == node_max:
                        self._fix_var(ph, tree_node, variable, index, node_min)
                        num_variables_fixed += 1

        print("Total number of variables fixed at PH termination due to convergence="+str(num_variables_fixed))
