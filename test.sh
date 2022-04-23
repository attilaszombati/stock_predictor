#!/bin/sh

set -eux

pylint scraper orm tests main.py
pytest -sv tests