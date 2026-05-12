#!/bin/bash
set -e

# Base directory and templates
BASE_DIR="./src/scrapers"
TEMPLATE="Dockerfile.template"
TEMPLATE_SELENIUM="Dockerfile.selenium"
OUTPUT_NAME="Dockerfile"

# Find all scraper directories that contain a scrape.py
find "$BASE_DIR" -mindepth 2 -maxdepth 3 -type f -name "scrape.py" | while read -r scrape_file; do
  dir_path=$(dirname "$scrape_file")

  # Skip WIP directories
  case "$dir_path" in
    *japan_wip*|*old_scrapers*) continue ;;
  esac

  # Build image name: strip base dir prefix, replace / with _
  prefix_removed=${dir_path#"$BASE_DIR"/}
  image_name=${prefix_removed//\//_}

  echo "=== Building: $image_name ==="

  # Pick template: use selenium template if requirements.txt contains selenium
  if [ -f "$dir_path/requirements.txt" ] && grep -qi "selenium" "$dir_path/requirements.txt"; then
    TMPL="$TEMPLATE_SELENIUM"
    echo "  (using selenium template)"
  else
    TMPL="$TEMPLATE"
  fi

  # Generate Dockerfile from template
  output_file="$dir_path/$OUTPUT_NAME"
  awk -v p="$dir_path" '{gsub(/@replace/, p); print}' "$TMPL" >"$output_file"

  # Build and push
  docker build -t localhost:5000/"${image_name}":latest -f "${dir_path}"/Dockerfile .
  docker push localhost:5000/"${image_name}":latest

  echo "  Done: $image_name"
done

echo "=== All images built and pushed ==="
