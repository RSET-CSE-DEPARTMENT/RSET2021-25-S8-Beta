const fs = require("fs");
const csv = require("csv-parser");
const mongoose = require("mongoose");

// Import your models
const Agency = require("../models/Agency");
const Route = require("../models/Route");
const Trip = require("../models/Trip");
const Stop = require("../models/Stop");
const StopTimes = require("../models/StopTimes");

/**
 * Import data from a comma-separated .txt file into a MongoDB collection.
 * @param {String} filePath - Path to the .txt file.
 * @param {Mongoose.Model} Model - Mongoose model for the target collection.
 */

// async function importTxtToDatabase(filePath, Model, uniqueField) {
//   console.log(`🚀 Starting import: ${filePath} -> ${Model.modelName}`);

//   const batchSize = 500; // Process in batches of 500 records
//   let batch = [];
//   let totalProcessed = 0; // Track total processed records
//   let duplicatesSkipped = 0;

//   return new Promise((resolve, reject) => {
//     const startTime = Date.now();

//     fs.createReadStream(filePath)
//       .pipe(csv({ separator: "," }))
//       .on("data", async (row) => {
//         batch.push(row);
//         totalProcessed++;
//         if (batch.length >= batchSize) {
//           console.log(
//             `✅ Inserting ${totalProcessed} records into ${Model.modelName}`
//           );
//           insertBatch(batch, Model, uniqueField);
//           console.log(
//             `✅ Inserted ${totalProcessed} records into ${Model.modelName}`
//           );
//           batch = [];
//         }
//       })
//       .on("end", async () => {
//         if (batch.length > 0) {
//           await insertBatch(batch, Model, uniqueField);
//         }

//         const endTime = Date.now();
//         console.log(
//           `🎉 Finished importing ${filePath} -> ${
//             Model.modelName
//           }: ${totalProcessed} records processed, ${duplicatesSkipped} duplicates skipped. ⏱️ Time taken: ${
//             (endTime - startTime) / 1000
//           }s`
//         );
//         resolve();
//       })
//       .on("error", (error) => {
//         console.error(`❌ Error processing ${filePath}:`, error);
//         reject(error);
//       });
//   });
// }
async function importTxtToDatabase(filePath, Model, uniqueField) {
  console.log(`🚀 Starting import: ${filePath} -> ${Model.modelName}`);
  const batchSize = 100;
  let batch = [];
  let totalProcessed = 0;

  const stream = fs.createReadStream(filePath).pipe(csv({ separator: "," }));

  try {
    for await (const row of stream) {
      console.log(row);

      batch.push(row);
      totalProcessed++;

      if (batch.length >= batchSize) {
        console.log(
          `✅ Inserting ${totalProcessed} records into ${Model.modelName}`
        );
        await insertBatch(batch, Model, uniqueField);
        console.log(
          `✅ Inserted ${totalProcessed} records into ${Model.modelName}`
        );
        batch = [];
      }
    }
  } catch (err) {
    console.error("Error during stream processing:", err);
  }

  if (batch.length > 0) {
    await insertBatch(batch, Model, uniqueField);
  }

  console.log(
    `🎉 Finished importing ${filePath} -> ${Model.modelName}: ${totalProcessed} records processed.`
  );
}

// async function importTxtToDatabase(filePath, Model, uniqueField) {
//   console.log(`🚀 Starting import: ${filePath} -> ${Model.modelName}`);

//   const batchSize = 100;
//   let batch = [];
//   let totalProcessed = 0;

//   const stream = fs.createReadStream(filePath).pipe(csv({ separator: "," }));

//   for await (const row of stream) {
//     batch.push(row);
//     totalProcessed++;

//     if (batch.length >= batchSize) {
//       console.log(
//         `✅ Inserting ${totalProcessed} records into ${Model.modelName}`
//       );
//       await insertBatch(batch, Model, uniqueField);
//       console.log(
//         `✅ Inserted ${totalProcessed} records into ${Model.modelName}`
//       );
//       batch = [];
//     }
//   }

//   if (batch.length > 0) {
//     await insertBatch(batch, Model, uniqueField);
//   }

//   const endTime = Date.now();
//   console.log(
//     `🎉 Finished importing ${filePath} -> ${Model.modelName}: ${totalProcessed} records processed.`
//   );
// }

async function insertBatch(batch, Model, uniqueField) {
  try {
    await Model.bulkWrite(
      batch.map((doc) => ({
        updateOne: {
          filter: { [uniqueField]: doc[uniqueField] },
          update: { $set: doc },
          upsert: true,
        },
      })),
      { ordered: false }
    );
    console.log("Inserted...");
  } catch (error) {
    if (error.code === 11000) {
      console.warn(
        `⚠️ Duplicate key error in ${Model.modelName}, skipping duplicates.`
      );
    } else {
      console.error(`❌ Error inserting batch into ${Model.modelName}:`, error);
    }
  }
}

// Example usage (replace with the correct file path)
const importData = async () => {
  await mongoose.connect(
    "mongodb+srv://elviinteldho:vjFrU6LslwMEW76B@routesync.nzpyk.mongodb.net/?retryWrites=true&w=majority&appName=RouteSync"
  );

  console.log("Connected to MongoDB");

  // await importTxtToDatabase("data/agency.txt", Agency, "agency_id");
  // await importTxtToDatabase("data/routes.txt", Route, "route_id");
  // await importTxtToDatabase("data/trips.txt", Trip, "trip_id");
  // await importTxtToDatabase("data/stops.txt", Stop, "stop_id");
  await importTxtToDatabase("data/stop_times.txt", StopTimes);

  console.log("Data import completed.");

  // Disconnect to allow the process to exit
  await mongoose.disconnect();
  console.log("Disconnected from MongoDB");
};

// Call the function to import data
importData();
