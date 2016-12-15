#!/bin/bash -x

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=06:00:00
#SBATCH --partition=batch
#SBATCH --cpus-per-task=24
#SBATCH --mail-type=ALL
#SBATCH --mail-user=ueding@hiskp.uni-bonn.de

module load Intel
module load IntelMPI

export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}
export KMP_AFFINITY=scatter,0
srun ./hmc -i hmc-wilson-clover.ini.xml -o hmc-wilson-clover.out.xml -by 8 -bz 8 -c 24 -sy 1 -sz 1 -pxy 1 -pxyz 0 -minct 2
