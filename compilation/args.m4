ARG_HELP([Installs Chroma with dependencies from scratch.

This is a script to install Chroma, QPhiX, QDP++, QMP, and their
dependencies on the following HPC systems:

=============== ====================== ==========================
Name            Architecture           Location
=============== ====================== ==========================
Hazel Hen       Haswell                Stuttgart, Germany
JURECA          Haswell                Jülich, Germany
JURECA Booster  Knights Landung        Jülich, Germany
Marconi A2      Knights Landing        Casalecchio di Reno, Italy
QBIG            Sandy Bridge / Haswell Bonn, Germany
=============== ====================== ==========================

The script will automatically find out which computer you run it on. If
this check fails, the script need to be fixed.

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
])

ARG_POSITIONAL_SINGLE([host], [Machine to build on, can be one of the following: hazelhen, jureca, jureca-booster, local, marconi-a2, qbig.], [])
ARG_POSITIONAL_SINGLE([basedir], [Base path for compilation and installation.], [])

ARG_OPTIONAL_BOOLEAN([verbose], [V], [Print Bash commands executed.], [on])
ARG_OPTIONAL_BOOLEAN([download-only], [d], [Download only. This is needed for systems like Hazel Hen where outgoing connections are not allowed. Run the script with the this option on your workstation, rsync everything to the machine and then compile there.], [off])

ARG_OPTIONAL_SINGLE([compiler], [c], [Compiler family to use, defaults to best on given machine.], [])
ARG_OPTIONAL_SINGLE([make-j], [j], [Maximum number of parallel processes used by "make". The default value is the number of cores on the current machine.], [$(nproc)])
ARG_OPTIONAL_SINGLE([isa], [i], [Manual instruction set architecture (ISA), usually automatically set. Can also be used to override ISA in edge cases, like using AVX2 on KNL in order to use SoA length of 2 in double precision.], )

ARG_OPTIONAL_BOOLEAN([qdpjit], , [Use QDP-JIT instead of QDP++.], [off])

ARG_OPTIONAL_BOOLEAN([only-qphix], [q], [Only compile QPhiX, not Chroma.], [off])
ARG_OPTIONAL_SINGLE([qphix-branch], [Q], [QPhiX git branch to use.], [devel])
ARG_OPTIONAL_SINGLE([precision], [p], [Precision of solver, can be "double", "float".], [double])
ARG_OPTIONAL_SINGLE([precision-inner], [P], [Precision of inner solver, can be "double", "float" or "half".], [single])
ARG_OPTIONAL_SINGLE([soalen], [s], [Structure of array (SoA) length.], )
ARG_OPTIONAL_SINGLE([soalen-inner], [S], [Structure of array (SoA) length for inner solver.], )

ARG_OPTIONAL_SINGLE([chroma-branch], [C], [Chroma git branch to use.], [devel])

ARGBASH_SET_INDENT([  ])
ARGBASH_GO
