const express = require("express");
const Agency = require("../models/Agency");
const router = express.Router();

// Fields to include in different response types
const agencyListFields = {
  agency_id: 1,
  agency_name: 1,
  agency_url: 1,
  agency_timezone: 1,
  agency_lang: 1,
  agency_phone: 1,
  agency_route_types: 1,
  agency_metrics: {
    total_stops: 1,
    total_routes: 1,
    total_trips: 1
  },
  agency_features: {
    has_rapid_transit: 1,
    has_express_routes: 1,
    has_airport_connectivity: 1,
    has_intercity_connectivity: 1
  },
  agency_metadata: {
    established_date: 1,
    last_route_update: 1,
    last_stop_update: 1,
    last_trip_update: 1
  }
};

const agencyDetailFields = {
  ...agencyListFields,
  agency_operating_area: 1,
  agency_metrics: 1,
  agency_features: 1,
  agency_metadata: 1
};

// Create a new agency
router.post("/", async (req, res) => {
  try {
    // Only allow specific fields to be set during creation
    const allowedFields = {
      agency_id: req.body.agency_id,
      agency_name: req.body.agency_name,
      agency_url: req.body.agency_url,
      agency_timezone: req.body.agency_timezone,
      agency_lang: req.body.agency_lang,
      agency_phone: req.body.agency_phone
    };

    const agency = new Agency(allowedFields);
    await agency.save();
    
    // Return only necessary fields
    const response = await Agency.findById(agency._id).select(agencyListFields);
    res.status(201).json(response);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// Get all agencies with pagination and search
router.get("/", async (req, res) => {
  try {
    let { page = 1, limit = 50, agency_name, fields } = req.query;
    page = parseInt(page);
    limit = parseInt(limit);

    let query = {};
    let selectedFields = agencyListFields;

    // Allow custom field selection if specified
    if (fields) {
      try {
        selectedFields = JSON.parse(fields);
      } catch (e) {
        return res.status(400).json({ error: "Invalid fields parameter" });
      }
    }

    if (agency_name) {
      query.agency_name = { $regex: agency_name, $options: "i" };
    }

    const agencies = await Agency.find(query)
      .select(selectedFields)
      .skip((page - 1) * limit)
      .limit(limit)
      .lean();

    const totalAgencies = await Agency.countDocuments(query);

    res.json({
      agencies,
      pagination: {
        total: totalAgencies,
        page,
        limit,
        totalPages: Math.ceil(totalAgencies / limit)
      }
    });
  } catch (error) {
    console.error("Error fetching agencies:", error);
    res.status(500).json({ error: "Server error" });
  }
});

// Get a specific agency by ID
router.get("/:id", async (req, res) => {
  try {
    const { fields } = req.query;
    let selectedFields = agencyDetailFields;

    // Allow custom field selection if specified
    if (fields) {
      try {
        selectedFields = JSON.parse(fields);
      } catch (e) {
        return res.status(400).json({ error: "Invalid fields parameter" });
      }
    }

    const agency = await Agency.findById(req.params.id).select(selectedFields);
    if (!agency) return res.status(404).json({ message: "Agency not found" });
    res.json(agency);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Update an agency
router.put("/:id", async (req, res) => {
  try {
    // Only allow specific fields to be updated
    const allowedUpdates = {
      agency_name: req.body.agency_name,
      agency_url: req.body.agency_url,
      agency_timezone: req.body.agency_timezone,
      agency_lang: req.body.agency_lang,
      agency_phone: req.body.agency_phone,
      agency_route_types: req.body.agency_route_types,
      agency_operating_area: req.body.agency_operating_area,
      agency_features: req.body.agency_features
    };

    // Remove undefined fields
    Object.keys(allowedUpdates).forEach(key => 
      allowedUpdates[key] === undefined && delete allowedUpdates[key]
    );

    const updatedAgency = await Agency.findByIdAndUpdate(
      req.params.id,
      { $set: allowedUpdates },
      { new: true }
    ).select(agencyDetailFields);

    if (!updatedAgency) return res.status(404).json({ message: "Agency not found" });
    res.json(updatedAgency);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// Delete an agency
router.delete("/:id", async (req, res) => {
  try {
    const deletedAgency = await Agency.findByIdAndDelete(req.params.id);
    if (!deletedAgency) return res.status(404).json({ message: "Agency not found" });
    res.json({ 
      message: "Agency deleted successfully",
      deletedAgencyId: deletedAgency._id
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;