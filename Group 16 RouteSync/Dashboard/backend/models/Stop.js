const mongoose = require("mongoose");

const stopSchema = new mongoose.Schema(
  {
    stop_code: { type: String, required: true, trim: true },
    stop_id: { type: String, required: true, unique: true, trim: true },
    stop_lat: { type: Number, required: true, min: -90, max: 90 },
    stop_lon: { type: Number, required: true, min: -180, max: 180 },
    stop_name: { type: String, required: true, trim: true },
    stop_desc: { type: String, trim: true },
    zone_id: { type: String, required: true, trim: true },
    stop_url: { type: String, trim: true, match: /^https?:\/\// },
    location_type: {
      type: String,
      enum: ['station', 'stop', 'entrance', 'exit', 'generic_node'],
      default: 'stop'
    },
    parent_station: { type: String, ref: 'Stop' },
    stop_timezone: { type: String, trim: true },
    wheelchair_boarding: {
      type: String,
      enum: ['0', '1', '2'],
      default: '0'
    },
    stop_status: {
      type: String,
      enum: ['active', 'inactive', 'temporary_closure', 'planned'],
      default: 'active'
    },
    stop_metrics: {
      total_routes: { type: Number, default: 0 },
      total_trips: { type: Number, default: 0 },
      average_daily_boardings: { type: Number, default: 0 },
      average_daily_alightings: { type: Number, default: 0 },
      last_updated: { type: Date, default: Date.now }
    },
    stop_features: {
      has_elevator: { type: Boolean, default: false },
      has_escalator: { type: Boolean, default: false },
      has_stairs: { type: Boolean, default: true },
      has_ramp: { type: Boolean, default: false },
      has_ticket_counter: { type: Boolean, default: false },
      has_restroom: { type: Boolean, default: false },
      has_parking: { type: Boolean, default: false },
      has_bike_rack: { type: Boolean, default: false },
      has_wifi: { type: Boolean, default: false },
      has_charging_station: { type: Boolean, default: false }
    },
    stop_amenities: {
      has_retail: { type: Boolean, default: false },
      has_food_court: { type: Boolean, default: false },
      has_atm: { type: Boolean, default: false },
      has_pharmacy: { type: Boolean, default: false },
      has_newsstand: { type: Boolean, default: false }
    },
    stop_metadata: {
      created_at: { type: Date, default: Date.now },
      last_modified: { type: Date, default: Date.now },
      last_route_update: { type: Date },
      last_trip_update: { type: Date }
    },
    stop_schedule: {
      first_arrival: { type: String, match: /^([01]\d|2[0-3]):[0-5]\d$/ },
      last_arrival: { type: String, match: /^([01]\d|2[0-3]):[0-5]\d$/ },
      operating_days: [{
        type: String,
        enum: ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
      }]
    },
    stop_connections: {
      nearby_stops: [{
        stop_id: { type: String, ref: 'Stop' },
        distance: { type: Number }, // in meters
        walking_time: { type: Number } // in minutes
      }],
      interchange_routes: [{
        route_id: { type: String, ref: 'Route' },
        direction: { type: String, enum: ['inbound', 'outbound', 'both'] }
      }]
    },
    stop_landmarks: [{
      name: { type: String, trim: true },
      type: { type: String, trim: true },
      distance: { type: Number }, // in meters
      direction: { type: String, trim: true }
    }],
    stop_geography: {
      elevation: { type: Number }, // in meters
      terrain_type: { type: String, enum: ['flat', 'hilly', 'underground', 'elevated'] },
      is_underground: { type: Boolean, default: false },
      is_elevated: { type: Boolean, default: false }
    }
  },
  {
    timestamps: true,
    toJSON: { virtuals: true },
    toObject: { virtuals: true }
  }
);

// Virtual field to get the number of routes
stopSchema.virtual('routeCount', {
  ref: 'Route',
  localField: 'stop_id',
  foreignField: 'route_info.major_stops',
  count: true
});

// Virtual field to get the number of trips
stopSchema.virtual('tripCount', {
  ref: 'Trip',
  localField: 'stop_id',
  foreignField: 'stops',
  count: true
});

// Indexes for better query performance
stopSchema.index({ stop_id: 1 });
stopSchema.index({ zone_id: 1 });
stopSchema.index({ location_type: 1 });
stopSchema.index({ stop_status: 1 });
stopSchema.index({ 'stop_features.has_elevator': 1 });
stopSchema.index({ 'stop_features.has_escalator': 1 });
stopSchema.index({ 'stop_features.has_parking': 1 });
stopSchema.index({ 'stop_geography.is_underground': 1 });
stopSchema.index({ 'stop_geography.is_elevated': 1 });
stopSchema.index({ stop_lat: 1, stop_lon: 1 }); // Geospatial index

// Pre-save middleware to update metrics
stopSchema.pre('save', async function(next) {
  if (this.isModified('stop_id')) {
    const Route = mongoose.model('Route');
    const Trip = mongoose.model('Trip');
    
    const [routeCount, tripCount] = await Promise.all([
      Route.countDocuments({ 'route_info.major_stops': this.stop_id }),
      Trip.countDocuments({ stops: this.stop_id })
    ]);

    this.stop_metrics = {
      ...this.stop_metrics,
      total_routes: routeCount,
      total_trips: tripCount,
      last_updated: new Date()
    };
  }
  next();
});

// Method to calculate distance to another stop
stopSchema.methods.calculateDistanceTo = function(otherStop) {
  const R = 6371; // Earth's radius in kilometers
  const dLat = this.toRad(otherStop.stop_lat - this.stop_lat);
  const dLon = this.toRad(otherStop.stop_lon - this.stop_lon);
  const a = 
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(this.toRad(this.stop_lat)) * Math.cos(this.toRad(otherStop.stop_lat)) * 
    Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c * 1000; // Convert to meters
};

stopSchema.methods.toRad = function(value) {
  return value * Math.PI / 180;
};

// Method to estimate walking time to another stop
stopSchema.methods.estimateWalkingTime = function(otherStop) {
  const distance = this.calculateDistanceTo(otherStop);
  // Assuming average walking speed of 5 km/h
  return Math.ceil((distance / 5000) * 60); // Convert to minutes
};

module.exports = mongoose.model("Stop", stopSchema);
