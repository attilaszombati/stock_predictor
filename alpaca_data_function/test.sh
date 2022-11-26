#!/bin/sh

set -eux

pylint alpaca_data_function
black --check alpaca_data_function