const express = require("express");
const Stop = require("../models/Stop");
const router = express.Router();

// Fields to include in different response types
const stopListFields = {
  stop_id: 1,
  stop_name: 1,
  stop_desc: 1,
  stop_lat: 1,
  stop_lon: 1,
  location_type: 1,
  stop_timezone: 1,
  wheelchair_boarding: 1,
  stop_status: 1,
  stop_metrics: {
    total_routes: 1,
    total_trips: 1,
    average_daily_boardings: 1
  },
  stop_features: {
    has_elevator: 1,
    has_escalator: 1,
    has_stairs: 1,
    has_ramp: 1
  },
  stop_metadata: {
    created_at: 1,
    last_modified: 1,
    last_route_update: 1
  }
};

const stopDetailFields = {
  ...stopListFields,
  stop_metrics: 1,
  stop_features: 1,
  stop_amenities: 1,
  stop_metadata: 1,
  stop_schedule: 1,
  stop_connections: 1,
  stop_landmarks: 1,
  stop_geography: 1
};

const stopMapFields = {
  stop_id: 1,
  stop_name: 1,
  stop_lat: 1,
  stop_lon: 1,
  location_type: 1,
  wheelchair_boarding: 1,
  stop_status: 1,
  stop_features: {
    has_elevator: 1,
    has_escalator: 1,
    has_stairs: 1,
    has_ramp: 1
  }
};

// Create a new stop
router.post("/", async (req, res) => {
  try {
    // Only allow specific fields to be set during creation
    const allowedFields = {
      stop_id: req.body.stop_id,
      stop_name: req.body.stop_name,
      stop_desc: req.body.stop_desc,
      stop_lat: req.body.stop_lat,
      stop_lon: req.body.stop_lon,
      location_type: req.body.location_type,
      stop_timezone: req.body.stop_timezone,
      wheelchair_boarding: req.body.wheelchair_boarding
    };

    const stop = new Stop(allowedFields);
    await stop.save();
    
    // Return only necessary fields
    const response = await Stop.findById(stop._id).select(stopListFields);
    res.status(201).json(response);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// Get all stops with pagination and search
router.get("/", async (req, res) => {
  try {
    let { page = 1, limit = 50, stop_name, fields } = req.query;
    page = parseInt(page);
    limit = parseInt(limit);

    let query = {};
    let selectedFields = stopListFields;

    // Allow custom field selection if specified
    if (fields) {
      try {
        selectedFields = JSON.parse(fields);
      } catch (e) {
        return res.status(400).json({ error: "Invalid fields parameter" });
      }
    }

    if (stop_name) {
      query.stop_name = { $regex: stop_name, $options: "i" };
    }

    const stops = await Stop.find(query)
      .select(selectedFields)
      .skip((page - 1) * limit)
      .limit(limit)
      .lean();

    const totalStops = await Stop.countDocuments(query);

    res.json({
      stops,
      pagination: {
        total: totalStops,
        page,
        limit,
        totalPages: Math.ceil(totalStops / limit)
      }
    });
  } catch (error) {
    console.error("Error fetching stops:", error);
    res.status(500).json({ error: "Server error" });
  }
});

// Get minimal stop data for rendering markers
router.get("/map-data", async (req, res) => {
  try {
    const stops = await Stop.find()
      .select(stopMapFields)
      .lean();
    res.json(stops);
  } catch (error) {
    console.error("Error fetching stop map data:", error);
    res.status(500).json({ error: "Server error" });
  }
});

// Get a specific stop by ID
router.get("/:id", async (req, res) => {
  try {
    const { fields } = req.query;
    let selectedFields = stopDetailFields;

    // Allow custom field selection if specified
    if (fields) {
      try {
        selectedFields = JSON.parse(fields);
      } catch (e) {
        return res.status(400).json({ error: "Invalid fields parameter" });
      }
    }

    const stop = await Stop.findById(req.params.id).select(selectedFields);
    if (!stop) return res.status(404).json({ message: "Stop not found" });
    res.json(stop);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Update a stop
router.put("/:id", async (req, res) => {
  try {
    // Only allow specific fields to be updated
    const allowedUpdates = {
      stop_name: req.body.stop_name,
      stop_desc: req.body.stop_desc,
      stop_lat: req.body.stop_lat,
      stop_lon: req.body.stop_lon,
      location_type: req.body.location_type,
      stop_timezone: req.body.stop_timezone,
      wheelchair_boarding: req.body.wheelchair_boarding,
      stop_status: req.body.stop_status,
      stop_features: req.body.stop_features,
      stop_amenities: req.body.stop_amenities,
      stop_schedule: req.body.stop_schedule,
      stop_connections: req.body.stop_connections,
      stop_landmarks: req.body.stop_landmarks,
      stop_geography: req.body.stop_geography
    };

    // Remove undefined fields
    Object.keys(allowedUpdates).forEach(key => 
      allowedUpdates[key] === undefined && delete allowedUpdates[key]
    );

    const updatedStop = await Stop.findByIdAndUpdate(
      req.params.id,
      { $set: allowedUpdates },
      { new: true }
    ).select(stopDetailFields);

    if (!updatedStop) return res.status(404).json({ message: "Stop not found" });
    res.json(updatedStop);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// Delete a stop
router.delete("/:id", async (req, res) => {
  try {
    const deletedStop = await Stop.findByIdAndDelete(req.params.id);
    if (!deletedStop) return res.status(404).json({ message: "Stop not found" });
    res.json({ 
      message: "Stop deleted successfully",
      deletedStopId: deletedStop._id
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
