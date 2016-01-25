#! /bin/bash
git clone --quiet https://github.com/pyQode/pyqode.qt
pushd pyqode.qt
pip install --quiet -e .
popd
