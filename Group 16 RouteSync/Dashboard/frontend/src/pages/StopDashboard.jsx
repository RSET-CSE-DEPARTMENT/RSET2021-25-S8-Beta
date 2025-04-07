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
  LocationOn,
  AccessibilityNew,
  Elevator,
  Stairs,
  Escalator,
  Update,
} from "@mui/icons-material";

const API_URL = "http://localhost:5000/api/stop";

const StopDashboard = () => {
  const [stops, setStops] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalStops, setTotalStops] = useState(0);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedFields, setSelectedFields] = useState(null);

  useEffect(() => {
    fetchStops();
  }, [currentPage, searchQuery, selectedFields]);

  const fetchStops = async () => {
    setLoading(true);
    try {
      const response = await axios.get(API_URL, {
        params: {
          page: currentPage,
          limit: 50,
          stop_name: searchQuery || undefined,
          fields: selectedFields ? JSON.stringify(selectedFields) : undefined,
        },
      });
      setStops(response.data.stops);
      setTotalPages(response.data.pagination.totalPages);
      setTotalStops(response.data.pagination.total);
    } catch (error) {
      console.error("Error fetching stops:", error);
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
        {features.has_elevator && (
          <Chip
            label="Elevator"
            color="primary"
            size="small"
            icon={<Elevator />}
          />
        )}
        {features.has_escalator && (
          <Chip
            label="Escalator"
            color="secondary"
            size="small"
            icon={<Escalator />}
          />
        )}
        {features.has_stairs && (
          <Chip
            label="Stairs"
            color="info"
            size="small"
            icon={<Stairs />}
          />
        )}
        {features.has_ramp && (
          <Chip
            label="Ramp"
            color="success"
            size="small"
            icon={<AccessibilityNew />}
          />
        )}
      </Box>
    );
  };

  const getLocationTypeLabel = (type) => {
    const types = {
      0: "Stop",
      1: "Station",
      2: "Station Entrance/Exit",
      3: "Generic Node",
      4: "Boarding Area",
    };
    return types[type] || `Type ${type}`;
  };

  return (
    <Container>
      <Typography variant="h4" fontWeight="bold" mt={4} mb={2}>
        Stop Dashboard
      </Typography>

      {/* Statistics Section */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1}>
                <LocationOn color="primary" />
                <Typography variant="h6">Total Stops: {totalStops}</Typography>
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
        label="Search by Stop Name"
        variant="outlined"
        fullWidth
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        sx={{ mb: 2 }}
      />

      {/* Stops Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>
                <strong>Stop ID</strong>
              </TableCell>
              <TableCell>
                <strong>Stop Info</strong>
              </TableCell>
              <TableCell>
                <strong>Location</strong>
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
              stops.map((stop) => (
                <TableRow key={stop.stop_id}>
                  <TableCell>{stop.stop_id}</TableCell>
                  <TableCell>
                    <Typography variant="body1">{stop.stop_name}</Typography>
                    {stop.stop_desc && (
                      <Typography variant="caption" color="textSecondary">
                        {stop.stop_desc}
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1}>
                      <LocationOn color="primary" />
                      <Typography>
                        {getLocationTypeLabel(stop.location_type)}
                      </Typography>
                    </Box>
                    <Typography variant="caption" color="textSecondary">
                      {stop.stop_lat}, {stop.stop_lon}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      Routes: {stop.stop_metrics?.total_routes || 0}
                    </Typography>
                    <Typography variant="body2">
                      Trips: {stop.stop_metrics?.total_trips || 0}
                    </Typography>
                    <Typography variant="body2">
                      Daily Boardings: {stop.stop_metrics?.average_daily_boardings || 0}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {getFeatureChips(stop.stop_features)}
                  </TableCell>
                  <TableCell>
                    <Tooltip title="Last Route Update">
                      <Box display="flex" alignItems="center" gap={1}>
                        <Update fontSize="small" />
                        <Typography variant="caption">
                          {formatDate(stop.stop_metadata?.last_route_update)}
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
        count={totalStops}
        page={currentPage - 1}
        onPageChange={(e, newPage) => setCurrentPage(newPage + 1)}
        rowsPerPage={50}
        rowsPerPageOptions={[50]}
      />
    </Container>
  );
};

export default StopDashboard;
