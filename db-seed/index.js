const {
    MongoClient,
    ObjectId
} = require('mongodb');
const fs = require('fs');

const MONGO_USER = 'devuser';
const MONGO_PWD = 'devpwd';
const MONGO_HOST = 'mongodb';
const MONGO_PORT = 27017;
const MONGO_DATABASE = 'computervision';
const MONGO_COLLECTION = 'images';

/**
 * Make the given images ready to save in the database.
 *
 * @param {object[]} images - Images to save.
 */
function formatImages(images) {
    console.log(`Mapping ${images.length} images`);

    return images.map((image) => {
        const {
            _id,
            createdAt,
            histograms,
            good_features,
        } = image;

        const parsedImage = {
            ...image,
            _id: new ObjectId(_id),
            createdAt: new Date(createdAt),
        };

        if (good_features) {
            parsedImage.good_features = Buffer.from(good_features, 'base64');
        }

        if (histograms) {
            const {
                full_histogram,
                block_histogram,
            } = histograms;

            parsedImage.histograms = {
                full_histogram: Buffer.from(full_histogram, 'base64'),
                block_histogram: Buffer.from(block_histogram, 'base64'),
            };
        }

        return parsedImage;
    });
}

function getAllJSONDumpFiles() {
    const dir = 'dump';
    const files = fs.readdirSync(dir);
    return files.filter((filename) => filename.endsWith('.json'))
        .map((filename) => `${dir}/${filename}`);
}

function getParsedFileContent(file) {
    const buffer = fs.readFileSync(file);
    const images = JSON.parse(buffer.toString());
    return formatImages(images);
}

// all fs actions are sync to save memory!
async function main() {
    console.log('Connecting to MongoDB');
    const client = await MongoClient.connect(`mongodb://${MONGO_USER}:${MONGO_PWD}@${MONGO_HOST}:${MONGO_PORT}/${MONGO_DATABASE}?authSource=admin`, {
        useUnifiedTopology: true,
    });
    console.log('Connected');

    const db = client.db();
    const imagesCollection = db.collection(MONGO_COLLECTION);

    console.log('Deleting possible existing images');
    await imagesCollection.deleteMany();

    const files = getAllJSONDumpFiles();

    console.log('Populating database');
    for (let i = 0; i < files.length; i++) {
        const filename = files[i];
        console.log(`${filename} started`);
        const images = getParsedFileContent(filename);
        await imagesCollection.insertMany(images);
        console.log(`${filename} done`);
    }

    console.log('Creating a couple of indices (filename and room)');
    await imagesCollection.createIndexes([{
            key: {
                filename: 1,
            },
            background: true
        },
        {
            key: {
                room: 1
            },
            background: true
        },
    ]);

    await client.close();
}

(async () => await main())();
