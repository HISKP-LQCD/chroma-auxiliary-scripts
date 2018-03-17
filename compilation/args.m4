ARG_HELP([Installs Chroma with dependencies from scratch])

ARG_OPTIONAL_BOOLEAN([verbose], [V], [Disable printing of Bash commands executed. By default every command that is executed will be printed on the screen.], [off])
ARG_OPTIONAL_SINGLE([machine], [m], , )
ARG_OPTIONAL_SINGLE([compiler], [c], [Compiler family to use.], [])
ARG_OPTIONAL_SINGLE([chroma-branch], [C], , [devel])
ARG_OPTIONAL_SINGLE([make-j], [j], , )
ARG_OPTIONAL_SINGLE([isa], [i], , )
ARG_OPTIONAL_SINGLE([only-qphix], [q], , [no])
ARG_OPTIONAL_SINGLE([qphix-branch], [Q], , [devel])
ARG_OPTIONAL_SINGLE([precision], [p], , [double])
ARG_OPTIONAL_SINGLE([precision-inner], [P], , [single])
ARG_OPTIONAL_SINGLE([soalen], [s], , )
ARG_OPTIONAL_SINGLE([soalen-inner], [S], , )

ARGBASH_SET_INDENT([  ])
ARGBASH_GO
