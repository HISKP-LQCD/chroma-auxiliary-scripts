#PBS -N JOBNAME
#PBS -l walltime=10:00:00,mem=35gb
#PBS -l nodes=1:ppn=4:gpus=4
#PBS -M bartosz_kostrzewa@fastmail.com
#PBS -m abe
#PBS -j oe

rundir=RUNDIR
exe=EXEC
outfile=OUTFILE
infile=INFILE
export QUDA_RESOURCE_PATH=QUDA_RSC_PATH

cd ${rundir}
date > ${outfile}
mpirun.openmpi -x QUDA_RESOURCE_PATH -x OMP_NUM_THREADS=1 -np 4 -npersocket 2 \
${exe} -LapHsin ${infile} | tee -a ${outfile}
date >> ${outfile}

