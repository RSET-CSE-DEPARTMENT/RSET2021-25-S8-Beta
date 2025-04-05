const express = require("express");
const fs = require("fs");
const path = require("path");
const csv = require("csv-parser");
const Route = require("../models/Route");
const Trip = require("../models/Trip");
const router = express.Router();

// Fields to include in different response types
const routeListFields = {
  route_id: 1,
  route_short_name: 1,
  route_long_name: 1,
  route_desc: 1,
  route_type: 1,
  route_url: 1,
  route_color: 1,
  route_text_color: 1,
  route_status: 1,
  route_metrics: {
    total_stops: 1,
    total_trips: 1,
    average_trip_duration: 1
  },
  route_features: {
    is_express: 1,
    is_rapid: 1,
    is_accessible: 1
  },
  route_metadata: {
    created_at: 1,
    last_modified: 1,
    last_trip_update: 1
  }
};

const routeDetailFields = {
  ...routeListFields,
  route_metrics: 1,
  route_schedule: 1,
  route_features: 1,
  route_metadata: 1,
  route_info: 1,
  coordinates: 1
};

const routeMapFields = {
  route_id: 1,
  route_short_name: 1,
  route_long_name: 1,
  route_type: 1,
  route_color: 1,
  route_text_color: 1,
  coordinates: 1,
  route_status: 1
};

// Create a new route
router.post("/", async (req, res) => {
  try {
    // Only allow specific fields to be set during creation
    const allowedFields = {
      route_id: req.body.route_id,
      route_short_name: req.body.route_short_name,
      route_long_name: req.body.route_long_name,
      route_desc: req.body.route_desc,
      route_type: req.body.route_type,
      route_url: req.body.route_url,
      route_color: req.body.route_color,
      route_text_color: req.body.route_text_color
    };

    const route = new Route(allowedFields);
    await route.save();
    
    // Return only necessary fields
    const response = await Route.findById(route._id).select(routeListFields);
    res.status(201).json(response);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// Get all routes for map display
router.get("/map-data", async (req, res) => {
  try {
    const routes = await Route.find().select(routeMapFields).lean();
    res.json(routes);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Function to read and parse shapes.txt
const parseShapesFile = async () => {
  return new Promise((resolve, reject) => {
    console.log("[LOG] Parsing shapes.txt file...");

    const shapes = {};

    fs.createReadStream(path.join(__dirname, "../data/shapes.txt"))
      .pipe(csv())
      .on("data", (row) => {
        const { shape_id, shape_pt_lat, shape_pt_lon, shape_pt_sequence } = row;

        if (!shapes[shape_id]) {
          shapes[shape_id] = [];
        }

        shapes[shape_id].push({
          latitude: parseFloat(shape_pt_lat),
          longitude: parseFloat(shape_pt_lon),
          sequence: parseInt(shape_pt_sequence),
        });
      })
      .on("end", () => {
        // Sort coordinates by sequence
        Object.keys(shapes).forEach((shape_id) => {
          shapes[shape_id].sort((a, b) => a.sequence - b.sequence);
        });

        console.log(
          `[LOG] Parsed ${Object.keys(shapes).length} shape IDs from shapes.txt`
        );
        resolve(shapes);
      })
      .on("error", (error) => {
        console.error("[ERROR] Failed to parse shapes.txt:", error);
        reject(error);
      });
  });
};

// API to set polyline coordinates for each route
router.post("/set-polyline", async (req, res) => {
  try {
    console.log("[LOG] Fetching first trips for each route...");

    // Step 1: Get the first trip for each route
    const trips = await Trip.aggregate([
      { $sort: { _id: 1 } },
      {
        $group: {
          _id: "$route_id",
          firstTrip: { $first: "$$ROOT" },
        },
      },
    ]).project({
      _id: 1,
      firstTrip: {
        shape_id: 1
      }
    });

    console.log(`[LOG] Found ${trips.length} unique routes with trips.`);

    // Step 2: Map route_id → shape_id
    const routeToShapeMap = {};
    trips.forEach(({ _id, firstTrip }) => {
      if (firstTrip.shape_id) {
        routeToShapeMap[_id] = firstTrip.shape_id;
      } else {
        console.warn(`[WARN] Route ID ${_id} has no associated shape_id!`);
      }
    });

    console.log(
      `[LOG] Mapped ${Object.keys(routeToShapeMap).length} routes to shape IDs.`
    );

    // Step 3: Read and parse shapes.txt
    const shapeCoordinates = await parseShapesFile();

    console.log("[LOG] Updating routes with polyline coordinates...");

    // Step 4: Update each Route with the polyline coordinates
    const updates = [];
    for (const [routeId, shapeId] of Object.entries(routeToShapeMap)) {
      const coordinates =
        shapeCoordinates[shapeId]?.map(({ latitude, longitude }) => ({
          latitude,
          longitude,
        })) || [];

      if (coordinates.length === 0) {
        console.warn(
          `[WARN] No coordinates found for shape_id: ${shapeId} (Route ID: ${routeId})`
        );
      } else {
        console.log(
          `[LOG] Route ID ${routeId}: Updating with ${coordinates.length} coordinates.`
        );
      }

      updates.push(
        Route.findOneAndUpdate(
          { route_id: routeId },
          { coordinates },
          { new: true }
        ).select(routeMapFields)
      );
    }

    // Execute all updates
    const updatedRoutes = await Promise.all(updates);
    console.log(`[LOG] Successfully updated ${updatedRoutes.length} routes.`);

    res.json({
      message: "Polyline coordinates updated successfully",
      updatedRoutes,
    });
  } catch (error) {
    console.error("[ERROR] Error setting polyline:", error);
    res.status(500).json({ error: "Server error" });
  }
});

// Get all routes with pagination and search
router.get("/", async (req, res) => {
  try {
    let { page = 1, limit = 50, route_id, fields } = req.query;
    page = parseInt(page);
    limit = parseInt(limit);

    let query = {};
    let selectedFields = routeListFields;

    // Allow custom field selection if specified
    if (fields) {
      try {
        selectedFields = JSON.parse(fields);
      } catch (e) {
        return res.status(400).json({ error: "Invalid fields parameter" });
      }
    }

    if (route_id) {
      query.route_id = { $regex: route_id, $options: "i" };
    }

    const routes = await Route.find(query)
      .select(selectedFields)
      .skip((page - 1) * limit)
      .limit(limit)
      .lean();

    const totalRoutes = await Route.countDocuments(query);

    res.json({
      routes,
      pagination: {
        total: totalRoutes,
        page,
        limit,
        totalPages: Math.ceil(totalRoutes / limit)
      }
    });
  } catch (error) {
    console.error("Error fetching routes:", error);
    res.status(500).json({ error: "Server error" });
  }
});

// Get a specific route by ID
router.get("/specific/:id", async (req, res) => {
  try {
    const { fields } = req.query;
    let selectedFields = routeDetailFields;

    // Allow custom field selection if specified
    if (fields) {
      try {
        selectedFields = JSON.parse(fields);
      } catch (e) {
        return res.status(400).json({ error: "Invalid fields parameter" });
      }
    }

    const route = await Route.findOne({ route_id: req.params.id }).select(selectedFields);
    if (!route) return res.status(404).json({ message: "Route not found" });
    res.json(route);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Update a route
router.put("/:id", async (req, res) => {
  try {
    // Only allow specific fields to be updated
    const allowedUpdates = {
      route_short_name: req.body.route_short_name,
      route_long_name: req.body.route_long_name,
      route_desc: req.body.route_desc,
      route_type: req.body.route_type,
      route_url: req.body.route_url,
      route_color: req.body.route_color,
      route_text_color: req.body.route_text_color,
      route_status: req.body.route_status,
      route_schedule: req.body.route_schedule,
      route_features: req.body.route_features,
      route_info: req.body.route_info
    };

    // Remove undefined fields
    Object.keys(allowedUpdates).forEach(key => 
      allowedUpdates[key] === undefined && delete allowedUpdates[key]
    );

    const updatedRoute = await Route.findByIdAndUpdate(
      req.params.id,
      { $set: allowedUpdates },
      { new: true }
    ).select(routeDetailFields);

    if (!updatedRoute) return res.status(404).json({ message: "Route not found" });
    res.json(updatedRoute);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// Delete a route
router.delete("/:id", async (req, res) => {
  try {
    const deletedRoute = await Route.findByIdAndDelete(req.params.id);
    if (!deletedRoute) return res.status(404).json({ message: "Route not found" });
    res.json({ 
      message: "Route deleted successfully",
      deletedRouteId: deletedRoute._id
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
