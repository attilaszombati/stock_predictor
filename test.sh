#!/bin/sh

set -eux

llintpy llintpy.yml
pytest -sv tests