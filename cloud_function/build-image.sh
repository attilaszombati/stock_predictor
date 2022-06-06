#!/bin/sh

echo 'export PATH=~$PATH:~/.local/bin' >>$BASH_ENV
echo ${GCP_PROJECT_KEY} | base64 --decode --ignore-garbage >$HOME/gcloud-service-key.json
echo 'export GOOGLE_CLOUD_KEYS=$(cat $HOME/gcloud-service-key.json)' >>$BASH_ENV
echo 'export TAG=${CIRCLE_SHA1}' >> $BASH_ENV
echo 'export LATEST_TAG=latest' >> $BASH_ENV
echo 'export IMAGE_NAME=twitter-scraper' >>$BASH_ENV && source $BASH_ENV
docker build -t gcr.io/$GOOGLE_PROJECT_ID/$IMAGE_NAME:latest -t gcr.io/$GOOGLE_PROJECT_ID/$IMAGE_NAME:$TAG ./cloud_function
