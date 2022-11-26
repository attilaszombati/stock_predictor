#!/bin/sh

set -eux

pylint predictor_api
black --check predictor_api