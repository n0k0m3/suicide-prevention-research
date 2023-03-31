#!/usr/bin/env bash

DATADIR=$(realpath -e  -- "$(dirname -- "${BASH_SOURCE[0]}";)";)/../data

FILES="$DATADIR/*.json"

for f in $FILES
do
  filename=$(basename -- "$f")
  filename="${filename%.*}"
  echo "Processing $filename file..."
  mongoimport -u n0k0m3 -p password321 --db IRI_staging --collection $filename --type json --file $f --host=127.0.0.1 --port=27017 --authenticationDatabase=admin
done
