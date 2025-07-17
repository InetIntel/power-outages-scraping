#!/bin/bash

# Base directory and template file
BASE_DIR="./src/scrapers"
TEMPLATE="Dockerfile.template"
OUTPUT_NAME="Dockerfile"

# Find all subdirectories (non-recursive)
find "$BASE_DIR" -mindepth 2 -maxdepth 2 -type d | while read -r dir_path; do
  # Escape path if needed
  escaped_path="$dir_path"

  # Output file path inside the subdirectory
  output_file="$dir_path/$OUTPUT_NAME"

  # x=$(echo "$dir_path" | sed 's|^src/scrapers|.|')
  prefix_removed=${dir_path//.\/src\/scrapers\//}
  image_name=${prefix_removed//\//_}

  echo "$image_name"

  # Replace @replace in the template and write to subdirectory
  awk -v p="$escaped_path" '{gsub(/@replace/, p); print}' "$TEMPLATE" >"$output_file"

  docker build -t localhost:5000/"${image_name}":latest -f "${dir_path}"/Dockerfile .
  docker push localhost:5000/"${image_name}":latest

  echo "Written to: $output_file"
done
