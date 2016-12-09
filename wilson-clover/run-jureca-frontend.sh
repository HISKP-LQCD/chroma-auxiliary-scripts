#!/bin/bash -x

module load Intel
module load IntelMPI

OMP_NUM_THREADS=24 KMP_AFFINITY=scatter,0 \
    ~/jureca-local-icc/bin/hmc -i hmc-wilson-clover.ini.xml -o hmc-wilson-clover.out.xml \
    -by 8 -bz 8 -c 24 -sy 1 -sz 1 -pxy 1 -pxyz 0 -minct 2
