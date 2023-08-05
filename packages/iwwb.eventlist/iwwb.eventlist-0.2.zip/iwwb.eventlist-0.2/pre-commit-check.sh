#!/bin/bash

echo 'Running tests'
bin/test -s iwwb.eventlist

echo '====== Running ZPTLint ======'
for pt in `find src/iwwb/eventlist/ -name "*.pt"` ; do bin/zptlint $pt; done

echo '====== Running PyFlakes ======'
bin/pyflakes src/iwwb/eventlist
bin/pyflakes setup.py

echo '====== Running pep8 =========='
bin/pep8 --ignore=E501 src/iwwb/eventlist
bin/pep8 --ignore=E501 setup.py

