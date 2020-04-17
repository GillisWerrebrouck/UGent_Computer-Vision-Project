DATABASE='cv-temp'
COLLECTION='images' # necessary for JSON files
OUTPUT_DIR='out'
DUMP_FOLDER='mongo-dump'
USERNAME='devuser'
PASSWORD='devpwd'

##############
# BSON FILES #
##############
for FILE in dump_*.zip; do
    echo "==> Processing $FILE"
    # unzip the file
    unzip $FILE -d $OUTPUT_DIR

    # restore the BSON data in the specified database
    mongorestore -d $DATABASE -u $USERNAME -p $PASSWORD --authenticationDatabase=admin $OUTPUT_DIR/$DUMP_FOLDER

    # remove all created data
    rm -rf $OUTPUT_DIR
done

##############
# JSON FILES #
##############
for FILE in dump_*.json; do
    echo "==> Processing $FILE"
    mongoimport -d $DATABASE -u $USERNAME -p $PASSWORD --authenticationDatabase=admin -c $COLLECTION --file $FILE
done

mongodump --db $DATABASE -u $USERNAME -p $PASSWORD --authenticationDatabase=admin
