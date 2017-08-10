Name
====

bootstrap-chroma — Installs Chroma with dependencies from scratch

Synopsis
========

::

    bootstrap-chroma [OPTIONS] BASE

Description
===========

This is a script to install Chroma, QPhiX, QDP++, QMP, and their
dependencies on the following HPC systems:

+--------------+----------------------------+------------------------------+
| Name         | Architecture               | Location                     |
+==============+============================+==============================+
| Hazel Hen    | Haswell (AVX2)             | Stuttgart, Germany           |
+--------------+----------------------------+------------------------------+
| JURECA       | Haswell (AVX2)             | Jülich, Germany              |
+--------------+----------------------------+------------------------------+
| Marconi A2   | Knights Landing (AVX512)   | Casalecchio di Reno, Italy   |
+--------------+----------------------------+------------------------------+

The script will automatically find out which computer you run it on. If
this check fails, the script need to be fixed.

Options
=======

Option parsing is done using the ``getopts`` function in Bash, therefore
it has the limitation that all options need to be given before the
positional arguments (``BASE`` in this case).

Positional Arguments
--------------------

``BASE`` is the directory where everthing is downloaded, compiled, and
installed.

Flags
-----

``-c COMPILER``
    Compiler family to use. Depending on the platform, there is support
    for

    -  cray
    -  gnu
    -  icc

    The script automatically chooses a compiler that is supported on the
    architecture and gives decent performance. The default has been
    chosen after trying the other compilers. For example the GNU
    compiler gives less performance than the Intel one on Hazel Hen
    (40-ish versus 60-ish gigaflops per node). The Cray compiler does
    not support half-precision floating point types, therefore it cannot
    be used for the AVX2 target. If you just plan to *use* Chroma or
    QPhiX, just go with the default compiler that the script selects.

``-C BRANCH``
    Git branch that should be used for Chroma. (Default: ``devel``)

``-h``
    Prints a short usage message.

``-j NPROC``
    The number of processes to use with Make. By default all available
    cores in the system will be used, the number is queried with
    ``nproc``. If there are error messages, supply supply ``-j 1`` to
    get a serial build.

``-q``
    Do not build Chroma, abort after QPhiX has been compiled.

``-Q BRANCH``
    Git branch that should be used for QPhiX. (Default: ``devel``)

``-p PRECISION``
    Working precision for QDP++ and Chroma. Can be either ``double`` or
    ``float``. (Default: ``double``)

``-P PRECISION``
    Working precision for the *inner* solver in QPhiX. Can be either ``float``
    or ``double`` or ``half``. (Default: ``float``)

``-s SOALEN``
    Sets the SoA length that Chroma uses. For QPhiX, all variants will be
    compiled and are available. (Default: 4 on AVX2, 8 on KNL)

``-S SOALEN``
    Sets the SoA length that for the *inner* solver. (Default: 4)

``-V``
    Disable printing of Bash commands executed. By default every command
    that is executed will be printed on the screen.

Files
=====

After this script ran though, you will have the following directories::

    BASE/build-icc/chroma
    BASE/build-icc/libxml2
    BASE/build-icc/qdpxx
    BASE/build-icc/qmp
    BASE/build-icc/qphix

    BASE/local-icc/bin
    BASE/local-icc/include
    BASE/local-icc/lib
    BASE/local-icc/share

    BASE/sources/chroma
    BASE/sources/libxml2
    BASE/sources/qdpxx
    BASE/sources/qmp
    BASE/sources/qphix

Example
=======

When you run on Marconi A2 and you would like to use SoA length of 8 and
test a new QPhiX branch that is available on the JeffersonLab
repository, use this::

    bootstrap-chroma -Q new-qphix-branch -s 8
