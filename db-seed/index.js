const {
  MongoClient,
  ObjectId
} = require('mongodb');
const fs = require('fs');

/**
 * Sometimes the corners are sorted in the wrong order, so fix this.
 */
function fixCorners(corners) {
  let tmp;
  let [A, B, C, D] = corners;

  if (A[0] > B[0]) {
    tmp = B;
    B = A;
    A = tmp;
  }

  if (C[0] < D[0]) {
    tmp = C;
    C = D;
    D = tmp;
  }

  return [A, B, C, D];
}

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
      corners,
      sobel,
      histograms: {
        full_histogram,
        block_histogram,
      },
      good_features,
    } = image;
    const fixedCorners = fixCorners(corners);

    return {
      ...image,
      _id: new ObjectId(_id),
      createdAt: new Date(createdAt),
      corners: fixedCorners,
      sobel: Buffer.from(sobel, 'base64'),
      good_features: Buffer.from(good_features, 'base64'),
      histograms: {
        full_histogram: Buffer.from(full_histogram, 'base64'),
        block_histogram: Buffer.from(block_histogram, 'base64'),
      }
    };
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
  const client = await MongoClient.connect('mongodb://devuser:devpwd@localhost:27017/cv-temp?authSource=admin', {
    useUnifiedTopology: true,
  });
  console.log('Connected');

  const db = client.db();
  const imagesCollection = db.collection('img');

  console.log('Deleting possible existing images');
  await imagesCollection.deleteMany();

  const files = getAllJSONDumpFiles();
  console.log(files);

  console.log('Populating database');
  for (let i = 0; i < files.length; i++) {
    const filename = files[i];
    console.log(`${filename} started`);
    const images = getParsedFileContent(filename);
    await imagesCollection.insertMany(images);
    console.log(`${filename} done`);
  }

  console.log('Creating a couple of indices (filename and room)');
  await imagesCollection.createIndexes([
    { key: { filename: 1, }, background: true },
    { key: { room: 1 }, background: true },
  ]);

  await client.close();
}

(async () => await main())();
