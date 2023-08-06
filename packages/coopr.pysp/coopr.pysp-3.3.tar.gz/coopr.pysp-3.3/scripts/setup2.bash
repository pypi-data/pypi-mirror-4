#!/bin/bash

#$ -N DLW_MIP_dispatch_Server
#$ -cwd
#$ -V
#$ -o mipdisserver.out
#$ -e mipdissserver.err       

#$ -j yes

mpirun -np 1 dispatch_srvr : -np 3 pyro_mip_server

