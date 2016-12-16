#!/bin/bash -x
# Copyright © 2016 Martin Ueding <dev@martin-ueding.de>

#SBATCH --nodes=8
#SBATCH --ntasks-per-node=1
#SBATCH --time=06:00:00
#SBATCH --partition=batch
#SBATCH --cpus-per-task=24
#SBATCH --mail-type=ALL
#SBATCH --mail-user=ueding@hiskp.uni-bonn.de

module load Intel
module load IntelMPI

# Get the restart XML file that has been changed last in this directory.
last_restart=$(ls -rt | grep restart | grep xml | tail -n 1)

# In case no restart file can be found, use the start file. The `-` means
# “default”, the `:` means that an empty but defined variable still counts as
# undefined. That is exactly what we want here.
input=${last_restart:-hmc-wilson-clover.ini.xml}

# Set the approprite OpenMP variables for thread count and binding.
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}
export KMP_AFFINITY=scatter,0

# Start the Hybrid Monte Carlo simulation.
srun ./hmc -i $input -o slurm-${SLURM_JOB_ID}.out.xml -by 8 -bz 8 -c 24 -sy 1 -sz 1 -pxy 1 -pxyz 0 -minct 2
