#!/bin/bash
# Copyright © 2017 Martin Ueding <mu@martin-ueding.de>

../marconi-benchmark.py clover-*-????.txt --output perf-clover.csv
../marconi-benchmark.py tm-48*-????.txt --output perf-tm.csv
../marconi-benchmark.py tm-clover-*-????.txt --output perf-tm-clover.csv
../marconi-benchmark.py wilson*-????.txt --output perf-wilson.csv

