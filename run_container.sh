#!/bin/sh
APP_NAME="runicbabble"
VERSION="1.1"

WORKDIR=$(pwd)

docker build -t ${APP_NAME}:${VERSION} .

docker run -v "${WORKDIR}/config":/bot/config:ro \
--env-file ./deploy.env -d --name ${APP_NAME} --restart unless-stopped ${APP_NAME}:${VERSION}