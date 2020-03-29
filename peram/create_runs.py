#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2017 Martin Ueding <mu@martin-ueding.de>

import argparse
import os

import jinja2

{
    16: 32,
    20: 66,
    24: 120,
    32: 220,
    48: 660
}

seeds=[387117, 852224, 517234, 794900, 552324, 541384]

flavour="strange"

def main():
    # Parse command line arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('conf_start', type=int)
    parser.add_argument('conf_end', type=int)
    parser.add_argument('conf_step', type=int, nargs='?', default=8, help='default: %(default)s')
    parser.add_argument('--email', default='', help='default: %(default)s')
    parser.add_argument('--evdir', default='/hiskp2/eigensystems/0120-Mpi270-L24-T96/hyp_062_062_3/nev_120', help='default: %(default)s')
    parser.add_argument('--gconfbase', default='/hiskp2/gauges/0120_Mpi270_L24_T96/stout_smeared/conf', help='default: %(default)s')
    parser.add_argument('--exe', default='/hadron/bartek/bin/peram_gen/peram_gen.multigpu.hybrid.quda-v0.7.2.openmpi', help='default: %(default)s')
    parser.add_argument('--jobname', default='sWC_A2p1_Mpi270_L24T96', help='default: %(default)s')
    parser.add_argument('--rundir', default='/hiskp2/ueding/peram_generation/sWC_A2p1_Mpi270_L24T96/${flavour}/cnfg', help='default: %(default)s')
    parser.add_argument('--quda_rsc_path', default='/hadron/ueding/quda_rsc_path/', help='default: %(default)s')
    options = parser.parse_args()

    # Set up Jinja.
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("."))
    template_invert = env.get_template("quda.invert.input.j2")
    template_pbs = env.get_template("quda.job.pbs.sh.j2")
    template_laph = env.get_template("quda.LapH.in.j2")

    for cfg_id in range(options.conf_start, options.conf_end + 1, options.conf_step):
        print('Creating scripts for configuration', cfg_id)

        for flavor, kappa, quarktype in [('light', 0.1280738, 'u'),
                                         ('strange', 0.126807, 's')]:
            cfg_dir = os.path.join(flavor, 'cnfg{:04d}'.format(cfg_id))
            os.makedirs(os.path.join(cfg_dir, 'outputs'), exist_ok=True)
            rundir = os.path.join(options.rundir, flavor, 'cnfg')

            jobname = '{}_{}'.format(options.jobname, quarktype)

            for rv, seed in enumerate(seeds):
                rv_dir = os.path.join(cfg_dir, 'rnd_vec_{:02d}'.format(rv))
                os.makedirs(rv_dir, exist_ok=True)

                laphin = 'LapH_{:04d}_{:02d}.in'.format(cfg_id, rv)
                jscr = 'quda.job.pbs.{:04d}_{:02d}.sh'.format(cfg_id, rv)
                outfile = '../outputs/run_{:04d}_{:02d}.out'.format(cfg_id, rv)

                with open(os.path.join(rv_dir, laphin), 'w') as f:
                    f.write(template_laph.render(
                        rv=rv,
                        i=cfg_id,
                        seed=seed,
                        quarktype=quarktype,
                        evdir=options.evdir,
                    ))

                with open(os.path.join(rv_dir, jscr), 'w') as f:
                    f.write(template_pbs.render(
                        jobname=jobname,
                        i=cfg_id,
                        email_address=options.email,
                        rv=rv,
                        exe=options.exe,
                        outfile=outfile,
                        laphin=laphin,
                        quda_rsc_path=options.quda_rsc_path,
                        rundir=rundir,
                        flavor=flavor,
                    ))

                with open(os.path.join(rv_dir, 'invert.input'), 'w') as f:
                    f.write(template_invert.render(
                        i=cfg_id,
                        kappa=kappa,
                        gconfbase=options.gconfbase,
                    ))

    os.makedirs(options.quda_rsc_path, exist_ok=True)


if __name__ == "__main__":
    main()
