import React, { useEffect, useState } from "react";
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  IconButton,
  Tooltip,
  TextField,
  TablePagination,
  InputAdornment,
} from "@mui/material";
import {
  DirectionsBus,
  Refresh,
  CheckCircle,
  Cancel,
  Warning,
  Search,
} from "@mui/icons-material";
import fetchRealTimeData from "../services/apiService";

const BusDashboard = () => {
  const [busData, setBusData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  const fetchBusData = async () => {
    try {
      setLoading(true);
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
      setBusData(vehicleData);
      setError(null);
    } catch (error) {
      setError("Error fetching bus data");
      console.error("Error fetching bus data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBusData();
    const intervalId = setInterval(fetchBusData, 30000);
    return () => clearInterval(intervalId);
  }, []);

  const getStatusColor = (status) => {
    switch (status) {
      case "active":
        return "success.main";
      case "inactive":
        return "error.main";
      case "temporary_closure":
        return "warning.main";
      default:
        return "text.secondary";
    }
  };

  const getOccupancyColor = (occupancy) => {
    switch (occupancy) {
      case "MANY_SEATS_AVAILABLE":
        return "success.main";
      case "FEW_SEATS_AVAILABLE":
        return "warning.main";
      case "STANDING_ROOM_ONLY":
        return "error.main";
      default:
        return "text.secondary";
    }
  };

  // Filter and pagination logic
  const filteredBuses = busData.filter((bus) =>
    bus.id.toString().toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleSearchChange = (event) => {
    setSearchQuery(event.target.value);
    setPage(0);
  };

  const paginatedBuses = filteredBuses.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  const statistics = {
    total: busData.length,
    active: busData.filter((bus) => bus.status === "active").length,
    inactive: busData.filter((bus) => bus.status === "inactive").length,
    temporary: busData.filter((bus) => bus.status === "temporary_closure").length,
  };

  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: "flex", justifyContent: "space-between", mb: 3 }}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          Bus Dashboard
        </Typography>
        <Tooltip title="Refresh Data">
          <IconButton onClick={fetchBusData} color="primary">
            <Refresh />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                <DirectionsBus color="primary" />
                <Typography variant="h6">Total Buses</Typography>
              </Box>
              <Typography variant="h4" sx={{ mt: 2, fontWeight: "bold" }}>
                {statistics.total}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                <CheckCircle color="success" />
                <Typography variant="h6">Active</Typography>
              </Box>
              <Typography variant="h4" sx={{ mt: 2, fontWeight: "bold", color: "success.main" }}>
                {statistics.active}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                <Cancel color="error" />
                <Typography variant="h6">Inactive</Typography>
              </Box>
              <Typography variant="h4" sx={{ mt: 2, fontWeight: "bold", color: "error.main" }}>
                {statistics.inactive}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                <Warning color="warning" />
                <Typography variant="h6">Temporary Closure</Typography>
              </Box>
              <Typography variant="h4" sx={{ mt: 2, fontWeight: "bold", color: "warning.main" }}>
                {statistics.temporary}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Search Bar */}
      <Box sx={{ mb: 3 }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Search by Bus ID..."
          value={searchQuery}
          onChange={handleSearchChange}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search color="action" />
              </InputAdornment>
            ),
          }}
        />
      </Box>

      {/* Bus Data Table */}
      <TableContainer component={Paper}>
        <Table sx={{ minWidth: 650 }}>
          <TableHead>
            <TableRow>
              <TableCell>Bus ID</TableCell>
              <TableCell>Route ID</TableCell>
              <TableCell>Trip ID</TableCell>
              <TableCell>Speed</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Occupancy</TableCell>
              <TableCell>Location</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {paginatedBuses.map((bus) => (
              <TableRow key={bus.id} hover>
                <TableCell>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <DirectionsBus color="primary" fontSize="small" />
                    {bus.id}
                  </Box>
                </TableCell>
                <TableCell>{bus.routeId}</TableCell>
                <TableCell>{bus.tripId}</TableCell>
                <TableCell>
                  {bus.speed ? `${(bus.speed * 3.6).toFixed(1)} km/h` : "N/A"}
                </TableCell>
                <TableCell>
                  <Typography
                    sx={{
                      color: getStatusColor(bus.status),
                      fontWeight: "medium",
                    }}
                  >
                    {bus.status}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography
                    sx={{
                      color: getOccupancyColor(bus.occupancy),
                      fontWeight: "medium",
                    }}
                  >
                    {bus.occupancy.replace(/_/g, " ")}
                  </Typography>
                </TableCell>
                <TableCell>
                  {`${bus.latitude.toFixed(4)}, ${bus.longitude.toFixed(4)}`}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={filteredBuses.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </TableContainer>

      {error && (
        <Typography color="error" sx={{ mt: 2 }}>
          {error}
        </Typography>
      )}
    </Box>
  );
};

export default BusDashboard;
