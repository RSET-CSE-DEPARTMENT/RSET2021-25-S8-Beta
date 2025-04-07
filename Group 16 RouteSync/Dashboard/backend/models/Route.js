const mongoose = require("mongoose");

const routeSchema = new mongoose.Schema({
  agency_id: { type: String, required: true },
  route_id: { type: String, required: true, unique: true },
  route_long_name: { type: String },
  route_short_name: { type: String },
  route_type: { type: Number, required: true },
  route_desc: { type: String, trim: true },
  route_url: { type: String, trim: true, match: /^https?:\/\// },
  route_color: { type: String, trim: true, match: /^#[0-9A-Fa-f]{6}$/ },
  route_text_color: { type: String, trim: true, match: /^#[0-9A-Fa-f]{6}$/ },
  route_sort_order: { type: Number, min: 0 },
  continuous_pickup: { 
    type: String, 
    enum: ['0', '1', '2', '3'],
    default: '1'
  },
  continuous_drop_off: { 
    type: String, 
    enum: ['0', '1', '2', '3'],
    default: '1'
  },
  route_status: {
    type: String,
    enum: ['active', 'inactive', 'temporary_closure', 'planned'],
    default: 'active'
  },
  route_metrics: {
    total_stops: { type: Number, default: 0 },
    total_trips: { type: Number, default: 0 },
    average_trip_duration: { type: Number, default: 0 }, // in minutes
    total_distance: { type: Number, default: 0 }, // in kilometers
    average_speed: { type: Number, default: 0 }, // in km/h
    last_updated: { type: Date, default: Date.now }
  },
  route_schedule: {
    first_trip: { type: String, match: /^([01]\d|2[0-3]):[0-5]\d$/ },
    last_trip: { type: String, match: /^([01]\d|2[0-3]):[0-5]\d$/ },
    frequency: {
      peak_hours: { type: Number, min: 0 }, // minutes between trips
      off_peak_hours: { type: Number, min: 0 }, // minutes between trips
      weekend: { type: Number, min: 0 } // minutes between trips
    },
    operating_days: [{
      type: String,
      enum: ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    }]
  },
  route_features: {
    is_express: { type: Boolean, default: false },
    is_rapid: { type: Boolean, default: false },
    is_accessible: { type: Boolean, default: false },
    has_wifi: { type: Boolean, default: false },
    has_air_conditioning: { type: Boolean, default: false },
    has_bike_rack: { type: Boolean, default: false }
  },
  route_metadata: {
    created_at: { type: Date, default: Date.now },
    last_modified: { type: Date, default: Date.now },
    last_trip_update: { type: Date },
    last_stop_update: { type: Date }
  },
  // Array of coordinates for rendering polyline
  coordinates: [
    {
      latitude: { type: Number, required: true },
      longitude: { type: Number, required: true },
      sequence: { type: Number, required: true },
      is_stop: { type: Boolean, default: false },
      stop_id: { type: String, ref: 'Stop' }
    }
  ],
  // Additional route information
  route_info: {
    start_stop: { type: String, ref: 'Stop' },
    end_stop: { type: String, ref: 'Stop' },
    major_stops: [{ type: String, ref: 'Stop' }],
    interchange_stations: [{ type: String, ref: 'Stop' }],
    fare_zones: [{ type: String }],
    estimated_travel_time: { type: Number, min: 0 }, // in minutes
    wheelchair_accessible: { type: Boolean, default: false },
    bike_accessible: { type: Boolean, default: false }
  }
}, {
  timestamps: true,
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// Virtual field to get the number of trips
routeSchema.virtual('tripCount', {
  ref: 'Trip',
  localField: 'route_id',
  foreignField: 'route_id',
  count: true
});

// Virtual field to get the number of stops
routeSchema.virtual('stopCount', {
  ref: 'Stop',
  localField: 'route_id',
  foreignField: 'route_id',
  count: true
});

// Indexes for better query performance
routeSchema.index({ agency_id: 1 });
routeSchema.index({ route_type: 1 });
routeSchema.index({ route_status: 1 });
routeSchema.index({ 'route_features.is_express': 1 });
routeSchema.index({ 'route_features.is_rapid': 1 });
routeSchema.index({ 'route_info.start_stop': 1 });
routeSchema.index({ 'route_info.end_stop': 1 });
routeSchema.index({ 'route_schedule.operating_days': 1 });

// Pre-save middleware to update metrics
routeSchema.pre('save', async function(next) {
  if (this.isModified('route_id')) {
    const Trip = mongoose.model('Trip');
    const Stop = mongoose.model('Stop');
    
    const [tripCount, stopCount] = await Promise.all([
      Trip.countDocuments({ route_id: this.route_id }),
      Stop.countDocuments({ route_id: this.route_id })
    ]);

    this.route_metrics = {
      ...this.route_metrics,
      total_trips: tripCount,
      total_stops: stopCount,
      last_updated: new Date()
    };
  }
  next();
});

// Method to calculate route distance
routeSchema.methods.calculateDistance = function() {
  let totalDistance = 0;
  for (let i = 0; i < this.coordinates.length - 1; i++) {
    const start = this.coordinates[i];
    const end = this.coordinates[i + 1];
    totalDistance += this.calculateHaversineDistance(
      start.latitude,
      start.longitude,
      end.latitude,
      end.longitude
    );
  }
  return totalDistance;
};

// Helper method to calculate Haversine distance
routeSchema.methods.calculateHaversineDistance = function(lat1, lon1, lat2, lon2) {
  const R = 6371; // Earth's radius in kilometers
  const dLat = this.toRad(lat2 - lat1);
  const dLon = this.toRad(lon2 - lon1);
  const a = 
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(this.toRad(lat1)) * Math.cos(this.toRad(lat2)) * 
    Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
};

routeSchema.methods.toRad = function(value) {
  return value * Math.PI / 180;
};

module.exports = mongoose.model("Route", routeSchema);
