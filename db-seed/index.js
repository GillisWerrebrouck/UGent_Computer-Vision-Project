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

console.log('Mapping images');
// map the weird output of MongoDB
// (we do not save the mapped output to be compatible with future dumps)
const imagesToSave = images.map((image) => {
  const { _id, createdAt, corners } = image;
  const formattedCorners = corners.map((corner) => {
    const [x, y] = corner;
    return [mapToNumber(x), mapToNumber(y)];
  });

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

  await client.close();
}

(async () => await main())();
