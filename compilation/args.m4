ARG_HELP([Installs Chroma with dependencies from scratch.

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

ARG_POSITIONAL_SINGLE([basedir], [Base path], [])

ARG_OPTIONAL_BOOLEAN([verbose], [V], [Print Bash commands executed], [yes])
ARG_OPTIONAL_BOOLEAN([download-only], [d], [Download only (for systems like Hazel Hen)], [no])

ARG_OPTIONAL_BOOLEAN([autodetect-machine], [m], [Automatically figure out which machine we are on], [yes])
ARG_OPTIONAL_SINGLE([compiler], [c], [Compiler family to use, defaults to best on given machine], [])
ARG_OPTIONAL_SINGLE([make-j], [j], [Maximum number of parallel processes used by make], [$(nproc)])
ARG_OPTIONAL_SINGLE([isa], [i], [Manual instruction set architecture (ISA), usually automatically set], )

ARG_OPTIONAL_BOOLEAN([only-qphix], [q], [Only compile QPhiX, not Chroma], [no])
ARG_OPTIONAL_SINGLE([qphix-branch], [Q], [QPhiX git branch], [devel])
ARG_OPTIONAL_SINGLE([precision], [p], [Precision of solver, can be "double", "float"], [double])
ARG_OPTIONAL_SINGLE([precision-inner], [P], [Precision of inner solver, can be "double", "float" or "half"], [single])
ARG_OPTIONAL_SINGLE([soalen], [s], [Structure of array (SoA) length], )
ARG_OPTIONAL_SINGLE([soalen-inner], [S], [Structure of array (SoA) length for inner solver], )

ARG_OPTIONAL_SINGLE([chroma-branch], [C], [Chroma git branch], [devel])

ARGBASH_SET_INDENT([  ])
ARGBASH_GO
