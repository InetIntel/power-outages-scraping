#!/bin/bash
# Usage: ./publish-single.sh ./src/scrapers/brazil/aneel

if [ -z "$1" ]; then
  echo "Insufficent args. Usage: $0 <path_to_scraper_dir>"
  exit 1
fi

DIR_PATH="$1"

# clean up the path: remove `./src/scrapers` and attach and replace `/` with `_`
prefix_removed=${DIR_PATH//.\/src\/scrapers\//}
image_name=${prefix_removed//\//_}


# use a lighter docker file if we don't need selenium
TEMPLATE_REGULAR="Dockerfile.template"
TEMPLATE_SELENIUM="Dockerfile.selenium.template"
OUTPUT_NAME="Dockerfile"
CURRENT_TEMPLATE="" # will be set soon
# check the python requirements.txt to see if we need selenium
REQ_FILE="$DIR_PATH/requirements.txt"
USE_SELENIUM=false

if [ -f "$REQ_FILE" ]; then
  # check if selenium is in the file, ignoring commented out lines (^)
  if grep -E '^[[:space:]]*selenium([=><!].*)?([[:space:]]|$)' "$REQ_FILE" > /dev/null; then
    USE_SELENIUM=true
  fi
fi

if [ "$USE_SELENIUM" = "true" ]; then
  CURRENT_TEMPLATE="$TEMPLATE_SELENIUM"
  echo "[publish-single.sh] using the selenium template"
else
  CURRENT_TEMPLATE="$TEMPLATE_REGULAR"
  echo "[publish-single.sh] using the regular template"
fi

# using the template, replace placeholder names with the arg path and make a Dockerfile
awk -v p="$DIR_PATH" '{gsub(/@replace/, p); print}' "$CURRENT_TEMPLATE" >"$DIR_PATH/$OUTPUT_NAME"

# build + push the image: use the edited path as its name
# docker build -t "$image_name":pr_$(git rev-parse --short HEAD) -f "${DIR_PATH}"/Dockerfile .
docker build -t localhost:5000/"${image_name}":latest -f "${DIR_PATH}"/Dockerfile .
docker push localhost:5000/"${image_name}":latest


# Make the DAGU YAML file
