const mongoose = require("mongoose");

const tripSchema = new mongoose.Schema(
  {
    route_id: {
      type: String,
      required: true,
      ref: 'Route'
    },
    service_id: { 
      type: String, 
      required: true, 
      trim: true,
      ref: 'Calendar'
    },
    trip_id: { 
      type: String, 
      required: true, 
      unique: true, 
      trim: true 
    },
    trip_short_name: { type: String, trim: true },
    trip_long_name: { type: String, trim: true },
    direction_id: { 
      type: String, 
      enum: ['0', '1'],
      required: true 
    },
    block_id: { type: String, trim: true },
    shape_id: { type: String, trim: true },
    wheelchair_accessible: { 
      type: String, 
      enum: ['0', '1', '2'],
      default: '0'
    },
    bikes_allowed: { 
      type: String, 
      enum: ['0', '1', '2'],
      default: '0'
    },
    trip_status: {
      type: String,
      enum: ['scheduled', 'active', 'completed', 'cancelled', 'delayed'],
      default: 'scheduled'
    },
    // Trip metrics
    trip_metrics: {
      total_stops: { type: Number, default: 0 },
      total_distance: { type: Number, default: 0 }, // in kilometers
      total_duration: { type: Number, default: 0 }, // in minutes
      average_speed: { type: Number, default: 0 }, // in km/h
      passenger_capacity: { type: Number, default: 0 },
      last_updated: { type: Date, default: Date.now }
    },
    // Trip schedule
    trip_schedule: {
      start_time: { type: String, match: /^([01]\d|2[0-3]):[0-5]\d:[0-5]\d$/ },
      end_time: { type: String, match: /^([01]\d|2[0-3]):[0-5]\d:[0-5]\d$/ },
      frequency: { type: Number, min: 0 }, // minutes between trips
      operating_days: [{
        type: String,
        enum: ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
      }]
    },
    // Trip features
    trip_features: {
      is_express: { type: Boolean, default: false },
      is_rapid: { type: Boolean, default: false },
      is_accessible: { type: Boolean, default: false },
      has_wifi: { type: Boolean, default: false },
      has_air_conditioning: { type: Boolean, default: false },
      has_bike_rack: { type: Boolean, default: false }
    },
    // Trip metadata
    trip_metadata: {
      created_at: { type: Date, default: Date.now },
      last_modified: { type: Date, default: Date.now },
      last_update: { type: Date },
      update_source: { type: String, enum: ['manual', 'gtfs', 'realtime', 'api'] }
    },
    // Trip analytics
    trip_analytics: {
      average_passenger_load: { type: Number, min: 0 },
      reliability_score: { type: Number, min: 0, max: 100 }, // percentage
      on_time_performance: { type: Number, min: 0, max: 100 }, // percentage
      last_calculated: { type: Date, default: Date.now }
    },
    // Trip alerts
    trip_alerts: [{
      type: { 
        type: String, 
        enum: ['delay', 'cancellation', 'detour', 'crowding', 'maintenance', 'weather']
      },
      severity: { 
        type: String, 
        enum: ['low', 'medium', 'high', 'critical']
      },
      message: { type: String },
      start_time: { type: Date },
      end_time: { type: Date },
      is_active: { type: Boolean, default: true }
    }],
    // Trip predictions
    trip_predictions: {
      predicted_start: { type: String, match: /^([01]\d|2[0-3]):[0-5]\d:[0-5]\d$/ },
      predicted_end: { type: String, match: /^([01]\d|2[0-3]):[0-5]\d:[0-5]\d$/ },
      confidence_score: { type: Number, min: 0, max: 100 },
      last_prediction: { type: Date }
    },
    // Trip stops
    stops: [{
      stop_id: { type: String, ref: 'Stop' },
      sequence: { type: Number, required: true },
      arrival_time: { type: String, match: /^([01]\d|2[0-3]):[0-5]\d:[0-5]\d$/ },
      departure_time: { type: String, match: /^([01]\d|2[0-3]):[0-5]\d:[0-5]\d$/ }
    }]
  },
  {
    timestamps: true,
    toJSON: { virtuals: true },
    toObject: { virtuals: true }
  }
);

// Virtual field to get the route information
tripSchema.virtual('route', {
  ref: 'Route',
  localField: 'route_id',
  foreignField: 'route_id',
  justOne: true
});

// Virtual field to get the service information
tripSchema.virtual('service', {
  ref: 'Calendar',
  localField: 'service_id',
  foreignField: 'service_id',
  justOne: true
});

// Virtual field to get the stop times
tripSchema.virtual('stopTimes', {
  ref: 'StopTimes',
  localField: 'trip_id',
  foreignField: 'trip_id'
});

// Indexes for better query performance
tripSchema.index({ trip_id: 1 });
tripSchema.index({ route_id: 1 });
tripSchema.index({ service_id: 1 });
tripSchema.index({ direction_id: 1 });
tripSchema.index({ trip_status: 1 });
tripSchema.index({ 'trip_features.is_express': 1 });
tripSchema.index({ 'trip_features.is_rapid': 1 });
tripSchema.index({ 'trip_schedule.start_time': 1 });
tripSchema.index({ 'trip_schedule.end_time': 1 });
tripSchema.index({ 'trip_alerts.is_active': 1 });

// Pre-save middleware to update metrics
tripSchema.pre('save', async function(next) {
  if (this.isModified('stops')) {
    // Calculate total stops
    this.trip_metrics.total_stops = this.stops.length;

    // Calculate total duration if we have start and end times
    if (this.stops.length > 0) {
      const firstStop = this.stops[0];
      const lastStop = this.stops[this.stops.length - 1];
      const startTime = this.parseTimeString(firstStop.departure_time);
      const endTime = this.parseTimeString(lastStop.arrival_time);
      this.trip_metrics.total_duration = (endTime - startTime) / (1000 * 60); // Convert to minutes
    }

    // Update last modified timestamp
    this.trip_metadata.last_modified = new Date();
  }
  next();
});

// Method to parse time string to milliseconds
tripSchema.methods.parseTimeString = function(timeStr) {
  const [hours, minutes, seconds] = timeStr.split(':').map(Number);
  return (hours * 3600 + minutes * 60 + seconds) * 1000;
};

// Method to check if trip is on time
tripSchema.methods.isOnTime = function() {
  if (!this.trip_predictions.predicted_start) return true;
  
  const scheduledStart = this.parseTimeString(this.trip_schedule.start_time);
  const predictedStart = this.parseTimeString(this.trip_predictions.predicted_start);
  const timeDiff = Math.abs(predictedStart - scheduledStart) / 1000; // Convert to seconds
  return timeDiff <= 300; // Within 5 minutes
};

// Method to get next stop
tripSchema.methods.getNextStop = function() {
  const now = new Date();
  const currentTime = now.getHours() * 3600 + now.getMinutes() * 60 + now.getSeconds();
  
  return this.stops.find(stop => {
    const stopTime = this.parseTimeString(stop.arrival_time) / 1000;
    return stopTime > currentTime;
  });
};

// Method to get previous stop
tripSchema.methods.getPreviousStop = function() {
  const now = new Date();
  const currentTime = now.getHours() * 3600 + now.getMinutes() * 60 + now.getSeconds();
  
  return this.stops.reverse().find(stop => {
    const stopTime = this.parseTimeString(stop.departure_time) / 1000;
    return stopTime < currentTime;
  });
};

module.exports = mongoose.model("Trip", tripSchema);
