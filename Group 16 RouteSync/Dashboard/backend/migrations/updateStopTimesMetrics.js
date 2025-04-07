const mongoose = require('mongoose');
const StopTimes = require('../models/StopTimes');

const MONGODB_URI = 'mongodb+srv://elviinteldho:vjFrU6LslwMEW76B@routesync.nzpyk.mongodb.net/?retryWrites=true&w=majority&appName=RouteSync';

// Add connection options
const mongooseOptions = {
  useNewUrlParser: true,
  useUnifiedTopology: true,
  serverSelectionTimeoutMS: 5000,
  socketTimeoutMS: 45000,
};

// Helper function to parse time string to milliseconds
function parseTimeString(timeStr) {
  const [hours, minutes, seconds] = timeStr.split(':').map(Number);
  return (hours * 3600 + minutes * 60 + seconds) * 1000;
}

// Helper function to calculate dwell time
function calculateDwellTime(arrivalTime, departureTime) {
  const arrival = parseTimeString(arrivalTime);
  const departure = parseTimeString(departureTime);
  return (departure - arrival) / 1000; // Convert to seconds
}

async function updateStopTimesMetrics() {
  try {
    // Connect to MongoDB with better error handling
    console.log('Attempting to connect to MongoDB...');
    await mongoose.connect(MONGODB_URI, mongooseOptions);
    console.log('Successfully connected to MongoDB');

    // Verify StopTimes model is loaded
    console.log('\nVerifying StopTimes model...');
    console.log(`- ${StopTimes.modelName} model loaded`);

    // Update StopTimes Metrics
    console.log('\nUpdating StopTimes Metrics...');
    const stopTimes = await StopTimes.find({});
    console.log(`Found ${stopTimes.length} stop times to update`);

    let updatedCount = 0;
    for (const stopTime of stopTimes) {
      try {
        // Calculate dwell time
        const dwellTime = calculateDwellTime(stopTime.arrival_time, stopTime.departure_time);

        // Calculate headway (time between consecutive trips at the same stop)
        const previousStopTime = await StopTimes.findOne({
          stop_id: stopTime.stop_id,
          departure_time: { $lt: stopTime.arrival_time }
        }).sort({ departure_time: -1 });

        let headway = null;
        if (previousStopTime) {
          const currentArrival = parseTimeString(stopTime.arrival_time);
          const previousDeparture = parseTimeString(previousStopTime.departure_time);
          headway = (currentArrival - previousDeparture) / 1000; // Convert to seconds
        }

        await StopTimes.findByIdAndUpdate(stopTime._id, {
          $set: {
            'stop_time_metrics.dwell_time': dwellTime,
            'stop_time_metrics.headway_secs': headway,
            'stop_time_metrics.last_updated': new Date()
          }
        });

        updatedCount++;
        if (updatedCount % 1000 === 0) {
          console.log(`Updated ${updatedCount} stop times...`);
        }
      } catch (stopTimeError) {
        console.error(`Error updating stop time ${stopTime._id}:`, stopTimeError.message);
      }
    }

    console.log(`\nMigration completed successfully:`);
    console.log(`- Total stop times processed: ${stopTimes.length}`);
    console.log(`- Successfully updated: ${updatedCount}`);
    console.log(`- Failed to update: ${stopTimes.length - updatedCount}`);

    // Close the connection
    await mongoose.connection.close();
    console.log('\nDatabase connection closed');
  } catch (error) {
    console.error('\nMigration failed with error:', error.message);
    if (error.code === 'MODULE_NOT_FOUND') {
      console.error('\nModule not found error. Please check:');
      console.error('1. You are in the correct directory');
      console.error('2. StopTimes model is properly imported');
      console.error('3. The file path is correct');
    } else if (error.name === 'MongoServerSelectionError') {
      console.error('\nMongoDB connection error. Please check:');
      console.error('1. Your MongoDB connection string is correct');
      console.error('2. Your network connection is working');
      console.error('3. MongoDB Atlas is accessible');
    }
    process.exit(1);
  }
}

// Run the migration
console.log('Starting StopTimes metrics update migration...');
updateStopTimesMetrics(); 