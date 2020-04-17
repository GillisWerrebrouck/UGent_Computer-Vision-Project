#!/bin/bash

mongodump --db computervision -u devuser -p devpwd --authenticationDatabase=admin

mv /dump/computervision/ /data/db/dump/
rm -rf dump
