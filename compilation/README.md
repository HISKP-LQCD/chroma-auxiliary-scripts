# Chroma Compilation

Getting Chroma up and running is not an easy task. The scripts in this
directory are the result of several months of fiddling with compiler options
and dependencies.

Use the
[`bootstrap-chroma`](https://martin-ueding.de/apps/lqcd/bootstrap-chroma)
script and have a look into its `--help` message.

Compilation on JUQUEEN (Blue Gene/Q) had been tried, it does not make much
sense, though. The performance of the Chroma solvers is not great. Bagel does
not support current Chroma versions and the Blue Gene/Q architecture. QPhiX
does not work on Blue Gene/Q. Therefore the focus is on Intel architectures.
