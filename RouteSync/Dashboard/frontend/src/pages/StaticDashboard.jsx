import React, { useEffect, useRef, useState } from "react";
import "leaflet/dist/leaflet.css";
import axios from "axios";
import {
  Box,
  CircularProgress,
  Paper,
  Typography,
  IconButton,
  Tooltip,
  FormControlLabel,
  Switch,
  Stack,
  Chip,
} from "@mui/material";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  useMap,
  useMapEvent,
  Polyline,
  ZoomControl,
  LayersControl,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { Icon } from "leaflet";
import MarkerClusterGroup from "react-leaflet-cluster";
import {
  LocationOn,
  DirectionsBus,
  Refresh,
} from "@mui/icons-material";

const BusStopMarkers = ({ stopsData, busStopIcon, showStops }) => {
  const [visibleStops, setVisibleStops] = useState([]);
  const map = useMap();

  useMapEvent("moveend", () => {
    const bounds = map.getBounds();
    const filteredStops = stopsData.filter(
      (stop) => bounds.contains([stop.stop_lat, stop.stop_lon])
    );
    setVisibleStops(filteredStops);
  });

  useEffect(() => {
    const bounds = map.getBounds();
    const filteredStops = stopsData.filter(
      (stop) => bounds.contains([stop.stop_lat, stop.stop_lon])
    );
    setVisibleStops(filteredStops);
  }, [stopsData, map]);

  if (!showStops) return null;

  return (
    <MarkerClusterGroup chunkedLoading>
      {visibleStops.map((stop, index) => (
        <Marker
          icon={busStopIcon}
          key={stop.stop_code || `stop-${index}`}
          position={[stop.stop_lat, stop.stop_lon]}
        >
          <Popup>
            <Box sx={{ p: 1.5, minWidth: 300 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <LocationOn color="primary" />
                <Typography variant="h6" component="div" fontWeight="bold">
                  {stop.stop_name}
                </Typography>
              </Box>
              <Box sx={{ display: 'grid', gap: 0.75 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="text.secondary">
                    Stop Code
                  </Typography>
                  <Typography variant="body2" fontWeight="medium">
                    {stop.stop_code || "N/A"}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="text.secondary">
                    Zone ID
                  </Typography>
                  <Typography variant="body2" fontWeight="medium">
                    {stop.zone_id || "N/A"}
                  </Typography>
                </Box>
                {stop.stop_desc && (
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="text.secondary">
                      Description
                    </Typography>
                    <Typography variant="body2" fontWeight="medium">
                      {stop.stop_desc}
                    </Typography>
                  </Box>
                )}
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="text.secondary">
                    Location Type
                  </Typography>
                  <Typography variant="body2" fontWeight="medium">
                    {stop.location_type || "stop"}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="text.secondary">
                    Status
                  </Typography>
                  <Typography 
                    variant="body2" 
                    fontWeight="medium"
                    sx={{ 
                      color: stop.stop_status === 'active' ? 'success.main' : 
                             stop.stop_status === 'inactive' ? 'error.main' :
                             stop.stop_status === 'temporary_closure' ? 'warning.main' : 'text.secondary'
                    }}
                  >
                    {stop.stop_status || "active"}
                  </Typography>
                </Box>
                {stop.stop_metrics && (
                  <>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2" color="text.secondary">
                        Total Routes
                      </Typography>
                      <Typography variant="body2" fontWeight="medium">
                        {stop.stop_metrics.total_routes || 0}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2" color="text.secondary">
                        Total Trips
                      </Typography>
                      <Typography variant="body2" fontWeight="medium">
                        {stop.stop_metrics.total_trips || 0}
                      </Typography>
                    </Box>
                  </>
                )}
                {stop.stop_features && (
                  <Box sx={{ mt: 0.5 }}>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 0.25 }}>
                      Features
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.25 }}>
                      {stop.stop_features.has_elevator && <Chip size="small" label="Elevator" />}
                      {stop.stop_features.has_escalator && <Chip size="small" label="Escalator" />}
                      {stop.stop_features.has_ramp && <Chip size="small" label="Ramp" />}
                      {stop.stop_features.has_parking && <Chip size="small" label="Parking" />}
                      {stop.stop_features.has_wifi && <Chip size="small" label="WiFi" />}
                    </Box>
                  </Box>
                )}
              </Box>
            </Box>
          </Popup>
        </Marker>
      ))}
    </MarkerClusterGroup>
  );
};

const MapControls = ({ onRefresh, showStops, onToggleStops }) => {
  return (
    <Box
      sx={{
        position: "absolute",
        top: 16,
        right: 16,
        zIndex: 1000,
        display: "flex",
        flexDirection: "column",
        gap: 1,
      }}
    >
      <Paper elevation={3} sx={{ p: 1 }}>
        <Stack spacing={1}>
          <Tooltip title="Toggle Stops">
            <FormControlLabel
              control={
                <Switch
                  checked={showStops}
                  onChange={onToggleStops}
                  color="primary"
                />
              }
              label={<LocationOn />}
            />
          </Tooltip>
          <Tooltip title="Refresh Data">
            <IconButton onClick={onRefresh} color="primary">
              <Refresh />
            </IconButton>
          </Tooltip>
        </Stack>
      </Paper>
    </Box>
  );
};

const StaticDashboard = () => {
  const [stops, setStops] = useState([]);
  const [routes, setRoutes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showStops, setShowStops] = useState(true);
  const mapRef = useRef(null);

  const busStopIcon = new Icon({
    iconUrl: "/src/img/bus-stop.png",
    iconSize: [38, 38],
  });

    const fetchData = async () => {
    setLoading(true);
      try {
        const [stopsRes, routesRes] = await Promise.all([
          axios.get("http://localhost:5000/api/stop/map-data"),
          axios.get("http://localhost:5000/api/route/map-data"),
        ]);
      setStops(stopsRes.data.filter((stop) => stop.stop_lat && stop.stop_lon));
        setRoutes(routesRes.data);
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
      }
    };

  useEffect(() => {
    fetchData();
  }, []);

  const getRandomPastelColor = () => {
    const hue = Math.floor(Math.random() * 360);
    return `hsl(${hue}, 70%, 60%)`;
  };

  return (
    <Box
      sx={{
        width: "100%",
        height: "calc(100vh - 48px)",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <Paper elevation={1} sx={{ mb: 2 }}>
        <Box sx={{ p: 2, pb: 0 }}>
          <Typography variant="h5" component="h1" fontWeight="bold" gutterBottom>
            Static Dashboard
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            View and analyze transit stops and routes across the system
          </Typography>
        </Box>
      </Paper>

      {loading ? (
        <Box
          sx={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            flexGrow: 1,
          }}
        >
          <CircularProgress />
        </Box>
      ) : (
        <Box sx={{ flexGrow: 1, position: "relative" }}>
          <MapContainer
            ref={mapRef}
            center={[28.6139, 77.209]}
            zoom={12}
            style={{ height: "100%", width: "100%", zIndex: 10 }}
            zoomControl={false}
          >
            <TileLayer
              url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
            />

            <ZoomControl position="bottomright" />
            <LayersControl position="topright" />

            <BusStopMarkers
              stopsData={stops}
              busStopIcon={busStopIcon}
              showStops={showStops}
            />

            {routes
              .filter(
                (route) =>
                  Array.isArray(route.coordinates) &&
                  route.coordinates.length > 0
              )
              .map((route) => (
                <Polyline
                  key={route.route_id}
                  positions={route.coordinates.map((coordinate) => [
                    coordinate.latitude,
                    coordinate.longitude,
                  ])}
                  color={getRandomPastelColor()}
                  weight={3}
                  opacity={0.7}
                >
                  <Popup>
                    <Box sx={{ p: 1.5, minWidth: 300 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        <DirectionsBus color="primary" />
                        <Typography variant="h6" component="div" fontWeight="bold">
                          {route.route_long_name}
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'grid', gap: 0.75 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2" color="text.secondary">
                            Route ID
                          </Typography>
                          <Typography variant="body2" fontWeight="medium">
                            {route.route_id}
                          </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2" color="text.secondary">
                            Short Name
                          </Typography>
                          <Typography variant="body2" fontWeight="medium">
                            {route.route_short_name}
                          </Typography>
                        </Box>
                        {route.route_desc && (
                          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                            <Typography variant="body2" color="text.secondary">
                              Description
                            </Typography>
                            <Typography variant="body2" fontWeight="medium">
                              {route.route_desc}
                            </Typography>
                          </Box>
                        )}
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2" color="text.secondary">
                            Route Type
                          </Typography>
                          <Typography variant="body2" fontWeight="medium">
                            {route.route_type}
                          </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2" color="text.secondary">
                            Status
                          </Typography>
                          <Typography 
                            variant="body2" 
                            fontWeight="medium"
                            sx={{ 
                              color: route.route_status === 'active' ? 'success.main' : 
                                     route.route_status === 'inactive' ? 'error.main' :
                                     route.route_status === 'temporary_closure' ? 'warning.main' : 'text.secondary'
                            }}
                          >
                            {route.route_status || "active"}
                          </Typography>
                        </Box>
                        {route.route_metrics && (
                          <>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                              <Typography variant="body2" color="text.secondary">
                                Total Stops
                              </Typography>
                              <Typography variant="body2" fontWeight="medium">
                                {route.route_metrics.total_stops || 0}
                              </Typography>
                            </Box>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                              <Typography variant="body2" color="text.secondary">
                                Total Trips
                              </Typography>
                              <Typography variant="body2" fontWeight="medium">
                                {route.route_metrics.total_trips || 0}
                              </Typography>
                            </Box>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                              <Typography variant="body2" color="text.secondary">
                                Total Distance
                              </Typography>
                              <Typography variant="body2" fontWeight="medium">
                                {route.route_metrics.total_distance ? `${route.route_metrics.total_distance.toFixed(2)} km` : "N/A"}
                              </Typography>
                            </Box>
                          </>
                        )}
                        {route.route_features && (
                          <Box sx={{ mt: 0.5 }}>
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 0.25 }}>
                              Features
                            </Typography>
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.25 }}>
                              {route.route_features.is_express && <Chip size="small" label="Express" />}
                              {route.route_features.is_rapid && <Chip size="small" label="Rapid" />}
                              {route.route_features.is_accessible && <Chip size="small" label="Accessible" />}
                              {route.route_features.has_wifi && <Chip size="small" label="WiFi" />}
                              {route.route_features.has_air_conditioning && <Chip size="small" label="AC" />}
                              {route.route_features.has_bike_rack && <Chip size="small" label="Bike Rack" />}
                            </Box>
                          </Box>
                        )}
                      </Box>
                    </Box>
                  </Popup>
                </Polyline>
              ))}

            <MapControls
              onRefresh={fetchData}
              showStops={showStops}
              onToggleStops={() => setShowStops(!showStops)}
            />
          </MapContainer>
        </Box>
      )}
    </Box>
  );
};

export default StaticDashboard;
