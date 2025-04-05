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
  Speed,
  Update,
  AccessibilityNew,
} from "@mui/icons-material";

const API_URL = "http://localhost:5000/api/route";

const RouteDashboard = () => {
  const navigate = useNavigate();
  const [routes, setRoutes] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalRoutes, setTotalRoutes] = useState(0);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedFields, setSelectedFields] = useState(null);

  useEffect(() => {
    fetchRoutes();
  }, [currentPage, searchQuery, selectedFields]);

  const fetchRoutes = async () => {
    setLoading(true);
    try {
      const response = await axios.get(API_URL, {
        params: {
          page: currentPage,
          limit: 50,
          route_id: searchQuery || undefined,
          fields: selectedFields ? JSON.stringify(selectedFields) : undefined,
        },
      });
      setRoutes(response.data.routes);
      setTotalPages(response.data.pagination.totalPages);
      setTotalRoutes(response.data.pagination.total);
    } catch (error) {
      console.error("Error fetching routes:", error);
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

  const handleRowClick = (routeId) => {
    navigate(`/route/${routeId}`);
  };

  return (
    <Container>
      <Typography variant="h4" fontWeight="bold" mt={4} mb={2}>
        Route Dashboard
      </Typography>

      {/* Statistics Section */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1}>
                <DirectionsBus color="primary" />
                <Typography variant="h6">Total Routes: {totalRoutes}</Typography>
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
        label="Search by Route ID"
        variant="outlined"
        fullWidth
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        sx={{ mb: 2 }}
      />

      {/* Routes Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>
                <strong>Route ID</strong>
              </TableCell>
              <TableCell>
                <strong>Route Info</strong>
              </TableCell>
              <TableCell>
                <strong>Type</strong>
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
              routes.map((route) => (
                <TableRow 
                  key={route.route_id}
                  onClick={() => handleRowClick(route.route_id)}
                  sx={{ 
                    cursor: 'pointer',
                    '&:hover': {
                      backgroundColor: 'action.hover',
                    },
                  }}
                >
                  <TableCell>{route.route_id}</TableCell>
                  <TableCell>
                    <Typography variant="body1">
                      {route.route_short_name} - {route.route_long_name}
                    </Typography>
                    {route.route_desc && (
                      <Typography variant="caption" color="textSecondary">
                        {route.route_desc}
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1}>
                      <DirectionsBus color="primary" />
                      <Typography>{getRouteTypeLabel(route.route_type)}</Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      Stops: {route.route_metrics?.total_stops || 0}
                    </Typography>
                    <Typography variant="body2">
                      Trips: {route.route_metrics?.total_trips || 0}
                    </Typography>
                    <Typography variant="body2">
                      Avg Duration: {route.route_metrics?.average_trip_duration || 0} min
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {getFeatureChips(route.route_features)}
                  </TableCell>
                  <TableCell>
                    <Tooltip title="Last Trip Update">
                      <Box display="flex" alignItems="center" gap={1}>
                        <Update fontSize="small" />
                        <Typography variant="caption">
                          {formatDate(route.route_metadata?.last_trip_update)}
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
        count={totalRoutes}
        page={currentPage - 1}
        onPageChange={(e, newPage) => setCurrentPage(newPage + 1)}
        rowsPerPage={50}
        rowsPerPageOptions={[50]}
      />
    </Container>
  );
};

export default RouteDashboard;
