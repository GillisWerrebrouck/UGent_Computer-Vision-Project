#!/bin/bash
DATABASE='computervision'
COLLECTION='images'
BSON_FILE='/docker-entrypoint-initdb.d/images.bson'
USERNAME='devuser'
PASSWORD='devpwd'
MONGO_OPTS="-u $USERNAME -p $PASSWORD --authenticationDatabase=admin"

mongorestore $MONGO_OPTS -d $DATABASE -c $COLLECTION $BSON_FILE
