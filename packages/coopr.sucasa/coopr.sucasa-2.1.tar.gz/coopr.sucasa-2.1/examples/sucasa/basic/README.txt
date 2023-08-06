##
## NOTE: this relies on a local Acro installation, so we assume that the
## acro environmental variable specifies the root directory.  For example
## within a CSH you can type
##
##   setenv acro <directory>
##

#
# Create customized solver
#
$acro/bin/sucasa --acro=$acro -g *.mod
#
# Build the customized solver, using the Acro installation referred
# to in the previous command.
#
make
#
# Run the customized solver, using AMPL to generate the problem instance
#
$acro/bin/sucasa --without-presolve -k *.mod *.dat
