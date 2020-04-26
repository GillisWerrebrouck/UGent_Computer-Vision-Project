const {
  MongoClient,
  ObjectId
} = require('mongodb');
const images = require('./images.json');

function mapToNumber(value) {
  if (isNaN(value)) {
    return Number(value['$numberDouble']);
  }
  return value;
}

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

console.log('Mapping images');
// map the weird output of MongoDB
// (we do not save the mapped output to be compatible with future dumps)
const imagesToSave = images.map((image) => {
  const { _id, createdAt, corners } = image;
  const formattedCorners = fixCorners(corners.map((corner) => {
    const [x, y] = corner;
    return [mapToNumber(x), mapToNumber(y)];
  }));

  return {
    ...image,
    _id: new ObjectId(_id['$oid']),
    createdAt: new Date(createdAt['$date']),
    corners: formattedCorners,
  };
});

async function main() {
  console.log('Connecting to MongoDB');
  const client = await MongoClient.connect('mongodb://devuser:devpwd@mongodb:27017/computervision?authSource=admin', {
    useUnifiedTopology: true,
  });
  console.log('Connected');

  const db = client.db();
  const imagesCollection = db.collection('images');

  console.log('Deleting possible existing images');
  await imagesCollection.deleteMany();

  console.log('Populating database');
  await imagesCollection.insertMany(imagesToSave);

  console.log('Creating an index on the image filename');
  await imagesCollection.createIndex({ filename: 1 });

  await client.close();
}

(async () => await main())();
