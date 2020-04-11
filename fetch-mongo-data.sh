#!/bin/bash

MONGO_CONTAINER_DUMP_DIR='./.mongodb/dump'
MONGO_LOCAL_DUMP_DIR='mongo-dump'

# let the container dumps its data
echo '==> Hey container! Dump your data!'
docker exec mongodb /scripts/data-dump.sh

# remove previous dump if existing
echo '==> Removing previous dump if existing'
[[ -d $MONGO_LOCAL_DUMP_DIR ]] && rm -rf $MONGO_LOCAL_DUMP_DIR

# move the dump file to the data dir
echo "==> Moving dump to output folder: $MONGO_LOCAL_DUMP_DIR"
mv "$MONGO_CONTAINER_DUMP_DIR" "$MONGO_LOCAL_DUMP_DIR"
