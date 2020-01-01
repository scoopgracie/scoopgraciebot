#!/bin/bash
#This file is released under the CC0 1.0 Universal (CC0 1.0) Public Domain
#Dedication. https://creativecommons.org/publicdomain/zero/1.0/
cd robotstxt/c-build
make clean
make
mv robots librobots.so ../../scoopgraciebot
