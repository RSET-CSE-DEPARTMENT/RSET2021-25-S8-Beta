const mongoose = require('mongoose');
const Route = require('../models/Route');

const MONGODB_URI = 'mongodb+srv://elviinteldho:vjFrU6LslwMEW76B@routesync.nzpyk.mongodb.net/?retryWrites=true&w=majority&appName=RouteSync';

async function updateAgencyId() {
  try {
    // Connect to MongoDB
    await mongoose.connect(MONGODB_URI);
    console.log('Connected to MongoDB');

    // Update all routes with agency_id as DMRC
    const result = await Route.updateMany(
      {}, // Match all documents
      { $set: { agency_id: 'DMRC' } },
      { multi: true }
    );

    console.log(`Migration completed successfully:`);
    console.log(`- Matched documents: ${result.matchedCount}`);
    console.log(`- Modified documents: ${result.modifiedCount}`);

    // Close the connection
    await mongoose.connection.close();
    console.log('Database connection closed');
  } catch (error) {
    console.error('Migration failed:', error);
    process.exit(1);
  }
}

// Run the migration
updateAgencyId(); 