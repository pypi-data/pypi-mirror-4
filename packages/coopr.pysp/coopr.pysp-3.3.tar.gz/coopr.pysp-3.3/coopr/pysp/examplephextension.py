#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2009 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

from pyutilib.component.core import *
from coopr.pysp import phextension


class examplephextension(SingletonPlugin):

    implements (phextension.IPHExtension)
    
    def pre_ph_initialization(self,ph):
        """Called before PH initialization."""
        print("PRE INITIALIZATION PH CALLBACK INVOKED")

    def post_instance_creation(self, ph):
        """Called after PH initialization has created the scenario instances, but before any PH-related weights/variables/parameters/etc are defined!"""
        print("POST INSTANCE CREATION PH CALLBACK INVOKED")

    def post_ph_initialization(self, ph):
        """Called after PH initialization!"""
        print("POST INITIALIZATION PH CALLBACK INVOKED")

    def post_iteration_0_solves(self, ph):
        """Called after the iteration 0 solves!"""
        print("POST ITERATION 0 SOLVE PH CALLBACK INVOKED")

    def post_iteration_0(self, ph):
        """Called after the iteration 0 solves, averages computation, and weight computation"""
        print("POST ITERATION 0 PH CALLBACK INVOKED")

    def pre_iteration_k_solves(self, ph):
        """Called immediately before the iteration k solves!"""
        print("PRE ITERATION K SOLVE PH CALLBACK INVOKED")

    def post_iteration_k_solves(self, ph):
        """Called after the iteration k solves!"""
        print("POST ITERATION K SOLVE PH CALLBACK INVOKED")

    def post_iteration_k(self, ph):
        """Called after the iteration k is finished, after weights have been updated!"""
        print("POST ITERATION K PH CALLBACK INVOKED")

    def post_ph_execution(self, ph):
        """Called after PH has terminated!"""
        print("POST EXECUTION PH CALLBACK INVOKED")

