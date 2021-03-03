#!/bin/bash
if [ $# -ne 1 ]
then
	echo 'Error: Program can only take in one parameter as input'
	exit 1
fi

python3 lab3b.py $1