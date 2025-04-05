const mongoose = require("mongoose");

const stopTimesSchema = new mongoose.Schema(
  {
    trip_id: {
      type: String,
      required: true,
      ref: 'Trip'
    },
    arrival_time: {
      type: String,
      required: true,
      match: /^([01]\d|2[0-3]):[0-5]\d:[0-5]\d$/,
    }, // HH:MM:SS
    departure_time: {
      type: String,
      required: true,
      match: /^([01]\d|2[0-3]):[0-5]\d:[0-5]\d$/,
    },
    stop_id: {
      type: String,
      required: true,
      ref: 'Stop'
    },
    stop_sequence: { 
      type: Number, 
      required: true, 
      min: 0 
    },
    // Additional stop time information
    stop_time_type: {
      type: String,
      enum: ['scheduled', 'estimated', 'actual'],
      default: 'scheduled'
    },
    pickup_type: {
      type: String,
      enum: ['0', '1', '2', '3'],
      default: '0'
    },
    drop_off_type: {
      type: String,
      enum: ['0', '1', '2', '3'],
      default: '0'
    },
    shape_dist_traveled: {
      type: Number,
      min: 0
    },
    timepoint: {
      type: Boolean,
      default: true
    },
    // Stop time metrics
    stop_time_metrics: {
      dwell_time: { type: Number, min: 0 }, // in seconds
      headway_secs: { type: Number, min: 0 }, // time between consecutive trips
      passenger_load: { type: Number, min: 0 }, // estimated passenger count
      last_updated: { type: Date, default: Date.now }
    },
    // Stop time features
    stop_time_features: {
      is_timepoint: { type: Boolean, default: true },
      is_accessible: { type: Boolean, default: false },
      has_bike_rack: { type: Boolean, default: false },
      has_parking: { type: Boolean, default: false }
    },
    // Stop time metadata
    stop_time_metadata: {
      created_at: { type: Date, default: Date.now },
      last_modified: { type: Date, default: Date.now },
      last_update: { type: Date },
      update_source: { type: String, enum: ['manual', 'gtfs', 'realtime', 'api'] }
    },
    // Stop time schedule
    stop_time_schedule: {
      service_id: { type: String, ref: 'Calendar' },
      calendar_dates: [{ type: Date }],
      exceptions: [{
        date: { type: Date },
        type: { type: String, enum: ['added', 'removed'] }
      }]
    },
    // Stop time analytics
    stop_time_analytics: {
      average_dwell_time: { type: Number, min: 0 }, // in seconds
      average_passenger_load: { type: Number, min: 0 },
      reliability_score: { type: Number, min: 0, max: 100 }, // percentage
      on_time_performance: { type: Number, min: 0, max: 100 }, // percentage
      last_calculated: { type: Date, default: Date.now }
    },
    // Stop time alerts
    stop_time_alerts: [{
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
    // Stop time predictions
    stop_time_predictions: {
      predicted_arrival: { type: String, match: /^([01]\d|2[0-3]):[0-5]\d:[0-5]\d$/ },
      predicted_departure: { type: String, match: /^([01]\d|2[0-3]):[0-5]\d:[0-5]\d$/ },
      confidence_score: { type: Number, min: 0, max: 100 },
      last_prediction: { type: Date }
    }
  },
  {
    timestamps: true,
    toJSON: { virtuals: true },
    toObject: { virtuals: true }
  }
);

// Virtual field to get the route information
stopTimesSchema.virtual('route', {
  ref: 'Trip',
  localField: 'trip_id',
  foreignField: 'trip_id',
  justOne: true
});

// Virtual field to get the stop information
stopTimesSchema.virtual('stop', {
  ref: 'Stop',
  localField: 'stop_id',
  foreignField: 'stop_id',
  justOne: true
});

// Indexes for better query performance
stopTimesSchema.index({ trip_id: 1, stop_sequence: 1 });
stopTimesSchema.index({ stop_id: 1 });
stopTimesSchema.index({ arrival_time: 1 });
stopTimesSchema.index({ departure_time: 1 });
stopTimesSchema.index({ 'stop_time_type': 1 });
stopTimesSchema.index({ 'stop_time_metrics.dwell_time': 1 });
stopTimesSchema.index({ 'stop_time_alerts.is_active': 1 });
stopTimesSchema.index({ 'stop_time_schedule.service_id': 1 });

// Pre-save middleware to update metrics
stopTimesSchema.pre('save', async function(next) {
  if (this.isModified('arrival_time') || this.isModified('departure_time')) {
    // Calculate dwell time
    const arrival = this.parseTimeString(this.arrival_time);
    const departure = this.parseTimeString(this.departure_time);
    this.stop_time_metrics.dwell_time = (departure - arrival) / 1000; // Convert to seconds

    // Update last modified timestamp
    this.stop_time_metadata.last_modified = new Date();
  }
  next();
});

// Method to parse time string to milliseconds
stopTimesSchema.methods.parseTimeString = function(timeStr) {
  const [hours, minutes, seconds] = timeStr.split(':').map(Number);
  return (hours * 3600 + minutes * 60 + seconds) * 1000;
};

// Method to calculate headway
stopTimesSchema.methods.calculateHeadway = async function() {
  const StopTimes = mongoose.model('StopTimes');
  const previousStop = await StopTimes.findOne({
    stop_id: this.stop_id,
    departure_time: { $lt: this.arrival_time }
  }).sort({ departure_time: -1 });

  if (previousStop) {
    const currentArrival = this.parseTimeString(this.arrival_time);
    const previousDeparture = this.parseTimeString(previousStop.departure_time);
    return (currentArrival - previousDeparture) / 1000; // Convert to seconds
  }
  return null;
};

// Method to check if stop time is on time
stopTimesSchema.methods.isOnTime = function() {
  const scheduledArrival = this.parseTimeString(this.arrival_time);
  const actualArrival = this.parseTimeString(this.stop_time_predictions.predicted_arrival);
  const timeDiff = Math.abs(actualArrival - scheduledArrival) / 1000; // Convert to seconds
  return timeDiff <= 300; // Within 5 minutes
};

module.exports = mongoose.model("StopTimes", stopTimesSchema);
