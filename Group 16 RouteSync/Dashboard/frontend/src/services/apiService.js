

import axios from 'axios';
import GtfsRealtimeBindings from 'gtfs-realtime-bindings';  // Import GTFS bindings

// Function to fetch and parse GTFS-realtime data
const fetchRealTimeData = async () => {
  try {
    const response = await axios.get(
      'https://otd.delhi.gov.in/api/realtime/VehiclePositions.pb?key=aGHg9jZNFhNw6mSi9g75sULDp475UIXj',
      { responseType: 'arraybuffer' }
    );

    const buffer = response.data;
    const feed = GtfsRealtimeBindings.transit_realtime.FeedMessage.decode(new Uint8Array(buffer));

    // Iterate over each entity to log more information
    console.log(JSON.stringify(feed.entity, null, 2));

    // feed.entity.forEach((entity) => {
    //   if (entity.vehicle && entity.vehicle.position) {
    //     const vehicle = entity.vehicle;
    //     console.log(`Vehicle ID: ${vehicle.vehicle.id}`);
    //     console.log(`License Plate: ${vehicle.vehicle.label}`);
    //     console.log(`Position: (${vehicle.position.latitude}, ${vehicle.position.longitude})`);
    //     console.log(`Timestamp: ${vehicle.timestamp}`);
    //     console.log(`Speed: ${vehicle.position.speed || 'N/A'}`);
    //     console.log(`Bearing: ${vehicle.position.bearing || 'N/A'}`);
    //     console.log(`Trip IDs: ${vehicle.trip_id ? vehicle.trip.trip_id : 'N/A'}`);
    //     console.log("-----------------------------------");
    //   }
    // });

    return feed; // Return the full feed for use in your app

  } catch (error) {
    console.error('Error fetching or parsing real-time data:', error);
    throw error;
  }
};


export default fetchRealTimeData;
