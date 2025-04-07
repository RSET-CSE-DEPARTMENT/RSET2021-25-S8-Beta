import React, { useEffect, useState } from "react";
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
  LocalParking,
  Update,
  Schedule,
  People,
} from "@mui/icons-material";

const API_URL = "http://localhost:5000/api/stop-times";

const StopTimesDashboard = () => {
  const [stopTimes, setStopTimes] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalStopTimes, setTotalStopTimes] = useState(0);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedFields, setSelectedFields] = useState(null);

  useEffect(() => {
    fetchStopTimes();
  }, [currentPage, searchQuery, selectedFields]);

  const fetchStopTimes = async () => {
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
      setStopTimes(response.data.stopTimes);
      setTotalPages(response.data.pagination.totalPages);
      setTotalStopTimes(response.data.pagination.total);
    } catch (error) {
      console.error("Error fetching stop times:", error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return "N/A";
    return new Date(dateString).toLocaleDateString();
  };

  const formatTime = (timeString) => {
    if (!timeString) return "N/A";
    return timeString;
  };

  const getFeatureChips = (features) => {
    if (!features) return null;
    return (
      <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
        {features.is_accessible && (
          <Chip
            label="Accessible"
            color="primary"
            size="small"
            icon={<AccessibilityNew />}
          />
        )}
        {features.has_amenities && (
          <Chip
            label="Amenities"
            color="secondary"
            size="small"
            icon={<LocalParking />}
          />
        )}
      </Box>
    );
  };

  const getStopTimeTypeLabel = (type) => {
    const types = {
      0: "Regular",
      1: "Not Available",
      2: "Phone Agency",
      3: "Coordinate with Driver",
    };
    return types[type] || `Type ${type}`;
  };

  return (
    <Container>
      <Typography variant="h4" fontWeight="bold" mt={4} mb={2}>
        Stop Times Dashboard
      </Typography>

      {/* Statistics Section */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1}>
                <Schedule color="primary" />
                <Typography variant="h6">Total Stop Times: {totalStopTimes}</Typography>
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

      {/* Stop Times Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>
                <strong>Trip ID</strong>
              </TableCell>
              <TableCell>
                <strong>Stop ID</strong>
              </TableCell>
              <TableCell>
                <strong>Schedule</strong>
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
                <TableCell colSpan={6} align="center">
                  <CircularProgress />
                </TableCell>
              </TableRow>
            ) : (
              stopTimes.map((stopTime) => (
                <TableRow key={`${stopTime.trip_id}-${stopTime.stop_id}`}>
                  <TableCell>{stopTime.trip_id}</TableCell>
                  <TableCell>{stopTime.stop_id}</TableCell>
                  <TableCell>
                    <Box display="flex" flexDirection="column" gap={0.5}>
                      <Typography variant="body2">
                        Arrival: {formatTime(stopTime.arrival_time)}
                      </Typography>
                      <Typography variant="body2">
                        Departure: {formatTime(stopTime.departure_time)}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        Sequence: {stopTime.stop_sequence}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      Dwell Time: {stopTime.stop_metrics?.dwell_time || 0} sec
                    </Typography>
                    <Typography variant="body2">
                      Headway: {stopTime.stop_metrics?.headway_secs || 0} sec
                    </Typography>
                    <Typography variant="body2">
                      Passengers: {stopTime.stop_metrics?.passenger_load || 0}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {getFeatureChips(stopTime.stop_features)}
                  </TableCell>
                  <TableCell>
                    <Tooltip title="Last Update">
                      <Box display="flex" alignItems="center" gap={1}>
                        <Update fontSize="small" />
                        <Typography variant="caption">
                          {formatDate(stopTime.stop_metadata?.last_update)}
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
        count={totalStopTimes}
        page={currentPage - 1}
        onPageChange={(e, newPage) => setCurrentPage(newPage + 1)}
        rowsPerPage={50}
        rowsPerPageOptions={[50]}
      />
    </Container>
  );
};

export default StopTimesDashboard;
