#!/bin/sh

set -eux

pylint main.py orm scraper
pytest -sv tests