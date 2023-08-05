#!/bin/bash

# Calls pyspread from top level folder of extracted tarball

export PYTHONPATH=./pyspread
./pyspread/pyspread $@
