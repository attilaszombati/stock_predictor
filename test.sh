#!/bin/sh

set -eux

pylint cloud_function
pytest -sv tests