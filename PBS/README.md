# Hold Queued CPU Jobs

Our cluster management based on PBS has the limitation that running CPU and GPU
jobs on the same node needs manual work. When CPU jobs are already running, GPU
jobs will not start, although the GPU are free.

A workaround is to put all CPU jobs into “hold” state and wait until the GPU
jobs have started up. Then the CPU jobs are released again into the “queued”
state. This is tedious and error prone.

The script `hold-queued-cpu-jobs.py` can hold (or release) all jobs that match
the following criteria:

- The job is currently “queued” (“hold”) and not running. Therefore it does not
  abort anything that is currently running.

- The job owner is the currently logged in user. This can be overridden by the
  `--user` option.

- The job does not allocate any GPUs. Holding GPU jobs would of course make no
  sense.

## Usage

An extra option `--armed` needs to be supplied to perform the changes. The
changes are only listed by default to give you an opportunity to look at them.

In order to yield resources, call it like so:

    python3 hold-queued-cpu-jobs.py hold --armed

When the GPU jobs have started up, you can release your CPU jobs with this:

    python3 hold-queued-cpu-jobs.py release --armed

## Implementation Detail

The script uses `qstat -x` to retrieve the information from PBS in machine
readable XML. Therefore there is no danger of truncated job names or similar
issues with the ASCII table output of `qstat`.

## License

MIT/Expat.

<!-- vim: set spell tw=79 :-->
