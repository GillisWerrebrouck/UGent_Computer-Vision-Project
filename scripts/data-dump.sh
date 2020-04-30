#!/bin/bash

NR_OF_DOCUMENTS=840
DOCUMENTS_PER_FILE=5
NR_OF_FILES=$((NR_OF_DOCUMENTS/DOCUMENTS_PER_FILE))

for i in $(seq 1 $NR_OF_FILES); do
  echo "=============== $i ==============="
  mongoexport \
    --db computervision \
    --type json --jsonArray \
    --collection=images \
    --out="images_$i.json" \
    -u devuser -p devpwd --authenticationDatabase=admin \
    --limit $DOCUMENTS_PER_FILE \
    --skip $(((i-1)*DOCUMENTS_PER_FILE))
  echo "=============== $i ==============="
done


