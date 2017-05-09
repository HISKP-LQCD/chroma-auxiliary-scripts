#!/bin/bash

conf_start=501
conf_step=8
conf_end=1565

rv_start=0
rv_end=5

seeds=(387117 852224  517234  794900  552324  541384)

flavour="strange"

EVDIR="\/hiskp2\/eigensystems\/0120-Mpi270-L24-T96\/hyp_062_062_3\/nev_120"
GCONFBASE="\/hiskp2\/gauges\/0120_Mpi270_L24_T96\/stout_smeared\/conf"
EXEC="\/hadron\/bartek\/bin\/peram_gen\/peram_gen.multigpu.hybrid.quda-v0.7.2.openmpi"
JOBNAME="sWC_A2p1_Mpi270_L24T96_s"

RUNDIR="\/hiskp2\/ueding\/peram_generation\/sWC_A2p1_Mpi270_L24T96\/${flavour}\/cnfg"
QUDA_RSC_PATH="\/hadron\/ueding\/quda_rsc_path\/"

for i in $( seq ${conf_start} ${conf_step} ${conf_end} ); do
  echo "creating config $i"
  j=`printf %04d $i`

  mkdir -p cnfg${j}/
  mkdir -p cnfg${j}/outputs
  cd cnfg${j}/
  
  for rv in $( seq ${rv_start} ${rv_end} ); do
    seed=${seeds[${rv}]}
    rnd2=$( printf %02d ${rv} )
    mkdir -p rnd_vec_${rnd2}
    cd rnd_vec_${rnd2}
  
    cp ../../templates/quda.invert.input invert.input
    sed -i "s@NSTORE@${i}@g" invert.input
    sed -i "s@GCONFBASE@${GCONFBASE}@g" invert.input
    
    laphin=LapH_${j}_${rnd2}.in
    jscr=quda.job.pbs.${j}_${rnd2}.sh
    outfile="..\/outputs\/run_${j}_${rnd2}.out"
  
    cp ../../templates/quda.job.pbs.sh ${jscr}
    sed -i "s@RUNDIR@${RUNDIR}${j}\/rnd_vec_${rnd2}@g" ${jscr}
    sed -i "s@JOBNAME@${JOBNAME}_${j}_${rv}@g" ${jscr}
    sed -i "s@INFILE@${laphin}@g" ${jscr}
    sed -i "s@OUTFILE@${outfile}@g" ${jscr}
    sed -i "s@EXEC@${EXEC}@g" ${jscr}
    sed -i "s@QUDA_RSC_PATH@${QUDA_RSC_PATH}@g" ${jscr}
  
    cp ../../templates/quda.LapH.in ${laphin}
    sed -i "s@NSTORE@${i}@g" ${laphin} 
    sed -i "s@NB_RND@${rv}@g" ${laphin}
    sed -i "s@SEED@${seed}@g" ${laphin}
    sed -i "s@EVDIR@${EVDIR}@g" ${laphin}

    cd ..
  done
  cd ..
done
