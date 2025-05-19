#! /usr/bin/bash
env_name=wow

if [ $# == 0 ]; then
	echo "please input filename"
	exit 0
fi

file=`find . -name ${1}`
if [ ! -f $file ]; then
	echo "file ${1} not exist..."
	exit 0
fi

# change env
source /root/p_envs/$env_name/bin/activate

exec_file=${0}
path=`dirname $(realpath $exec_file)`
export PYTHONPATH="$PYTHONPATH:$path"

clear
python3 $file
