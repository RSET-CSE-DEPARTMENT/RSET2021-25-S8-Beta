const express = require("express");
const Trip = require("../models/Trip");
const router = express.Router();

// Fields to include in different response types
const tripListFields = {
  trip_id: 1,
  route_id: 1,
  service_id: 1,
  trip_short_name: 1,
  trip_long_name: 1,
  direction_id: 1,
  block_id: 1,
  wheelchair_accessible: 1,
  bikes_allowed: 1,
  trip_status: 1,
  trip_metrics: {
    total_stops: 1,
    total_distance: 1,
    total_duration: 1
  },
  trip_features: {
    is_express: 1,
    is_rapid: 1,
    is_accessible: 1
  },
  trip_metadata: {
    created_at: 1,
    last_modified: 1,
    last_update: 1
  }
};

const tripDetailFields = {
  ...tripListFields,
  trip_metrics: 1,
  trip_schedule: 1,
  trip_features: 1,
  trip_metadata: 1,
  trip_analytics: 1,
  trip_alerts: 1,
  trip_predictions: 1,
  stops: 1
};

const tripMapFields = {
  trip_id: 1,
  route_id: 1,
  trip_short_name: 1,
  trip_long_name: 1,
  direction_id: 1,
  trip_status: 1,
  trip_metrics: {
    total_stops: 1,
    total_duration: 1
  },
  stops: {
    stop_id: 1,
    sequence: 1,
    arrival_time: 1,
    departure_time: 1
  }
};

// Create a new trip
router.post("/", async (req, res) => {
  try {
    // Only allow specific fields to be set during creation
    const allowedFields = {
      trip_id: req.body.trip_id,
      route_id: req.body.route_id,
      service_id: req.body.service_id,
      trip_short_name: req.body.trip_short_name,
      trip_long_name: req.body.trip_long_name,
      direction_id: req.body.direction_id,
      block_id: req.body.block_id,
      wheelchair_accessible: req.body.wheelchair_accessible,
      bikes_allowed: req.body.bikes_allowed
    };

    const trip = new Trip(allowedFields);
    await trip.save();
    
    // Return only necessary fields
    const response = await Trip.findById(trip._id).select(tripListFields);
    res.status(201).json(response);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// Get trip data for map display
router.get("/map-data", async (req, res) => {
  try {
    const trips = await Trip.find()
      .select(tripMapFields)
      .lean();
    res.json(trips);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Get all trips with pagination and search
router.get("/", async (req, res) => {
  try {
    let { page = 1, limit = 50, trip_id, fields } = req.query;
    page = parseInt(page);
    limit = parseInt(limit);

    let query = {};
    let selectedFields = tripListFields;

    // Allow custom field selection if specified
    if (fields) {
      try {
        selectedFields = JSON.parse(fields);
      } catch (e) {
        return res.status(400).json({ error: "Invalid fields parameter" });
      }
    }

    if (trip_id) {
      query.trip_id = { $regex: trip_id, $options: "i" };
    }

    const trips = await Trip.find(query)
      .select(selectedFields)
      .skip((page - 1) * limit)
      .limit(limit)
      .lean();

    const totalTrips = await Trip.countDocuments(query);

    res.json({
      trips,
      pagination: {
        total: totalTrips,
        page,
        limit,
        totalPages: Math.ceil(totalTrips / limit)
      }
    });
  } catch (error) {
    console.error("Error fetching trips:", error);
    res.status(500).json({ error: "Server error" });
  }
});

// Get a specific trip by ID
router.get("/:id", async (req, res) => {
  try {
    const { fields } = req.query;
    let selectedFields = tripDetailFields;

    // Allow custom field selection if specified
    if (fields) {
      try {
        selectedFields = JSON.parse(fields);
      } catch (e) {
        return res.status(400).json({ error: "Invalid fields parameter" });
      }
    }

    const trip = await Trip.findOne({ trip_id: req.params.id }).select(selectedFields);
    if (!trip) return res.status(404).json({ message: "Trip not found" });
    res.json(trip);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Update a trip
router.put("/:id", async (req, res) => {
  try {
    // Only allow specific fields to be updated
    const allowedUpdates = {
      trip_short_name: req.body.trip_short_name,
      trip_long_name: req.body.trip_long_name,
      direction_id: req.body.direction_id,
      block_id: req.body.block_id,
      wheelchair_accessible: req.body.wheelchair_accessible,
      bikes_allowed: req.body.bikes_allowed,
      trip_status: req.body.trip_status,
      trip_schedule: req.body.trip_schedule,
      trip_features: req.body.trip_features,
      trip_analytics: req.body.trip_analytics,
      trip_alerts: req.body.trip_alerts,
      trip_predictions: req.body.trip_predictions,
      stops: req.body.stops
    };

    // Remove undefined fields
    Object.keys(allowedUpdates).forEach(key => 
      allowedUpdates[key] === undefined && delete allowedUpdates[key]
    );

    const updatedTrip = await Trip.findOneAndUpdate(
      { trip_id: req.params.id },
      { $set: allowedUpdates },
      { new: true }
    ).select(tripDetailFields);

    if (!updatedTrip) return res.status(404).json({ message: "Trip not found" });
    res.json(updatedTrip);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// Delete a trip
router.delete("/:id", async (req, res) => {
  try {
    const deletedTrip = await Trip.findOneAndDelete({ trip_id: req.params.id });
    if (!deletedTrip) return res.status(404).json({ message: "Trip not found" });
    res.json({ 
      message: "Trip deleted successfully",
      deletedTripId: deletedTrip.trip_id
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
