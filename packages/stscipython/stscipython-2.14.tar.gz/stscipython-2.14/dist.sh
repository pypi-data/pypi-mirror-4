#!/bin/sh
#
# 
case "$1"
in
sdist)
	command=$1
	;;
bdist_egg)
	command=$1
	;;
*)
	echo only know sdist and bdist_egg
	exit 1
	;;
esac


new_install/stp_list | ( while read a b
	do
		if cd $a
		then
			python setup.py $command
			thisst=$?
			st=$st$thisst
			if [ $thisst != 0 ]
			then
				errpkg="$errpkg $a"
				echo ERROR FOR $a
				sleep 2
			fi
			cd ..
		else
			errpkg="$errpkg $a"
			st=${st}1
			echo NO DIRECTORY $a
			sleep 2
		fi
	done
echo ERRORS FOR $errpkg
st=`echo $st | tr -d '0' | cut -c1-1`
exit $st 
)
st=$?
if [ $st != 0 ]
then
	echo ERROR
fi
exit $st
