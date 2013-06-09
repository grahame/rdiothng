#!/bin/bash -x 

rm -rf ~/venv.rdio
virtualenv --system-site-packages ~/venv.rdio
~/venv.rdio/bin/pip install python-rdio
