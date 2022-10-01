#!/bin/sh

echo 'export PATH=~$PATH:~/.local/bin' >>$BASH_ENV
echo ${GCP_PROJECT_KEY} | base64 --decode --ignore-garbage >$HOME/gcloud-service-key.json
echo 'export GOOGLE_CLOUD_KEYS=$(cat $HOME/gcloud-service-key.json)' >>$BASH_ENV
echo 'export TAG=${CIRCLE_SHA1}' >>$BASH_ENV
echo 'export LATEST_TAG=latest' >>$BASH_ENV
echo 'export IMAGE_NAME=crypto-data-scraper' >>$BASH_ENV && /bin/bash -c "source ${BASH_ENV}"
# docker pull gcr.io/attila-szombati-sandbox/crypto-data-scraper:latest || true
docker build --cache-from gcr.io/attila-szombati-sandbox/crypto-data-scraper:latest -t gcr.io/attila-szombati-sandbox/crypto-data-scraper:${TAG} -t gcr.io/attila-szombati-sandbox/crypto-data-scraper:latest ./crypto_data_function
