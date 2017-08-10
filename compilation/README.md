# Chroma Compilation

Getting Chroma up and running is not an easy task. The scripts in this
directory are the result of several months of fiddling with compiler options
and dependencies.

Use the `bootstrap-chroma` script and have a look into its [manual page
`bootstrap-chroma.1.rst`](bootstrap-chroma.1.rst). If you like, you can convert
this into a manpage using Pandoc:

    pandoc -s bootstrap-chroma.1.rst -o bootstrap-chroma.1
    man -l bootstrap-chroma.1

Compilation on JUQUEEN (Blue Gene/Q) had been tried, it does not make much
sense, though. The performance of the Chroma solvers is not great. Bagel does
not support current Chroma versions and the Blue Gene/Q architecture. QPhiX
does not work on Blue Gene/Q. Therefore the focus is on Intel architectures.
