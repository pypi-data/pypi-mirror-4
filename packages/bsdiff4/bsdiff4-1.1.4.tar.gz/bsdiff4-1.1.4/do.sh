#!/bin/bash
for PY in 33
do
    PYBIN=$HOME/py$PY/bin/python
    rm -rf $HOME/$PY/lib/python*/site-packages
    $PYBIN -V
    rm -rf build dist
    $PYBIN setup.py install >/dev/null 2>&1 || exit 1
    pushd /tmp
    $PYBIN -c "import bsdiff4; assert bsdiff4.test().wasSuccessful()" || \
        exit 1
    popd
done
