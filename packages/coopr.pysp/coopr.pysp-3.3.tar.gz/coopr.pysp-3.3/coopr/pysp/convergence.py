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
import types
import copy
import os.path
import traceback
from math import fabs

from coopr.pyomo import *
from coopr.pysp.scenariotree import *

from six import iteritems, iterkeys

#
# This module contains a hierarchy of convergence "computers" for PH (or any
# other scenario-based decomposition strategy). Their basic function is to
# compute some measure of convergence among disparate scenario solutions,
# and to track the corresponding history of the metric. the sole inputs
# are a scenario tree and a (time-varying) set of instances (with solutions).
#

class ConvergenceBase(object):

    """ Constructor
        Arguments:
           convergence_threshold          numeric threshold at-or-below which a set of scenario solutions is considered converged. must be >= 0.0.
    """
    def __init__(self, *args, **kwds):

        # key is the iteration number, passed in via the update() method.
        self._metric_history = {}

        # the largest iteration key thus far - we assume continugous values from 0.
        self._largest_iteration_key = 0

        # at what point do I consider the scenario solution pool converged?
        self._convergence_threshold = 0.0

        for key in kwds:
            if key == "convergence_threshold":
                self._convergence_threshold = kwds[key]
            else:
                print("Unknown option=" + key + " specified in call to ConvergenceBase constructor")

    def reset(self):

        self._metric_history.clear()

    def lastMetric(self):

        if len(self._metric_history) == 0:
            raise RuntimeError("ConvergenceBase::lastMetric() invoked with 0-length history")

        assert max(iterkeys(self._metric_history)) == self._largest_iteration_key
        return self._metric_history[self._largest_iteration_key]

    def update(self, iteration_id, ph, scenario_tree, instances):

        current_value = self.computeMetric(ph, scenario_tree, instances)
        self._metric_history[iteration_id] = current_value
        self._largest_iteration_key = max(self._largest_iteration_key, iteration_id)

    def computeMetric(self, ph, scenario_tree, solutions):

        raise NotImplementedError("ConvergenceBase::computeMetric() is an abstract method")

    def isConverged(self, ph):

        if (ph._total_discrete_vars > 0) and (ph._total_discrete_vars == ph._total_fixed_discrete_vars):
            return True
        else:
            return self.lastMetric() <= self._convergence_threshold

    def isImproving(self, iteration_lag):

        last_iteration = self._largest_iteration_key
        reference_iteration = min(0,self._largest_iteration_key - iteration_lag)
        return self._metric_history[last_iteration] < self._metric_history[reference_iteration]

    def pprint(self):

        print("Iteration    Metric Value")
        for key, val in iteritems(self._metric_history):
            print(' %5d       %12.4f' % (key, val))

#
# Implements the baseline "term-diff" metric from our submitted CMS paper.
# For each variable, take the fabs of the difference from the mean at that
# node, and weight by scenario probability.
#

class TermDiffConvergence(ConvergenceBase):

    """ Constructor
        Arguments: None beyond those in the base class.

    """
    def __init__(self, *args, **kwds):

        ConvergenceBase.__init__(self, *args, **kwds)

    def computeMetric(self, ph, scenario_tree, instances):

        term_diff = 0.0

        for stage in scenario_tree._stages:

            # we don't blend in the last stage, so we don't current care about printing the associated information.
            if stage != scenario_tree._stages[-1]:

                for reference_variable_name, (reference_variable, index_template) in iteritems(stage._variables):

                    for tree_node in stage._tree_nodes:

                        variable_indices = tree_node._variable_indices[reference_variable_name]

                        node_variable_average = tree_node._averages[reference_variable_name]

                        for index in variable_indices:

                            is_used = True # until proven otherwise

                            for scenario in tree_node._scenarios:

                                instance = instances[scenario._name]

                                if getattr(instance, reference_variable_name)[index].stale is True:
                                    is_used = False

                            if is_used is True:

                                for scenario in tree_node._scenarios:

                                    instance = instances[scenario._name]
                                    this_value = getattr(instance, reference_variable_name)[index].value
                                    term_diff += scenario._probability * fabs(this_value - value(node_variable_average[index]))

        return term_diff


#
# Implements the normalized "term-diff" metric from our submitted CMS paper.
# For each variable, take the fabs of the difference from the mean at that
# node, and weight by scenario probability - but normalize by the mean.
# If I wasn't being lazy, this could be derived from the TermDiffConvergence
# class to avoid code replication :)
#

class NormalizedTermDiffConvergence(ConvergenceBase):

    """ Constructor
        Arguments: None beyond those in the base class.

    """
    def __init__(self, *args, **kwds):

        ConvergenceBase.__init__(self, *args, **kwds)

    def computeMetric(self, ph, scenario_tree, instances):

        normalized_term_diff = 0.0

        # we don't blend in the last stage, so we don't current care about printing the associated information.
        for stage in scenario_tree._stages[:-1]:

            for reference_variable_name, (reference_variable, index_template) in iteritems(stage._variables):

                for tree_node in stage._tree_nodes:

                    # create a cache of all instance variables (with name reference_variable_name) 
                    # for scenarios participating in this tree node. avoids excessive calls to
                    # the find_component method of a block.
                    instance_variables = tuple(((instances[scenario._name].find_component(reference_variable_name), scenario._probability) for scenario in tree_node._scenarios))

                    node_variable_average = tree_node._averages[reference_variable_name]

                    for index in tree_node._variable_indices[reference_variable_name]:

                        # should think about nixing the magic constant below (not sure how to best pararamterize it).
                        if fabs(value(node_variable_average[index])) > 0.0001:

                            is_used = True # until proven otherwise

                            for instance_variable, scenario_probability in instance_variables:
                                if instance_variable[index].stale == True:
                                    is_used = False

                            if is_used is True:

                                average_value = value(node_variable_average[index])

                                for instance_variable, scenario_probability in instance_variables:

                                    this_value = instance_variable[index].value
                                    normalized_term_diff += scenario_probability * fabs((this_value - average_value)/average_value)
        normalized_term_diff = normalized_term_diff / (ph._total_discrete_vars + ph._total_continuous_vars)
        return normalized_term_diff

#
# Implements a super-simple convergence criterion based on when a particular number of
# discrete variables are free (e.g., 20 or fewer).
#

class NumFixedDiscreteVarConvergence(ConvergenceBase):

    """ Constructor
        Arguments: None beyond those in the base class.

    """
    def __init__(self, *args, **kwds):

        ConvergenceBase.__init__(self, *args, **kwds)

    def computeMetric(self, ph, scenario_tree, instances):

        # the metric is brain-dead; just look at PH to see how many free discrete variables there are!
        return ph._total_discrete_vars - ph._total_fixed_discrete_vars
