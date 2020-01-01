#!/bin/bash
#This file is released under the CC0 1.0 Universal (CC0 1.0) Public Domain
#Dedication. https://creativecommons.org/publicdomain/zero/1.0/
anyNotFound=f
for i in git cmake make tar g++; do
	if ! which $i >/dev/null; then
		if [ $anyNotFound == f ]; then
			echo "The following dependencies are not installed:"
			anyNotFound=t
		fi
		echo $i
	fi
done
if [ $anyNotFound == f ]; then
	echo "All dependencies are installed."
fi
