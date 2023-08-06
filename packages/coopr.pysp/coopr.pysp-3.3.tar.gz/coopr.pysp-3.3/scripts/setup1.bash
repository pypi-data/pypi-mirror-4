#!/bin/bash

#$ -N dlw_ns
#$ -cwd
#$ -V
#$ -o ns.out
#$ -e ns.err       

#$ -j yes

mpirun -np 1 coopr_ns 

