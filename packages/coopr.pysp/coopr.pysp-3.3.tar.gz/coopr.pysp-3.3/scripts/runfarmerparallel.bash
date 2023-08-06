#!/bin/bash

#$ -o std.out

#$ -cwd

#$ -j yes

# if you're just running pyomo without a solver (e.g., to create an LP file), you don't need to pass environment
# variables to the compute nodes. however, if you want to invoke a command-line solver, you need to. it's generally
# a good idea to leave this on anyway.
#$ -V

#module load cplex/12.2.0

. /etc/profile.d/modules.sh
. /opt/openmpi_intel/1.4.2/bin/mpivars.sh

mpirun -np 1 coopr-ns : -np 1 dispatch_srvr : -np 3 pyro_mip_server : -np 1 runph --solver=cplex --solver-manager=pyro --model-directory=/home/external/sandia/jwatson/coopr/src/coopr.pysp/examples/pysp/farmer/models --instance-directory=/home/external/sandia/jwatson/coopr/src/coopr.pysp/examples/pysp/farmer/scenariodata >& ph.out
