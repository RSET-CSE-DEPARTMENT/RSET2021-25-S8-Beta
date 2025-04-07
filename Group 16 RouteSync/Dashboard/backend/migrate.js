const mongoose = require("mongoose");
const Agency = require("./models/Agency");
const Route = require("./models/Route");
const Stop = require("./models/Stop");
const StopTimes = require("./models/StopTimes");
const Trip = require("./models/Trip");

mongoose
  .connect(
    "mongodb+srv://elviinteldho:hW1E0sOVvaSPUpMX@routesync.nzpyk.mongodb.net/?retryWrites=true&w=majority&appName=RouteSync",
    {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    }
  )
  .then(() => console.log("✅ Connected to MongoDB"))
  .catch((error) => {
    console.error("❌ MongoDB Connection Error:", error);
    process.exit(1);
  });

async function migrateData() {
  try {
    console.log("🚀 Starting Migration...");

    // Convert route agency_id from String to ObjectId
    const routes = await Route.find();
    console.log(`🔍 Found ${routes.length} routes`);

    for (let i = 0; i < routes.length; i++) {
      const route = routes[i];
      console.log(
        `🔄 Processing route ${i + 1}/${routes.length}: ${route.route_id}`
      );

      const agency = await Agency.findOne({ agency_id: route.agency_id });
      if (agency) {
        console.log(
          `✅ Found agency for route ${route}`
        );
        route.agency_id = agency._id;
        await route.save();
      } else {
        console.warn(`⚠️ No agency found for route ${route}`);
      }
    }

    // Convert trip route_id from String to ObjectId
    const trips = await Trip.find();
    console.log(`🔍 Found ${trips.length} trips`);

    for (let i = 0; i < trips.length; i++) {
      const trip = trips[i];
      console.log(
        `🔄 Processing trip ${i + 1}/${trips.length}: ${trip.trip_id}`
      );

      const route = await Route.findOne({ route_id: trip.route_id });
      if (route) {
        console.log(`✅ Found route for trip ${trip.trip_id}`);
        trip.route_id = route._id;
        await trip.save();
      } else {
        console.warn(`⚠️ No route found for trip ${trip.trip_id}`);
      }
    }

    // Convert stop_times stop_id to ObjectId
    const stopTimes = await StopTimes.find();
    console.log(`🔍 Found ${stopTimes.length} stop times`);

    for (let i = 0; i < stopTimes.length; i++) {
      const stopTime = stopTimes[i];
      console.log(`🔄 Processing stop time ${i + 1}/${stopTimes.length}`);

      const stop = await Stop.findOne({ stop_id: stopTime.stop_id });
      if (stop) {
        console.log(`✅ Found stop for stop time entry`);
        stopTime.stop_id = stop._id;
        await stopTime.save();
      } else {
        console.warn(`⚠️ No stop found for stop time entry`);
      }
    }

    console.log("✅ Migration Completed Successfully!");
    mongoose.connection.close();
  } catch (error) {
    console.error("❌ Migration Failed:", error);
    mongoose.connection.close();
  }
}

migrateData();
