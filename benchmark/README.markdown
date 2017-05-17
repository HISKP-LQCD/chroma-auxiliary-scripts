# QPhiX Benchmarking Scripts

In this directory, there are scripts to benchmark QPhiX on Marconi A2 and
JURECA. A Python program will generate a bunch of job scripts that can then be
put into the queue. Another Python program can analyse the resulting output.

## Job Script Generation

To run the job script generator, you need the following:

- Python 3
- Jinja 2 for Python 3

Edit the `generate_marconi_jobs.py` script and adapt the `for` loops to iterate
through the parameters that you want.

## Analysis

The `marconi-benchmark.py` program will take all the output files and generate
one large CSV file with all the output data. Also it will combine the 12
measurements per run into a single mean and standard error.
