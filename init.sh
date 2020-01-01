#!/bin/bash
#This file is released under the CC0 1.0 Universal (CC0 1.0) Public Domain
#Dedication. https://creativecommons.org/publicdomain/zero/1.0/
rm -rf robotstxt
git clone https://github.com/google/robotstxt.git robotstxt
cd robotstxt/
mkdir c-build && cd c-build
cmake .. -DROBOTS_BUILD_TESTS=ON
cd ../../
cp external_code_modifications/robotsutil.cc robotstxt/robots_main.cc
