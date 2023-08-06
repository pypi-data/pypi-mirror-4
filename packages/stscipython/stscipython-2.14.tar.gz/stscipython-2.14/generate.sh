#!/bin/sh

# arg 1 is branch name; default is trunk
branch=$1

# get the new_install tools on our path
cd new_install
PATH=`pwd`:$PATH
export PATH
cd ..

# check out all the things we need
stp_list $branch | stp_checkout

# show all the packages in the order they need to be installed
# column 0 is the deepest location in the dependency tree
# column 1 is the package name
# column 2 is whether it uses the new install
stp_list | python cfgdep.py -i -status

# update the requires line in setup.cfg
stp_list | python cfgdep.py -i -cfgupdate

