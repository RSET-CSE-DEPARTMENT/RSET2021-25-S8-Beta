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
  Map,
  Info,
  ArrowBack,
  Schedule,
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

const API_URL = "http://localhost:5000/api/route";

const RouteDetails = () => {
  const { routeId } = useParams();
  const navigate = useNavigate();
  const [route, setRoute] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRouteDetails();
  }, [routeId]);

  const fetchRouteDetails = async () => {
    try {
      const response = await axios.get(`${API_URL}/specific/${routeId}`);
      setRoute(response.data);
    } catch (error) {
      console.error("Error fetching route details:", error);
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
            label="Rapid Transit"
            color="secondary"
            size="small"
            icon={<DirectionsBus />}
          />
        )}
        {features.is_accessible && (
          <Chip
            label="Accessible"
            color="success"
            size="small"
            icon={<AccessibilityNew />}
          />
        )}
      </Box>
    );
  };

  const getRouteTypeLabel = (type) => {
    const types = {
      0: "Tram/Streetcar",
      1: "Subway/Metro",
      2: "Rail",
      3: "Bus",
      4: "Ferry",
      5: "Cable Car",
      6: "Gondola",
      7: "Funicular",
    };
    return types[type] || `Type ${type}`;
  };

  const calculateBounds = (coordinates) => {
    if (!coordinates || coordinates.length === 0) return null;
    const lats = coordinates.map(coord => coord.latitude);
    const lngs = coordinates.map(coord => coord.longitude);
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

  if (!route) {
    return (
      <Container>
        <Typography variant="h5" color="error">
          Route not found
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
          {route.route_short_name} - {route.route_long_name}
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Route Details
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Basic Information */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Basic Information
            </Typography>
            <Box sx={{ display: 'grid', gap: 1 }}>
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
                  Type
                </Typography>
                <Typography variant="body2" fontWeight="medium">
                  {getRouteTypeLabel(route.route_type)}
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
            </Box>
          </Paper>
        </Grid>

        {/* Route Map */}
        {route.coordinates && route.coordinates.length > 0 && (
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Route Map
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
                  <MapUpdater bounds={calculateBounds(route.coordinates)} />
                  <Polyline
                    positions={route.coordinates.map(coord => [coord.latitude, coord.longitude])}
                    color={route.route_color || '#1976d2'}
                    weight={4}
                    opacity={0.8}
                    dashArray="5, 10"
                  />
                </MapContainer>
              </Box>
            </Paper>
          </Grid>
        )}

        {/* Metrics */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Route Metrics
            </Typography>
            <Box sx={{ display: 'grid', gap: 1 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2" color="text.secondary">
                  Total Stops
                </Typography>
                <Typography variant="body2" fontWeight="medium">
                  {route.route_metrics?.total_stops || 0}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2" color="text.secondary">
                  Total Trips
                </Typography>
                <Typography variant="body2" fontWeight="medium">
                  {route.route_metrics?.total_trips || 0}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2" color="text.secondary">
                  Average Trip Duration
                </Typography>
                <Typography variant="body2" fontWeight="medium">
                  {route.route_metrics?.average_trip_duration || 0} minutes
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
            {getFeatureChips(route.route_features)}
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
                    Last Trip Update: {formatDate(route.route_metadata?.last_trip_update)}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Schedule fontSize="small" color="action" />
                  <Typography variant="body2">
                    Schedule: {route.route_schedule?.operating_hours || "N/A"}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Info fontSize="small" color="action" />
                  <Typography variant="body2">
                    Status: {route.route_status || "Active"}
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

export default RouteDetails; 