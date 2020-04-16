DATABASE='cv-temp'
COLLECTION='images' # necessary for JSON files
OUTPUT_DIR='out'
DUMP_FOLDER='mongo-dump'

##############
# BSON FILES #
##############
for FILE in dump_*.zip; do
    echo "==> Processing $FILE"
    # unzip the file
    unzip $FILE -d $OUTPUT_DIR

    # restore the BSON data in the specified database
    mongorestore -d $DATABASE $OUTPUT_DIR/$DUMP_FOLDER

    # remove all created data
    rm -rf $OUTPUT_DIR
done

##############
# JSON FILES #
##############
for FILE in dump_*.json; do
    echo "==> Processing $FILE"
    mongoimport -d $DATABASE -c $COLLECTION --file $FILE
done
