#!/bin/bash -e

mkdir config
mkdir -p lib/galaxy/jobs/rules

make test GALAXY_PATH=.
