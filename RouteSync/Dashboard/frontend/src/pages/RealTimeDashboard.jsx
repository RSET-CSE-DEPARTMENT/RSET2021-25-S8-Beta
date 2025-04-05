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
import fetchRealTimeData from "../services/apiService";

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

const RealTimeDashboard = () => {
  const [busLocations, setBusLocations] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showStops, setShowStops] = useState(true);
  const mapRef = useRef(null);

  const busIcon = new Icon({
    iconUrl: "/src/img/bus.png",
    iconSize: [38, 38],
  });

  const fetchBusData = async () => {
    try {
      const data = await fetchRealTimeData();
      const vehicleData = data.entity
        .map((entity) => {
          if (entity.vehicle && entity.vehicle.position) {
            return {
              id: entity.vehicle.vehicle.id,
              latitude: entity.vehicle.position.latitude,
              longitude: entity.vehicle.position.longitude,
              routeId: entity.vehicle.trip?.routeId || "N/A",
              tripId: entity.vehicle.trip?.tripId || "N/A",
              speed: entity.vehicle.position.speed || 0,
              status: entity.vehicle.vehicleStatus || "active",
              occupancy: entity.vehicle.occupancyStatus || "unknown",
            };
          }
          return null;
        })
        .filter((vehicle) => vehicle !== null);
      setBusLocations(vehicleData);
    } catch (error) {
      setError("Error fetching real-time data");
      console.error("Error fetching real-time data:", error);
    }
  };

  useEffect(() => {
    setLoading(true);
    fetchBusData();
    setLoading(false);
    const intervalId = setInterval(() => {
      fetchBusData();
    }, 30000);
    return () => clearInterval(intervalId);
  }, []);

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
            Real-Time Transit Dashboard
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Monitor live bus locations across the system
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

            <MarkerClusterGroup chunkedLoading>
              {busLocations.map((bus) => (
                <Marker
                  icon={busIcon}
                  key={bus.id}
                  position={[bus.latitude, bus.longitude]}
                >
                  <Popup>
                    <Box sx={{ p: 1.5, minWidth: 300 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        <DirectionsBus color="primary" />
                        <Typography variant="h6" component="div" fontWeight="bold">
                          Bus {bus.id}
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'grid', gap: 0.75 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2" color="text.secondary">
                            Route ID
                          </Typography>
                          <Typography variant="body2" fontWeight="medium">
                            {bus.routeId}
                          </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2" color="text.secondary">
                            Trip ID
                          </Typography>
                          <Typography variant="body2" fontWeight="medium">
                            {bus.tripId}
                          </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2" color="text.secondary">
                            Speed
                          </Typography>
                          <Typography variant="body2" fontWeight="medium">
                            {bus.speed ? `${(bus.speed * 3.6).toFixed(1)} km/h` : "N/A"}
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
                              color: bus.status === 'active' ? 'success.main' : 
                                     bus.status === 'inactive' ? 'error.main' :
                                     bus.status === 'temporary_closure' ? 'warning.main' : 'text.secondary'
                            }}
                          >
                            {bus.status}
                          </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2" color="text.secondary">
                            Occupancy
                          </Typography>
                          <Typography 
                            variant="body2" 
                            fontWeight="medium"
                            sx={{ 
                              color: bus.occupancy === 'MANY_SEATS_AVAILABLE' ? 'success.main' : 
                                     bus.occupancy === 'FEW_SEATS_AVAILABLE' ? 'warning.main' :
                                     bus.occupancy === 'STANDING_ROOM_ONLY' ? 'error.main' : 'text.secondary'
                            }}
                          >
                            {bus.occupancy.replace(/_/g, ' ')}
                          </Typography>
                        </Box>
                      </Box>
                    </Box>
                  </Popup>
                </Marker>
              ))}
            </MarkerClusterGroup>

            <MapControls
              onRefresh={fetchBusData}
              showStops={showStops}
              onToggleStops={() => setShowStops(!showStops)}
            />
          </MapContainer>
        </Box>
      )}
    </Box>
  );
};

export default RealTimeDashboard;
