#!/bin/sh

set -eux

pylint cloud_function
pytest -sv cloud_function/tests