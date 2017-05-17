# Perambulator Generation

The perambulators are created from the gauge configuration and the
eigensystems. These are inverted using `peram_gen` on the GPU cluster.

The script `create_runs.py` will generate all the needed job scripts from the
`*.j2` templates in this directory. Call it with `-h` or `--help` in order to
get the following help message:

    usage: create_runs.py [-h] [--email EMAIL] [--evdir EVDIR]
                          [--gconfbase GCONFBASE] [--exe EXE] [--jobname JOBNAME]
                          [--rundir RUNDIR] [--quda_rsc_path QUDA_RSC_PATH]
                          conf_start conf_end [conf_step]

    positional arguments:
      conf_start
      conf_end
      conf_step             default: 8

    optional arguments:
      -h, --help            show this help message and exit
      --email EMAIL         default:
      --evdir EVDIR         default: /hiskp2/eigensystems/0120-Mpi270-L24-T96/hyp_
                            062_062_3/nev_120
      --gconfbase GCONFBASE
                            default:
                            /hiskp2/gauges/0120_Mpi270_L24_T96/stout_smeared/conf
      --exe EXE             default: /hadron/bartek/bin/peram_gen/peram_gen.multig
                            pu.hybrid.quda-v0.7.2.openmpi
      --jobname JOBNAME     default: sWC_A2p1_Mpi270_L24T96
      --rundir RUNDIR       default: /hiskp2/ueding/peram_generation/sWC_A2p1_Mpi2
                            70_L24T96/${flavour}/cnfg
      --quda_rsc_path QUDA_RSC_PATH
                            default: /hadron/ueding/quda_rsc_path/

After letting it create the scripts for a single configuration, you will have the following directory structure:

    $ tree light strange
    light
    └── cnfg0000
        ├── outputs
        ├── rnd_vec_00
        │   ├── invert.input
        │   ├── LapH_0000_00.in
        │   └── quda.job.pbs.0000_00.sh
        ├── rnd_vec_01
        │   ├── invert.input
        │   ├── LapH_0000_01.in
        │   └── quda.job.pbs.0000_01.sh
        ├── rnd_vec_02
        │   ├── invert.input
        │   ├── LapH_0000_02.in
        │   └── quda.job.pbs.0000_02.sh
        ├── rnd_vec_03
        │   ├── invert.input
        │   ├── LapH_0000_03.in
        │   └── quda.job.pbs.0000_03.sh
        ├── rnd_vec_04
        │   ├── invert.input
        │   ├── LapH_0000_04.in
        │   └── quda.job.pbs.0000_04.sh
        └── rnd_vec_05
            ├── invert.input
            ├── LapH_0000_05.in
            └── quda.job.pbs.0000_05.sh
    strange
    └── cnfg0000
        ├── outputs
        ├── rnd_vec_00
        │   ├── invert.input
        │   ├── LapH_0000_00.in
        │   └── quda.job.pbs.0000_00.sh
        ├── rnd_vec_01
        │   ├── invert.input
        │   ├── LapH_0000_01.in
        │   └── quda.job.pbs.0000_01.sh
        ├── rnd_vec_02
        │   ├── invert.input
        │   ├── LapH_0000_02.in
        │   └── quda.job.pbs.0000_02.sh
        ├── rnd_vec_03
        │   ├── invert.input
        │   ├── LapH_0000_03.in
        │   └── quda.job.pbs.0000_03.sh
        ├── rnd_vec_04
        │   ├── invert.input
        │   ├── LapH_0000_04.in
        │   └── quda.job.pbs.0000_04.sh
        └── rnd_vec_05
            ├── invert.input
            ├── LapH_0000_05.in
            └── quda.job.pbs.0000_05.sh

    16 directories, 36 files
