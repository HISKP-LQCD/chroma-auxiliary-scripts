#!/bin/bash
#PBS -S /bin/bash
#PBS -N {{ name }}
#PBS -l nodes={{ nodes }}:ppn=24
#PBS -l walltime=00:10:00
#PBS -j oe
#PBS -m a
#PBS -M ueding@hiskp.uni-bonn.de

set -e
set -u

module swap PrgEnv-cray PrgEnv-intel
module load gcc/6.3.0
module load intel/17.0.2.174

module list

set -x

cd $PBS_O_WORKDIR

geometry=( {{ geom|join(' ') }} )

#module load perftools-base
#rundir=${PBS_JOBNAME}-${PBS_JOBID}
#mkdir $rundir
#cd $rundir
#grid_order -C \
    #-g ${geometry[0]},${geometry[1]},${geometry[2]},${geometry[3]} -c 1,1,1,2 \
    #> MPICH_RANK_ORDER
#cat MPICH_RANK_ORDER
#export MPICH_RANK_REORDER_METHOD=3

export OMP_NUM_THREADS=12
#export OMP_PROC_BIND=SPREAD

for prog in ~/Chroma-older/build-icc/qphix/tests/time_clov_noqdp; do
    aprun -n $((geometry[0] * geometry[1] * geometry[2] * geometry[3])) -N 2 -d 12 \
    -cc depth \
    $prog \
    -c 12 -sy 1 -sz 1 -geom ${geometry[@]} \
    -by 4 -bz 4 -pxy 1 -pxyz 0 -minct 1 \
    -x {{ lattice }} -y {{ lattice }} -z {{ lattice }} -t 96 \
    -prec d -cg -i 100 -compress12
done
