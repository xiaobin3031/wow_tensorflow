#! /usr/bin/bash

if [ $# == 0 ]; then
	echo "please input filename"
	exit 0
fi

file=`find . -name ${1}`
if [ ! -f $file ]; then
	echo "file ${1} not exist..."
	exit 0
fi

pkg_path=~/.local/lib/python3.8/site-packages
P_PATH=""
for dir in $pkg_path/*; do
	if [ -d "$dir" ]; then
		P_PATH="$P_PATH:$dir"
	fi
done
exec_file=${0}
path=`dirname $(realpath $exec_file)`
export PYTHONPATH="$PYTHONPATH:$path"

python3.12 $file
