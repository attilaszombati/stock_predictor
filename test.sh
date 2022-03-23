#!/bin/sh

set -eux

pylint scraper orm tests
pytest -sv tests