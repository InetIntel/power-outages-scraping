#!/bin/bash
# Usage: ./publish-single.sh ./src/scrapers/brazil/aneel

if [ -z "$1" ]; then
  echo "Insufficent args. Usage: $0 <path_to_scraper_dir>"
  exit 1
fi

DIR_PATH="$1"
TEMPLATE="Dockerfile.template"
OUTPUT_NAME="Dockerfile"

# clean up the path: remove `./src/scrapers` and attach and replace `/` with `_`
prefix_removed=${DIR_PATH//.\/src\/scrapers\//}
image_name=${prefix_removed//\//_}


# TODO: use a lighter docker file if we don't need selenium

# using the template, replace placeholder names with the arg path and make a Dockerfile
awk -v p="$DIR_PATH" '{gsub(/@replace/, p); print}' "$TEMPLATE" >"$DIR_PATH/$OUTPUT_NAME"

# build + push the image: use the edited path as its name
# docker build -t "$image_name":pr_$(git rev-parse --short HEAD) -f "${DIR_PATH}"/Dockerfile .
docker build -t localhost:5000/"${image_name}":latest -f "${DIR_PATH}"/Dockerfile .
docker push localhost:5000/"${image_name}":latest


# Make the DAGU YAML file
