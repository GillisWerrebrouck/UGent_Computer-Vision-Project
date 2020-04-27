const {
    MongoClient,
} = require('mongodb');
const fs = require('fs');

class Dumper {

    constructor() {
        this.hadPrevious = false;
        this.maxBytes = 50 * 1000 * 1000; // 50MB on UGent GitHub
        this.bytesInCurrentFile = 0;
        this.fileCount = 0;
        this.fileHandle;
        this.comma = Buffer.from(',');
    }

    openNewFile() {
        console.log(`==> Opening file ${this.fileCount}`);
        this.fileHandle = fs.openSync(`dump/dump_${this.fileCount}.json`, 'w+');

        // Write the start of the JSON array
        fs.writeSync(this.fileHandle, Buffer.from('['));
    }

    closeFile() {
        console.log(`==> Closing file ${this.fileCount}`);
        if (this.fileHandle) {
            // Write the end of the JSON array
            fs.writeSync(this.fileHandle, Buffer.from(']'));
            fs.closeSync(this.fileHandle);

            this.fileHandle = null;
            this.hadPrevious = false;
            this.fileCount += 1;
            this.bytesInCurrentFile = 0;
        }
    }

    bulkWrite(images) {
        images.forEach((image) => this.write(image));
    }

    write(image) {
        if (!this.fileHandle) {
            this.openNewFile();
        }

        const jsonBuffer = Buffer.from(JSON.stringify(image));
        if (this.bytesInCurrentFile + jsonBuffer.length > this.maxBytes) {
            this.closeFile();
            this.openNewFile();
        }

        if (this.hadPrevious) {
            fs.writeSync(this.fileHandle, this.comma);
        }

        fs.writeSync(this.fileHandle, jsonBuffer);

        this.bytesInCurrentFile += this.comma.length + jsonBuffer.length;
        this.hadPrevious = true;
    }
}

async function main() {
    console.log('Connecting to MongoDB');
    const client = await MongoClient.connect('mongodb://devuser:devpwd@localhost:27017/computervision?authSource=admin', {
        useUnifiedTopology: true,
    });
    console.log('Connected');

    const db = client.db();
    const imagesCollection = db.collection('images');

    console.time('Image dump');
    console.log('Dumping images');

    const dumper = new Dumper();
    const batchSize = 20;
    const count = await imagesCollection.countDocuments();
    const nrOfBatches = Math.ceil(count / batchSize);
    console.log(`Will need ${nrOfBatches} batches to fetch all data`);

    const promises = [];

    console.log(`Fetching ${count} documents, hold on...`);
    // batch collect the images
    for (let i = 0; i < nrOfBatches; i++) {
        promises.push(imagesCollection
            .find()
            .skip(i * batchSize)
            .limit(batchSize)
            .toArray()
            .then((images) => {
                dumper.bulkWrite(images);
                console.log(`Batch ${i} done`);
            })
        );
    }

    await Promise.all(promises);
    console.timeEnd('Image dump');

    // close a file that may be left open
    dumper.closeFile();

    await client.close();
}

(async () => await main())();
