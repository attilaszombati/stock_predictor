#!/bin/sh

echo 'export PATH=~$PATH:~/.local/bin' >>$BASH_ENV
echo ${GCP_PROJECT_KEY} | base64 --decode --ignore-garbage >$HOME/gcloud-service-key.json
echo 'export GOOGLE_CLOUD_KEYS=$(cat $HOME/gcloud-service-key.json)' >>$BASH_ENV
echo 'export TAG=${CIRCLE_SHA1}' >>$BASH_ENV
echo 'export LATEST_TAG=latest' >>$BASH_ENV
echo 'export IMAGE_NAME=crypto-data-scraper' >>$BASH_ENV && /bin/bash -c "source ${BASH_ENV}"
curl -sSL https://sdk.cloud.google.com | bash
/bin/sh export=$PATH:/root/google-cloud-sdk/bin
gcloud auth configure-docker --quiet --project attila-szombati-sandbox gcr.io/attila-szombati-sandbox/crypto-data-scraper
docker pull gcr.io/attila-szombati-sandbox/crypto-data-scraper:latest || true
docker build --cache-from gcr.io/attila-szombati-sandbox/crypto-data-scraper:latest -t gcr.io/attila-szombati-sandbox/crypto-data-scraper:$CIRCLE_SHA1 -t gcr.io/attila-szombati-sandbox/crypto-data-scraper:latest ./crypto_data_function
