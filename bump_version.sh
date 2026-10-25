#!/bin/sh
runsed VERSION \
    pyproject.toml \
    gargleblaster/__init__.py \
    conda/win-64/meta.yaml \
    conda/osx-64/meta.yaml

