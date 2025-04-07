const fs = require('fs');
const csv = require('csv-parser');
const mongoose = require('mongoose');

// Import the Trip model (adjust the path as needed)
const Trip = require('../models/Trip');

// Replace with your MongoDB connection string and database name
const mongoURI = 'mongodb+srv://elviinteldho:vjFrU6LslwMEW76B@routesync.nzpyk.mongodb.net/?retryWrites=true&w=majority&appName=RouteSync';

// Connect to MongoDB
mongoose
  .connect(mongoURI, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  })
  .then(() => console.log('Connected to MongoDB'))
  .catch((err) => {
    console.error('Failed to connect to MongoDB:', err);
    process.exit(1);
  });

// Array to store CSV rows
const trips = [];

// Read CSV data from the text file (assumed to be comma-separated)
fs.createReadStream('data/trips.txt')
  .pipe(csv())
  .on('data', (row) => {
    // Optionally, you can convert fields if needed.
    // For instance, if route_id is stored as a string in the CSV and should be an ObjectId:
    // row.route_id = mongoose.Types.ObjectId(row.route_id);
    trips.push(row);
  })
  .on('end', async () => {
    console.log(`CSV file successfully processed. Found ${trips.length} records.`);
    try {
      // Insert all records into the Trips collection
      await Trip.insertMany(trips);
      console.log('Data successfully inserted into MongoDB.');
    } catch (err) {
      console.error('Error inserting data:', err);
    } finally {
      // Close the MongoDB connection
      mongoose.connection.close();
    }
  })
  .on('error', (err) => {
    console.error('Error reading the file:', err);
  });
