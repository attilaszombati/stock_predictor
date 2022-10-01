#!/bin/sh

# env.sh

# Change the contents of this output to get the environment variables
# of interest. The output must be valid JSON, with strings for both
# keys and values.

cat <<EOF
{
  "docker_image_tag": "$CIRCLE_SHA1"
}
EOF