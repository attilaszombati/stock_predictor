#!/bin/sh

echo 'export PATH=~$PATH:~/.local/bin' >>$BASH_ENV
echo ${GCP_PROJECT_KEY} | base64 --decode --ignore-garbage >$HOME/gcloud-service-key.json
echo 'export GOOGLE_CLOUD_KEYS=$(cat $HOME/gcloud-service-key.json)' >>$BASH_ENV
echo 'export TAG=${CIRCLE_SHA1}' >>$BASH_ENV
echo 'export LATEST_TAG=latest' >>$BASH_ENV
echo 'export IMAGE_NAME=twitter-scraper' >>$BASH_ENV && source $BASH_ENV
docker build --cache-from gcr.io/attila-szombati-sandbox/predictor_api:latest -t gcr.io/attila-szombati-sandbox/predictor_api:$CIRCLE_SHA1 -t gcr.io/attila-szombati-sandbox/predictor_api:latest ./predictor_api
