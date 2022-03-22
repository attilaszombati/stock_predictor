#!/bin/sh

set -eux

pylint orm scraper
pytest -sv tests