#!/bin/sh

cat <<EOF
{
  "docker_image_tag": "$CIRCLE_SHA1"
}
EOF