const express = require("express");
const StopTime = require("../models/StopTimes");
const router = express.Router();

// Fields to include in different response types
const stopTimeListFields = {
  trip_id: 1,
  stop_id: 1,
  arrival_time: 1,
  departure_time: 1,
  stop_sequence: 1,
  stop_time_type: 1,
  pickup_type: 1,
  drop_off_type: 1,
  stop_metrics: {
    dwell_time: 1,
    headway_secs: 1,
    passenger_load: 1
  },
  stop_features: {
    is_accessible: 1,
    has_amenities: 1
  },
  stop_metadata: {
    created_at: 1,
    last_modified: 1,
    last_update: 1
  }
};

const stopTimeDetailFields = {
  ...stopTimeListFields,
  stop_metrics: 1,
  stop_schedule: 1,
  stop_features: 1,
  stop_metadata: 1,
  stop_analytics: 1,
  stop_alerts: 1,
  stop_predictions: 1,
  service_id: 1,
  service_exceptions: 1
};

const stopTimeMapFields = {
  trip_id: 1,
  stop_id: 1,
  arrival_time: 1,
  departure_time: 1,
  stop_sequence: 1,
  stop_metrics: {
    dwell_time: 1,
    passenger_load: 1
  },
  stop_features: {
    is_accessible: 1
  }
};

// Create a new stop time
router.post("/", async (req, res) => {
  try {
    // Only allow specific fields to be set during creation
    const allowedFields = {
      trip_id: req.body.trip_id,
      stop_id: req.body.stop_id,
      arrival_time: req.body.arrival_time,
      departure_time: req.body.departure_time,
      stop_sequence: req.body.stop_sequence,
      stop_time_type: req.body.stop_time_type,
      pickup_type: req.body.pickup_type,
      drop_off_type: req.body.drop_off_type,
      service_id: req.body.service_id
    };

    const stopTime = new StopTime(allowedFields);
    await stopTime.save();
    
    // Return only necessary fields
    const response = await StopTime.findById(stopTime._id).select(stopTimeListFields);
    res.status(201).json(response);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// Get stop time data for map display
router.get("/map-data", async (req, res) => {
  try {
    const stopTimes = await StopTime.find()
      .select(stopTimeMapFields)
      .lean();
    res.json(stopTimes);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Get all stop times with pagination and search
router.get("/", async (req, res) => {
  try {
    let { page = 1, limit = 50, trip_id, fields } = req.query;
    page = parseInt(page);
    limit = parseInt(limit);

    let query = {};
    let selectedFields = stopTimeListFields;

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

    const stopTimes = await StopTime.find(query)
      .select(selectedFields)
      .skip((page - 1) * limit)
      .limit(limit)
      .lean();

    const totalStopTimes = await StopTime.countDocuments(query);

    res.json({
      stopTimes,
      pagination: {
        total: totalStopTimes,
        page,
        limit,
        totalPages: Math.ceil(totalStopTimes / limit)
      }
    });
  } catch (error) {
    console.error("Error fetching stop times:", error);
    res.status(500).json({ error: "Server error" });
  }
});

// Get a specific stop time by ID
router.get("/:id", async (req, res) => {
  try {
    const { fields } = req.query;
    let selectedFields = stopTimeDetailFields;

    // Allow custom field selection if specified
    if (fields) {
      try {
        selectedFields = JSON.parse(fields);
      } catch (e) {
        return res.status(400).json({ error: "Invalid fields parameter" });
      }
    }

    const stopTime = await StopTime.findById(req.params.id).select(selectedFields);
    if (!stopTime) return res.status(404).json({ message: "Stop time not found" });
    res.json(stopTime);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Update a stop time
router.put("/:id", async (req, res) => {
  try {
    // Only allow specific fields to be updated
    const allowedUpdates = {
      arrival_time: req.body.arrival_time,
      departure_time: req.body.departure_time,
      stop_sequence: req.body.stop_sequence,
      stop_time_type: req.body.stop_time_type,
      pickup_type: req.body.pickup_type,
      drop_off_type: req.body.drop_off_type,
      stop_metrics: req.body.stop_metrics,
      stop_schedule: req.body.stop_schedule,
      stop_features: req.body.stop_features,
      stop_analytics: req.body.stop_analytics,
      stop_alerts: req.body.stop_alerts,
      stop_predictions: req.body.stop_predictions,
      service_exceptions: req.body.service_exceptions
    };

    // Remove undefined fields
    Object.keys(allowedUpdates).forEach(key => 
      allowedUpdates[key] === undefined && delete allowedUpdates[key]
    );

    const updatedStopTime = await StopTime.findByIdAndUpdate(
      req.params.id,
      { $set: allowedUpdates },
      { new: true }
    ).select(stopTimeDetailFields);

    if (!updatedStopTime) return res.status(404).json({ message: "Stop time not found" });
    res.json(updatedStopTime);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// Delete a stop time
router.delete("/:id", async (req, res) => {
  try {
    const deletedStopTime = await StopTime.findByIdAndDelete(req.params.id);
    if (!deletedStopTime) return res.status(404).json({ message: "Stop time not found" });
    res.json({ 
      message: "Stop time deleted successfully",
      deletedStopTimeId: deletedStopTime._id
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
