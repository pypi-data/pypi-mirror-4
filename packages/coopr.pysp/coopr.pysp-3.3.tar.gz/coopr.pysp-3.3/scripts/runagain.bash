#!/bin/bash

#$ -N DLW_farmer_test
#$ -cwd
#$ -V
#$ -o farmertest.out
#$ -e farmertest.err       

#$ -j yes

echo "start"
date
mpirun -np 1 runph --solver=cplex --solver-manager=pyro --model-directory=/home/dlwoodruff/coopr/src/coopr.pysp/examples/pysp/farmer/models --instance-directory=/home/dlwoodruff/coopr/src/coopr.pysp/examples/pysp/farmer/scenariodata >& ph.out
date
echo "done."
