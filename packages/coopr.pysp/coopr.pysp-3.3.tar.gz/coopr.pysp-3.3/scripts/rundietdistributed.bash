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

mpirun -np 1 /home/external/sandia/jwatson/coopr/bin/coopr-ns : -np 1 /home/external/sandia/jwatson/coopr/bin/dispatch_srvr : -np 1 /home/external/sandia/jwatson/coopr/bin/pyro_mip_server : -np 1 /home/external/sandia/jwatson/coopr/bin/pyomo --solver=cplex --solver-manager=pyro /home/external/sandia/jwatson/coopr/src/coopr.pyomo/examples/pyomo/diet/diet1.py /home/external/sandia/jwatson/coopr/src/coopr.pyomo/examples/pyomo/diet/diet1.dat >& mip.out
