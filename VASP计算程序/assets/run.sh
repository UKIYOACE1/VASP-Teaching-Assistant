#!/bin/bash
#SBATCH -J AIMD
#SBATCH -p defq
#SBATCH -N 1
#SBATCH --ntasks-per-node=48
#SBATCH --cpus-per-task=1
#SBATCH --output=slurm-output.out

module add vasp/5.4.4
source /cm/shared/apps/intel/setvars.sh
mpirun vasp_std
