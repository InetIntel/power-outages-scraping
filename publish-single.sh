#!/bin/bash
# Usage: ./publish-single.sh ./src/scrapers/brazil/aneel
set -e

if [ -z "$1" ]; then
  echo "Usage: $0 <path_to_scraper_dir>"
  exit 1
fi

DIR_PATH="$1"
BASE_DIR="./src/scrapers"
TEMPLATE="Dockerfile.template"
TEMPLATE_SELENIUM="Dockerfile.selenium"
OUTPUT_NAME="Dockerfile"

# Build image name: strip base dir prefix, replace / with _
prefix_removed=${DIR_PATH#"$BASE_DIR"/}
image_name=${prefix_removed//\//_}

echo "=== Building: $image_name ==="

# Pick template: use selenium template if requirements.txt contains selenium
if [ -f "$DIR_PATH/requirements.txt" ] && grep -qi "selenium" "$DIR_PATH/requirements.txt"; then
  TMPL="$TEMPLATE_SELENIUM"
  echo "  (using selenium template)"
else
  TMPL="$TEMPLATE"
fi

# Generate Dockerfile from template
awk -v p="$DIR_PATH" '{gsub(/@replace/, p); print}' "$TMPL" >"$DIR_PATH/$OUTPUT_NAME"

# Build and push
docker build -t localhost:5000/"${image_name}":latest -f "${DIR_PATH}"/Dockerfile .
docker push localhost:5000/"${image_name}":latest

echo "  Done: $image_name"
