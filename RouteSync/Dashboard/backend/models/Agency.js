const mongoose = require("mongoose");

const agencySchema = new mongoose.Schema(
  {
    agency_id: { type: String, required: true, unique: true, trim: true },
    agency_name: { type: String, required: true, trim: true },
    agency_url: {
      type: String,
      required: true,
      trim: true,
      match: /^https?:\/\//,
    },
    agency_timezone: { type: String, required: true, trim: true },
    agency_lang: { type: String, required: true, trim: true },
    agency_phone: { type: String, trim: true },
    agency_fare_url: { type: String, trim: true, match: /^https?:\/\// },
    agency_email: { type: String, trim: true, match: /^[^\s@]+@[^\s@]+\.[^\s@]+$/ },
    agency_status: { 
      type: String, 
      enum: ['active', 'inactive', 'maintenance'],
      default: 'active'
    },
    agency_description: { type: String, trim: true },
    agency_operating_hours: {
      start: { type: String, match: /^([01]\d|2[0-3]):[0-5]\d$/ },
      end: { type: String, match: /^([01]\d|2[0-3]):[0-5]\d$/ }
    },
    agency_contact_person: {
      name: { type: String, trim: true },
      position: { type: String, trim: true },
      phone: { type: String, trim: true },
      email: { type: String, trim: true, match: /^[^\s@]+@[^\s@]+\.[^\s@]+$/ }
    },
    // New fields based on data analysis
    agency_route_types: [{
      type: Number,
      enum: [1, 2, 3, 4, 5, 6, 7, 11, 12], // Common transit route types
      required: true
    }],
    agency_operating_area: {
      type: {
        type: String,
        enum: ['Point', 'Polygon'],
        default: 'Polygon'
      },
      coordinates: [[[Number]]] // Array of [longitude, latitude] pairs for area boundary
    },
    agency_metrics: {
      total_stops: { type: Number, default: 0 },
      total_routes: { type: Number, default: 0 },
      total_trips: { type: Number, default: 0 },
      last_updated: { type: Date, default: Date.now }
    },
    agency_features: {
      has_rapid_transit: { type: Boolean, default: false },
      has_express_routes: { type: Boolean, default: false },
      has_airport_connectivity: { type: Boolean, default: false },
      has_intercity_connectivity: { type: Boolean, default: false }
    },
    agency_metadata: {
      established_date: { type: Date },
      last_route_update: { type: Date },
      last_stop_update: { type: Date },
      last_trip_update: { type: Date }
    }
  },
  { 
    timestamps: true,
    toJSON: { virtuals: true },
    toObject: { virtuals: true }
  }
);

// Virtual field to get the number of routes
agencySchema.virtual('routeCount', {
  ref: 'Route',
  localField: 'agency_id',
  foreignField: 'agency_id',
  count: true
});

// Virtual field to get the number of stops
agencySchema.virtual('stopCount', {
  ref: 'Stop',
  localField: 'agency_id',
  foreignField: 'agency_id',
  count: true
});

// Virtual field to get the number of trips
agencySchema.virtual('tripCount', {
  ref: 'Trip',
  localField: 'agency_id',
  foreignField: 'agency_id',
  count: true
});

// Indexes for better query performance
agencySchema.index({ agency_id: 1 });
agencySchema.index({ agency_status: 1 });
agencySchema.index({ 'agency_route_types': 1 });
agencySchema.index({ 'agency_features.has_rapid_transit': 1 });
agencySchema.index({ 'agency_features.has_airport_connectivity': 1 });

// Pre-save middleware to update metrics
agencySchema.pre('save', async function(next) {
  if (this.isModified('agency_id')) {
    // Update metrics when agency_id changes
    const Route = mongoose.model('Route');
    const Stop = mongoose.model('Stop');
    const Trip = mongoose.model('Trip');

    const [routeCount, stopCount, tripCount] = await Promise.all([
      Route.countDocuments({ agency_id: this.agency_id }),
      Stop.countDocuments({ agency_id: this.agency_id }),
      Trip.countDocuments({ agency_id: this.agency_id })
    ]);

    this.agency_metrics = {
      total_routes: routeCount,
      total_stops: stopCount,
      total_trips: tripCount,
      last_updated: new Date()
    };
  }
  next();
});

module.exports = mongoose.model("Agency", agencySchema);
