const fs = require("fs");
const csv = require("csv-parser");
const mongoose = require("mongoose");

// Import the StopTimes model
const StopTimes = require("../models/StopTimes");

/**
 * Transform a row of CSV data:
 * - Remove attributes that are not in the StopTimes schema.
 * - Convert values to match the schema types.
 *
 * Expected CSV columns:
 * trip_id,arrival_time,departure_time,stop_id,stop_sequence,
 * stop_headsign,pickup_type,drop_off_type,shape_dist_traveled,
 * timepoint,continuous_pickup,continuous_drop_off
 *
 * Only the first five columns are used.
 *
 * @param {Object} row - The CSV row.
 * @param {Mongoose.Model} Model - The StopTimes model.
 * @returns {Object} - Transformed object with only valid StopTimes keys.
 */
function transformRow(row, Model) {
  const transformed = {};
  const schemaPaths = Model.schema.paths;

  // Iterate over keys defined in the StopTimes schema.
  for (const key of Object.keys(schemaPaths)) {
    // Skip internal keys.
    if (key === "__v" || key === "createdAt" || key === "updatedAt") continue;

    if (row.hasOwnProperty(key)) {
      let value = row[key];
      const typeName = schemaPaths[key].instance;

      if (typeName === "Number") {
        const num = Number(value);
        transformed[key] = isNaN(num) ? undefined : num;
      } else if (typeName === "Date") {
        const date = new Date(value);
        transformed[key] = isNaN(date.getTime()) ? undefined : date;
      } else if (typeName === "Boolean") {
        transformed[key] =
          typeof value === "string" ? value.toLowerCase() === "true" : Boolean(value);
      } else {
        transformed[key] = value;
      }
    }
  }
  return transformed;
}

/**
 * Import StopTimes data from a CSV file.
 * @param {String} filePath - Path to the CSV file.
 */
async function importStopTimes(filePath) {
  console.log(`🚀 Starting import: ${filePath} -> StopTimes`);
  const batchSize = 500;
  let batch = [];
  let totalProcessed = 0;

  const stream = fs.createReadStream(filePath).pipe(csv({ separator: "," }));

  try {
    for await (const row of stream) {
      // Transform each row to contain only StopTimes fields.
      const transformedRow = transformRow(row, StopTimes);
      batch.push(transformedRow);
      totalProcessed++;

      if (batch.length >= batchSize) {
        console.log(`✅ Inserting ${totalProcessed} records into StopTimes`);
        await insertBatch(batch);
        console.log(`✅ Inserted ${totalProcessed} records into StopTimes`);
        batch = [];
      }
    }
  } catch (err) {
    console.error("Error during stream processing:", err);
  }

  if (batch.length > 0) {
    await insertBatch(batch);
  }

  console.log(`🎉 Finished importing ${filePath} -> StopTimes: ${totalProcessed} records processed.`);
}

/**
 * Insert a batch of StopTimes documents using bulkWrite with upsert.
 * Uses a composite key: { trip_id, stop_id, stop_sequence }.
 * @param {Array} batch - Array of transformed StopTimes documents.
 */
async function insertBatch(batch) {
  try {
    const bulkOps = batch.map((doc) => ({
      updateOne: {
        filter: {
          trip_id: doc.trip_id,
          stop_id: doc.stop_id,
          stop_sequence: doc.stop_sequence,
        },
        update: { $set: doc },
        upsert: true,
      },
    }));

    const result = await StopTimes.bulkWrite(bulkOps, { ordered: false });
    console.log("BulkWrite result:", result);
    console.log("Inserted batch successfully...");
  } catch (error) {
    if (error.code === 11000) {
      console.warn("⚠️ Duplicate key error in StopTimes, skipping duplicates.");
    } else {
      console.error("❌ Error inserting batch into StopTimes:", error);
    }
  }
}

/**
 * Verify that StopTimes data has been successfully added.
 * Logs the total count and a sample document.
 */
async function verifyStopTimes() {
  try {
    const count = await StopTimes.countDocuments();
    console.log(`Verification for StopTimes: Found ${count} documents.`);
    if (count > 0) {
      const sampleDoc = await StopTimes.findOne();
      console.log("Sample document:", sampleDoc);
      console.log("Data verification successful: Documents have been added.");
    } else {
      console.log("Data verification failed: No documents found.");
    }
  } catch (error) {
    console.error("Error verifying data for StopTimes:", error);
  }
}

async function importData() {
  await mongoose.connect(
    "mongodb+srv://elviinteldho:vjFrU6LslwMEW76B@routesync.nzpyk.mongodb.net/?retryWrites=true&w=majority&appName=RouteSync"
  );
  console.log("Connected to MongoDB");

  await importStopTimes("data/stop_times.txt");

  console.log("Data import completed.");

  await verifyStopTimes();

  await mongoose.disconnect();
  console.log("Disconnected from MongoDB");
}

// Call the function to start the import process.
importData();
