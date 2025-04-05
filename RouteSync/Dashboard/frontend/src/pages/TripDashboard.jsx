import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import {
  Container,
  Typography,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  TablePagination,
  Box,
  Grid,
  Card,
  CardContent,
  Chip,
  Tooltip,
} from "@mui/material";
import {
  AccessTime,
  DirectionsBus,
  AccessibilityNew,
  DirectionsBike,
  Update,
  Speed,
  Route,
} from "@mui/icons-material";

const API_URL = "http://localhost:5000/api/trip";

const TripDashboard = () => {
  const navigate = useNavigate();
  const [trips, setTrips] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalTrips, setTotalTrips] = useState(0);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedFields, setSelectedFields] = useState(null);

  useEffect(() => {
    fetchTrips();
  }, [currentPage, searchQuery, selectedFields]);

  const fetchTrips = async () => {
    setLoading(true);
    try {
      const response = await axios.get(API_URL, {
        params: {
          page: currentPage,
          limit: 50,
          trip_id: searchQuery || undefined,
          fields: selectedFields ? JSON.stringify(selectedFields) : undefined,
        },
      });
      setTrips(response.data.trips);
      setTotalPages(response.data.pagination.totalPages);
      setTotalTrips(response.data.pagination.total);
    } catch (error) {
      console.error("Error fetching trips:", error);
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

  const handleRowClick = (tripId) => {
    navigate(`/trip/${tripId}`);
  };

  return (
    <Container>
      <Typography variant="h4" fontWeight="bold" mt={4} mb={2}>
        Trip Dashboard
      </Typography>

      {/* Statistics Section */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1}>
                <DirectionsBus color="primary" />
                <Typography variant="h6">Total Trips: {totalTrips}</Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1}>
                <AccessTime color="primary" />
                <Typography variant="h6">
                  Page: {currentPage} / {totalPages}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Search Bar */}
      <TextField
        label="Search by Trip ID"
        variant="outlined"
        fullWidth
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        sx={{ mb: 2 }}
      />

      {/* Trips Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>
                <strong>Trip Info</strong>
              </TableCell>
              <TableCell>
                <strong>Route & Service</strong>
              </TableCell>
              <TableCell>
                <strong>Metrics</strong>
              </TableCell>
              <TableCell>
                <strong>Features</strong>
              </TableCell>
              <TableCell>
                <strong>Last Update</strong>
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  <CircularProgress />
                </TableCell>
              </TableRow>
            ) : (
              trips.map((trip) => (
                <TableRow 
                  key={trip.trip_id}
                  onClick={() => handleRowClick(trip.trip_id)}
                  sx={{ 
                    cursor: 'pointer',
                    '&:hover': {
                      backgroundColor: 'action.hover',
                    },
                  }}
                >
                  <TableCell>
                    <Typography variant="body1">{trip.trip_id}</Typography>
                    <Typography variant="body2" color="textSecondary">
                      {trip.trip_short_name || trip.trip_long_name}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      Direction: {getDirectionLabel(trip.direction_id)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      Route: {trip.route_id}
                    </Typography>
                    <Typography variant="body2">
                      Service: {trip.service_id}
                    </Typography>
                    {trip.block_id && (
                      <Typography variant="caption" color="textSecondary">
                        Block: {trip.block_id}
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      Stops: {trip.trip_metrics?.total_stops || 0}
                    </Typography>
                    <Typography variant="body2">
                      Distance: {trip.trip_metrics?.total_distance || 0} km
                    </Typography>
                    <Typography variant="body2">
                      Duration: {trip.trip_metrics?.total_duration || 0} min
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box display="flex" flexDirection="column" gap={1}>
                      {getFeatureChips(trip.trip_features)}
                      <Box display="flex" gap={1}>
                        {trip.wheelchair_accessible && (
                          <Tooltip title="Wheelchair Accessible">
                            <AccessibilityNew color="primary" fontSize="small" />
                          </Tooltip>
                        )}
                        {trip.bikes_allowed && (
                          <Tooltip title="Bikes Allowed">
                            <DirectionsBike color="primary" fontSize="small" />
                          </Tooltip>
                        )}
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Tooltip title="Last Update">
                      <Box display="flex" alignItems="center" gap={1}>
                        <Update fontSize="small" />
                        <Typography variant="caption">
                          {formatDate(trip.trip_metadata?.last_update)}
                        </Typography>
                      </Box>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Pagination */}
      <TablePagination
        component="div"
        count={totalTrips}
        page={currentPage - 1}
        onPageChange={(e, newPage) => setCurrentPage(newPage + 1)}
        rowsPerPage={50}
        rowsPerPageOptions={[50]}
      />
    </Container>
  );
};

export default TripDashboard;
