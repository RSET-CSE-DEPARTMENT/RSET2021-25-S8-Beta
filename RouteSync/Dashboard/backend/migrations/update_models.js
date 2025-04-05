const mongoose = require("mongoose");
const Agency = require("../models/Agency");
const Route = require("../models/Route");
const Stop = require("../models/Stop");
const StopTimes = require("../models/StopTimes");
const Trip = require("../models/Trip");

const migrateDatabase = async () => {
  const startTime = Date.now();
  console.log("\n=== Starting Database Migration ===");
  console.log(`Start Time: ${new Date().toISOString()}\n`);

  try {
    // Connect to MongoDB
    await mongoose.connect(
      process.env.MONGODB_URI || "mongodb+srv://elviinteldho:vjFrU6LslwMEW76B@routesync.nzpyk.mongodb.net/?retryWrites=true&w=majority&appName=RouteSync",
      {
        useNewUrlParser: true,
        useUnifiedTopology: true,
      }
    );

    console.log("Connected to MongoDB");

    // Migration steps
    await Promise.all([
      migrateAgencyCollection(),
      migrateRouteCollection(),
      migrateStopCollection(),
      migrateStopTimesCollection(),
      migrateTripCollection(),
    ]);

    const endTime = Date.now();
    const duration = (endTime - startTime) / 1000; // Convert to seconds
    console.log("\n=== Migration Summary ===");
    console.log(`End Time: ${new Date().toISOString()}`);
    console.log(`Total Duration: ${duration.toFixed(2)} seconds`);
    console.log("Migration completed successfully\n");
  } catch (error) {
    console.error("\n=== Migration Failed ===");
    console.error("Error:", error);
    throw error;
  } finally {
    await mongoose.disconnect();
    console.log("Disconnected from MongoDB");
  }
};

// Agency Collection Migration
async function migrateAgencyCollection() {
  console.log("\n--- Migrating Agency Collection ---");
  const startTime = Date.now();
  const agencies = await Agency.find({});
  console.log(`Found ${agencies.length} agencies to migrate`);

  let successCount = 0;
  let failureCount = 0;

  for (let i = 0; i < agencies.length; i++) {
    const agency = agencies[i];
    const progress = (((i + 1) / agencies.length) * 100).toFixed(1);

    try {
      console.log(
        `\nProcessing Agency ${i + 1}/${agencies.length} (${progress}%)`
      );
      console.log(`Agency ID: ${agency._id}`);

      // Add new fields with default values
      const updates = {
        agency_route_types: [1], // Default to route type 1
        agency_operating_area: {
          type: "Polygon",
          coordinates: [], // Will be populated later with actual coordinates
        },
        agency_metrics: {
          total_stops: 0,
          total_routes: 0,
          total_trips: 0,
          last_updated: new Date(),
        },
        agency_features: {
          has_rapid_transit: false,
          has_express_routes: false,
          has_airport_connectivity: false,
          has_intercity_connectivity: false,
        },
        agency_metadata: {
          established_date: agency.createdAt,
          last_route_update: agency.updatedAt,
          last_stop_update: agency.updatedAt,
          last_trip_update: agency.updatedAt,
        },
      };

      await Agency.findByIdAndUpdate(agency._id, { $set: updates });
      successCount++;
      console.log("✓ Agency updated successfully");
    } catch (error) {
      failureCount++;
      console.error("✗ Failed to update agency:", error.message);
    }
  }

  const duration = (Date.now() - startTime) / 1000;
  console.log("\n--- Agency Migration Summary ---");
  console.log(`Total Agencies: ${agencies.length}`);
  console.log(`Successful Updates: ${successCount}`);
  console.log(`Failed Updates: ${failureCount}`);
  console.log(`Duration: ${duration.toFixed(2)} seconds`);
}

// Route Collection Migration
async function migrateRouteCollection() {
  console.log("\n--- Migrating Route Collection ---");
  const startTime = Date.now();
  const routes = await Route.find({});
  console.log(`Found ${routes.length} routes to migrate`);

  let successCount = 0;
  let failureCount = 0;

  for (let i = 0; i < routes.length; i++) {
    const route = routes[i];
    const progress = (((i + 1) / routes.length) * 100).toFixed(1);

    try {
      console.log(
        `\nProcessing Route ${i + 1}/${routes.length} (${progress}%)`
      );
      console.log(`Route ID: ${route._id}`);

      // Add new fields with default values
      const updates = {
        route_desc: "",
        route_url: "",
        route_color: "#000000",
        route_text_color: "#FFFFFF",
        route_sort_order: 0,
        continuous_pickup: "1",
        continuous_drop_off: "1",
        route_status: "active",
        route_metrics: {
          total_stops: 0,
          total_trips: 0,
          average_trip_duration: 0,
          total_distance: 0,
          average_speed: 0,
          last_updated: new Date(),
        },
        route_schedule: {
          first_trip: "00:00",
          last_trip: "23:59",
          frequency: {
            peak_hours: 0,
            off_peak_hours: 0,
            weekend: 0,
          },
          operating_days: [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
          ],
        },
        route_features: {
          is_express: false,
          is_rapid: false,
          is_accessible: false,
          has_wifi: false,
          has_air_conditioning: false,
          has_bike_rack: false,
        },
        route_metadata: {
          created_at: route.createdAt,
          last_modified: route.updatedAt,
          last_trip_update: route.updatedAt,
          last_stop_update: route.updatedAt,
        },
        route_info: {
          start_stop: "",
          end_stop: "",
          major_stops: [],
          interchange_stations: [],
          fare_zones: [],
          estimated_travel_time: 0,
          wheelchair_accessible: false,
          bike_accessible: false,
        },
      };

      await Route.findByIdAndUpdate(route._id, { $set: updates });
      successCount++;
      console.log("✓ Route updated successfully");
    } catch (error) {
      failureCount++;
      console.error("✗ Failed to update route:", error.message);
    }
  }

  const duration = (Date.now() - startTime) / 1000;
  console.log("\n--- Route Migration Summary ---");
  console.log(`Total Routes: ${routes.length}`);
  console.log(`Successful Updates: ${successCount}`);
  console.log(`Failed Updates: ${failureCount}`);
  console.log(`Duration: ${duration.toFixed(2)} seconds`);
}

// Stop Collection Migration
async function migrateStopCollection() {
  console.log("\n--- Migrating Stop Collection ---");
  const startTime = Date.now();
  const stops = await Stop.find({});
  console.log(`Found ${stops.length} stops to migrate`);

  let successCount = 0;
  let failureCount = 0;

  for (let i = 0; i < stops.length; i++) {
    const stop = stops[i];
    const progress = (((i + 1) / stops.length) * 100).toFixed(1);

    try {
      console.log(`\nProcessing Stop ${i + 1}/${stops.length} (${progress}%)`);
      console.log(`Stop ID: ${stop._id}`);

      // Add new fields with default values
      const updates = {
        stop_desc: "",
        stop_url: "",
        location_type: "stop",
        stop_timezone: "Asia/Kolkata",
        wheelchair_boarding: "0",
        stop_status: "active",
        stop_metrics: {
          total_routes: 0,
          total_trips: 0,
          average_daily_boardings: 0,
          average_daily_alightings: 0,
          last_updated: new Date(),
        },
        stop_features: {
          has_elevator: false,
          has_escalator: false,
          has_stairs: true,
          has_ramp: false,
          has_ticket_counter: false,
          has_restroom: false,
          has_parking: false,
          has_bike_rack: false,
          has_wifi: false,
          has_charging_station: false,
        },
        stop_amenities: {
          has_retail: false,
          has_food_court: false,
          has_atm: false,
          has_pharmacy: false,
          has_newsstand: false,
        },
        stop_metadata: {
          created_at: stop.createdAt,
          last_modified: stop.updatedAt,
          last_route_update: stop.updatedAt,
          last_trip_update: stop.updatedAt,
        },
        stop_schedule: {
          first_arrival: "00:00",
          last_arrival: "23:59",
          operating_days: [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
          ],
        },
        stop_connections: {
          nearby_stops: [],
          interchange_routes: [],
        },
        stop_landmarks: [],
        stop_geography: {
          elevation: 0,
          terrain_type: "flat",
          is_underground: false,
          is_elevated: false,
        },
      };

      await Stop.findByIdAndUpdate(stop._id, { $set: updates });
      successCount++;
      console.log("✓ Stop updated successfully");
    } catch (error) {
      failureCount++;
      console.error("✗ Failed to update stop:", error.message);
    }
  }

  const duration = (Date.now() - startTime) / 1000;
  console.log("\n--- Stop Migration Summary ---");
  console.log(`Total Stops: ${stops.length}`);
  console.log(`Successful Updates: ${successCount}`);
  console.log(`Failed Updates: ${failureCount}`);
  console.log(`Duration: ${duration.toFixed(2)} seconds`);
}

// StopTimes Collection Migration
async function migrateStopTimesCollection() {
  console.log("\n--- Migrating StopTimes Collection ---");
  const startTime = Date.now();
  const stopTimes = await StopTimes.find({});
  console.log(`Found ${stopTimes.length} stop times to migrate`);

  let successCount = 0;
  let failureCount = 0;

  for (let i = 0; i < stopTimes.length; i++) {
    const stopTime = stopTimes[i];
    const progress = (((i + 1) / stopTimes.length) * 100).toFixed(1);

    try {
      console.log(
        `\nProcessing StopTime ${i + 1}/${stopTimes.length} (${progress}%)`
      );
      console.log(`StopTime ID: ${stopTime._id}`);

      // Add new fields with default values
      const updates = {
        stop_time_type: "scheduled",
        pickup_type: "0",
        drop_off_type: "0",
        shape_dist_traveled: 0,
        timepoint: true,
        stop_time_metrics: {
          dwell_time: 0,
          headway_secs: 0,
          passenger_load: 0,
          last_updated: new Date(),
        },
        stop_time_features: {
          is_timepoint: true,
          is_accessible: false,
          has_bike_rack: false,
          has_parking: false,
        },
        stop_time_metadata: {
          created_at: stopTime.createdAt,
          last_modified: stopTime.updatedAt,
          last_update: stopTime.updatedAt,
          update_source: "gtfs",
        },
        stop_time_schedule: {
          service_id: "",
          calendar_dates: [],
          exceptions: [],
        },
        stop_time_analytics: {
          average_dwell_time: 0,
          average_passenger_load: 0,
          reliability_score: 100,
          on_time_performance: 100,
          last_calculated: new Date(),
        },
        stop_time_alerts: [],
        stop_time_predictions: {
          predicted_arrival: stopTime.arrival_time,
          predicted_departure: stopTime.departure_time,
          confidence_score: 100,
          last_prediction: new Date(),
        },
      };

      await StopTimes.findByIdAndUpdate(stopTime._id, { $set: updates });
      successCount++;
      console.log("✓ StopTime updated successfully");
    } catch (error) {
      failureCount++;
      console.error("✗ Failed to update stop time:", error.message);
    }
  }

  const duration = (Date.now() - startTime) / 1000;
  console.log("\n--- StopTimes Migration Summary ---");
  console.log(`Total StopTimes: ${stopTimes.length}`);
  console.log(`Successful Updates: ${successCount}`);
  console.log(`Failed Updates: ${failureCount}`);
  console.log(`Duration: ${duration.toFixed(2)} seconds`);
}

// Trip Collection Migration
async function migrateTripCollection() {
  console.log("\n--- Migrating Trip Collection ---");
  const startTime = Date.now();
  const trips = await Trip.find({});
  console.log(`Found ${trips.length} trips to migrate`);

  let successCount = 0;
  let failureCount = 0;

  for (let i = 0; i < trips.length; i++) {
    const trip = trips[i];
    const progress = (((i + 1) / trips.length) * 100).toFixed(1);

    try {
      console.log(`\nProcessing Trip ${i + 1}/${trips.length} (${progress}%)`);
      console.log(`Trip ID: ${trip._id}`);

      // Add new fields with default values
      const updates = {
        trip_short_name: "",
        trip_long_name: "",
        direction_id: "0",
        block_id: "",
        wheelchair_accessible: "0",
        bikes_allowed: "0",
        trip_status: "scheduled",
        trip_metrics: {
          total_stops: 0,
          total_distance: 0,
          total_duration: 0,
          average_speed: 0,
          passenger_capacity: 0,
          last_updated: new Date(),
        },
        trip_schedule: {
          start_time: "00:00",
          end_time: "23:59",
          frequency: 0,
          operating_days: [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
          ],
        },
        trip_features: {
          is_express: false,
          is_rapid: false,
          is_accessible: false,
          has_wifi: false,
          has_air_conditioning: false,
          has_bike_rack: false,
        },
        trip_metadata: {
          created_at: trip.createdAt,
          last_modified: trip.updatedAt,
          last_update: trip.updatedAt,
          update_source: "gtfs",
        },
        trip_analytics: {
          average_passenger_load: 0,
          reliability_score: 100,
          on_time_performance: 100,
          last_calculated: new Date(),
        },
        trip_alerts: [],
        trip_predictions: {
          predicted_start: "00:00",
          predicted_end: "23:59",
          confidence_score: 100,
          last_prediction: new Date(),
        },
        stops: [],
      };

      await Trip.findByIdAndUpdate(trip._id, { $set: updates });
      successCount++;
      console.log("✓ Trip updated successfully");
    } catch (error) {
      failureCount++;
      console.error("✗ Failed to update trip:", error.message);
    }
  }

  const duration = (Date.now() - startTime) / 1000;
  console.log("\n--- Trip Migration Summary ---");
  console.log(`Total Trips: ${trips.length}`);
  console.log(`Successful Updates: ${successCount}`);
  console.log(`Failed Updates: ${failureCount}`);
  console.log(`Duration: ${duration.toFixed(2)} seconds`);
}

// Run migration
migrateDatabase()
  .then(() => {
    console.log("\n=== Migration Completed Successfully ===");
    process.exit(0);
  })
  .catch((error) => {
    console.error("\n=== Migration Failed ===");
    console.error("Error:", error);
    process.exit(1);
  });
