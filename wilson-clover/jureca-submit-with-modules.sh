#!/bin/bash
# Copyright © 2016 Martin Ueding <dev@martin-ueding.de>

# Submits the job to the JURECA queue and makes sure that the needed modules to
# run `hmc` are loaded before submitting.

set -e
set -u
set -x

module load Intel
module load IntelMPI

sbatch "$1"
