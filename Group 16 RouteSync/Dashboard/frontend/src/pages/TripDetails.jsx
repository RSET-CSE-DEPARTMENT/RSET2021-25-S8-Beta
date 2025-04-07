import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  Chip,
  Divider,
  IconButton,
  CircularProgress,
} from "@mui/material";
import {
  AccessTime,
  DirectionsBus,
  Speed,
  Update,
  AccessibilityNew,
  DirectionsBike,
  ArrowBack,
  Schedule,
  Route,
  Info,
} from "@mui/icons-material";
import { MapContainer, TileLayer, Polyline, ZoomControl, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

// Fix for default marker icons in React-Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

// Component to handle map updates
const MapUpdater = ({ bounds }) => {
  const map = useMap();
  useEffect(() => {
    if (bounds) {
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [bounds, map]);
  return null;
};

const API_URL = "http://localhost:5000/api/trip";

const TripDetails = () => {
  const { tripId } = useParams();
  const navigate = useNavigate();
  const [trip, setTrip] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTripDetails();
  }, [tripId]);

  const fetchTripDetails = async () => {
    try {
      const response = await axios.get(`${API_URL}/${tripId}`);
      setTrip(response.data);
    } catch (error) {
      console.error("Error fetching trip details:", error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return "N/A";
    return new Date(dateString).toLocaleDateString();
  };

  const getFeatureChips = (features) => {
    if (!features) return null;
    return (
      <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
        {features.is_express && (
          <Chip
            label="Express"
            color="primary"
            size="small"
            icon={<Speed />}
          />
        )}
        {features.is_rapid && (
          <Chip
            label="Rapid"
            color="secondary"
            size="small"
            icon={<Route />}
          />
        )}
        {features.is_accessible && (
          <Chip
            label="Accessible"
            color="info"
            size="small"
            icon={<AccessibilityNew />}
          />
        )}
      </Box>
    );
  };

  const getDirectionLabel = (directionId) => {
    return directionId === 0 ? "Outbound" : "Inbound";
  };

  const calculateBounds = (stops) => {
    if (!stops || stops.length === 0) return null;
    const lats = stops.map(stop => stop.stop_lat);
    const lngs = stops.map(stop => stop.stop_lon);
    return [
      [Math.min(...lats), Math.min(...lngs)],
      [Math.max(...lats), Math.max(...lngs)]
    ];
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  if (!trip) {
    return (
      <Container>
        <Typography variant="h5" color="error">
          Trip not found
        </Typography>
      </Container>
    );
  }

  return (
    <Container>
      <Box sx={{ mt: 4, mb: 2 }}>
        <IconButton onClick={() => navigate(-1)} sx={{ mb: 2 }}>
          <ArrowBack />
        </IconButton>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          {trip.trip_short_name || trip.trip_long_name}
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Trip Details
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Trip Map */}
        {trip.stops && trip.stops.length > 0 && (
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Trip Route Map
              </Typography>
              <Box 
                sx={{ 
                  height: 400, 
                  width: '100%', 
                  borderRadius: 1, 
                  overflow: 'hidden',
                  border: '1px solid',
                  borderColor: 'divider',
                  bgcolor: 'background.paper'
                }}
              >
                <MapContainer
                  center={[28.6139, 77.209]}
                  zoom={12}
                  style={{ height: '100%', width: '100%' }}
                  zoomControl={false}
                  scrollWheelZoom={true}
                >
                  <TileLayer
                    url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
                  />
                  <ZoomControl position="bottomright" />
                  <MapUpdater bounds={calculateBounds(trip.stops)} />
                  <Polyline
                    positions={trip.stops.map(stop => [stop.stop_lat, stop.stop_lon])}
                    color="#1976d2"
                    weight={4}
                    opacity={0.8}
                    dashArray="5, 10"
                  />
                </MapContainer>
              </Box>
            </Paper>
          </Grid>
        )}

        {/* Basic Information */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Basic Information
            </Typography>
            <Box sx={{ display: 'grid', gap: 1 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2" color="text.secondary">
                  Trip ID
                </Typography>
                <Typography variant="body2" fontWeight="medium">
                  {trip.trip_id}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2" color="text.secondary">
                  Direction
                </Typography>
                <Typography variant="body2" fontWeight="medium">
                  {getDirectionLabel(trip.direction_id)}
                </Typography>
              </Box>
              {trip.block_id && (
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="text.secondary">
                    Block ID
                  </Typography>
                  <Typography variant="body2" fontWeight="medium">
                    {trip.block_id}
                  </Typography>
                </Box>
              )}
            </Box>
          </Paper>
        </Grid>

        {/* Route & Service Information */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Route & Service
            </Typography>
            <Box sx={{ display: 'grid', gap: 1 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2" color="text.secondary">
                  Route ID
                </Typography>
                <Typography variant="body2" fontWeight="medium">
                  {trip.route_id}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2" color="text.secondary">
                  Service ID
                </Typography>
                <Typography variant="body2" fontWeight="medium">
                  {trip.service_id}
                </Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>

        {/* Trip Metrics */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Trip Metrics
            </Typography>
            <Box sx={{ display: 'grid', gap: 1 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2" color="text.secondary">
                  Total Stops
                </Typography>
                <Typography variant="body2" fontWeight="medium">
                  {trip.trip_metrics?.total_stops || 0}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2" color="text.secondary">
                  Total Distance
                </Typography>
                <Typography variant="body2" fontWeight="medium">
                  {trip.trip_metrics?.total_distance || 0} km
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2" color="text.secondary">
                  Total Duration
                </Typography>
                <Typography variant="body2" fontWeight="medium">
                  {trip.trip_metrics?.total_duration || 0} min
                </Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>

        {/* Features */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Features
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              {getFeatureChips(trip.trip_features)}
              <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                {trip.wheelchair_accessible && (
                  <Chip
                    label="Wheelchair Accessible"
                    color="success"
                    size="small"
                    icon={<AccessibilityNew />}
                  />
                )}
                {trip.bikes_allowed && (
                  <Chip
                    label="Bikes Allowed"
                    color="success"
                    size="small"
                    icon={<DirectionsBike />}
                  />
                )}
              </Box>
            </Box>
          </Paper>
        </Grid>

        {/* System Information */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              System Information
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Update fontSize="small" color="action" />
                  <Typography variant="body2">
                    Last Update: {formatDate(trip.trip_metadata?.last_update)}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Schedule fontSize="small" color="action" />
                  <Typography variant="body2">
                    Schedule: {trip.trip_schedule?.operating_hours || "N/A"}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Info fontSize="small" color="action" />
                  <Typography variant="body2">
                    Status: {trip.trip_status || "Active"}
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default TripDetails; 