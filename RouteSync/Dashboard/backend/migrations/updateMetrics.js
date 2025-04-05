const mongoose = require('mongoose');
const Agency = require('../models/Agency');
const Route = require('../models/Route');
const Stop = require('../models/Stop');
const Trip = require('../models/Trip');
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

async function updateMetrics() {
  try {
    // Connect to MongoDB with better error handling
    console.log('Attempting to connect to MongoDB...');
    await mongoose.connect(MONGODB_URI, mongooseOptions);
    console.log('Successfully connected to MongoDB');

    // Verify models are loaded
    console.log('\nVerifying models...');
    const models = [Agency, Route, Stop, Trip, StopTimes];
    for (const model of models) {
      console.log(`- ${model.modelName} model loaded`);
    }

    // Update Agency Metrics
    console.log('\nUpdating Agency Metrics...');
    const agencies = await Agency.find({});
    for (const agency of agencies) {
      const [routeCount, stopCount, tripCount] = await Promise.all([
        Route.countDocuments({ agency_id: agency.agency_id }),
        Stop.countDocuments({ agency_id: agency.agency_id }),
        Trip.countDocuments({ agency_id: agency.agency_id })
      ]);

      await Agency.findByIdAndUpdate(agency._id, {
        $set: {
          'agency_metrics.total_routes': routeCount,
          'agency_metrics.total_stops': stopCount,
          'agency_metrics.total_trips': tripCount,
          'agency_metrics.last_updated': new Date()
        }
      });
    }
    console.log(`Updated metrics for ${agencies.length} agencies`);

    // Update Route Metrics
    console.log('\nUpdating Route Metrics...');
    const routes = await Route.find({});
    for (const route of routes) {
      const [tripCount, stopCount] = await Promise.all([
        Trip.countDocuments({ route_id: route.route_id }),
        Stop.countDocuments({ route_id: route.route_id })
      ]);

      // Calculate route distance if coordinates exist
      let totalDistance = 0;
      if (route.coordinates && route.coordinates.length > 1) {
        totalDistance = route.calculateDistance();
      }

      await Route.findByIdAndUpdate(route._id, {
        $set: {
          'route_metrics.total_trips': tripCount,
          'route_metrics.total_stops': stopCount,
          'route_metrics.total_distance': totalDistance,
          'route_metrics.last_updated': new Date()
        }
      });
    }
    console.log(`Updated metrics for ${routes.length} routes`);

    // Update Stop Metrics
    console.log('\nUpdating Stop Metrics...');
    const stops = await Stop.find({});
    for (const stop of stops) {
      const [routeCount, tripCount] = await Promise.all([
        Route.countDocuments({ 'route_info.major_stops': stop.stop_id }),
        Trip.countDocuments({ 'stops.stop_id': stop.stop_id })
      ]);

      await Stop.findByIdAndUpdate(stop._id, {
        $set: {
          'stop_metrics.total_routes': routeCount,
          'stop_metrics.total_trips': tripCount,
          'stop_metrics.last_updated': new Date()
        }
      });
    }
    console.log(`Updated metrics for ${stops.length} stops`);

    // Update Trip Metrics
    console.log('\nUpdating Trip Metrics...');
    const trips = await Trip.find({});
    for (const trip of trips) {
      const stopCount = trip.stops.length;
      let totalDuration = 0;

      if (trip.stops.length > 0) {
        const firstStop = trip.stops[0];
        const lastStop = trip.stops[trip.stops.length - 1];
        const startTime = parseTimeString(firstStop.departure_time);
        const endTime = parseTimeString(lastStop.arrival_time);
        totalDuration = (endTime - startTime) / (1000 * 60); // Convert to minutes
      }

      await Trip.findByIdAndUpdate(trip._id, {
        $set: {
          'trip_metrics.total_stops': stopCount,
          'trip_metrics.total_duration': totalDuration,
          'trip_metrics.last_updated': new Date()
        }
      });
    }
    console.log(`Updated metrics for ${trips.length} trips`);

    // Update StopTimes Metrics
    console.log('\nUpdating StopTimes Metrics...');
    const stopTimes = await StopTimes.find({});
    for (const stopTime of stopTimes) {
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
    }
    console.log(`Updated metrics for ${stopTimes.length} stop times`);

    // Close the connection
    await mongoose.connection.close();
    console.log('\nDatabase connection closed');
  } catch (error) {
    console.error('\nMigration failed with error:', error.message);
    if (error.code === 'MODULE_NOT_FOUND') {
      console.error('\nModule not found error. Please check:');
      console.error('1. You are in the correct directory');
      console.error('2. All required models are properly imported');
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
console.log('Starting metrics update migration...');
updateMetrics(); 