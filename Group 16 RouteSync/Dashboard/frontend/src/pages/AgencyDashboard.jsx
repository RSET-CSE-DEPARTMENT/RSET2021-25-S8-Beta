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
  Dialog,
  DialogTitle,
  DialogContent,
  IconButton,
  Divider,
} from "@mui/material";
import {
  AccessTime,
  DirectionsBus,
  LocationOn,
  Speed,
  Update,
  Close,
  Phone,
  Language,
  Schedule,
  Info,
} from "@mui/icons-material";

const API_URL = "http://localhost:5000/api/agency";

const AgencyDashboard = () => {
  const [agencies, setAgencies] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalAgencies, setTotalAgencies] = useState(0);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedFields, setSelectedFields] = useState(null);
  const [selectedAgency, setSelectedAgency] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);

  useEffect(() => {
    fetchAgencies();
  }, [currentPage, searchQuery, selectedFields]);

  const fetchAgencies = async () => {
    setLoading(true);
    try {
      const response = await axios.get(API_URL, {
        params: {
          page: currentPage,
          limit: 50,
          agency_name: searchQuery || undefined,
          fields: selectedFields ? JSON.stringify(selectedFields) : undefined,
        },
      });
      setAgencies(response.data.agencies);
      setTotalPages(response.data.pagination.totalPages);
      setTotalAgencies(response.data.pagination.total);
    } catch (error) {
      console.error("Error fetching agencies:", error);
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
        {features.has_rapid_transit && (
          <Chip
            label="Rapid Transit"
            color="primary"
            size="small"
            icon={<Speed />}
          />
        )}
        {features.has_express_routes && (
          <Chip
            label="Express Routes"
            color="secondary"
            size="small"
            icon={<DirectionsBus />}
          />
        )}
        {features.has_airport_connectivity && (
          <Chip
            label="Airport Service"
            color="success"
            size="small"
            icon={<LocationOn />}
          />
        )}
        {features.has_intercity_connectivity && (
          <Chip
            label="Intercity Service"
            color="info"
            size="small"
            icon={<DirectionsBus />}
          />
        )}
      </Box>
    );
  };

  const handleRowClick = (agency) => {
    setSelectedAgency(agency);
    setOpenDialog(true);
  };

  return (
    <Container>
      <Typography variant="h4" fontWeight="bold" mt={4} mb={2}>
        Agency Dashboard
      </Typography>

      {/* Statistics Section */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1}>
                <DirectionsBus color="primary" />
                <Typography variant="h6">Total Agencies: {totalAgencies}</Typography>
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
        label="Search by Agency Name"
        variant="outlined"
        fullWidth
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        sx={{ mb: 2 }}
      />

      {/* Agencies Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>
                <strong>Agency ID</strong>
              </TableCell>
              <TableCell>
                <strong>Agency Name</strong>
              </TableCell>
              <TableCell>
                <strong>Contact</strong>
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
              agencies.map((agency) => (
                <TableRow 
                  key={agency.agency_id}
                  onClick={() => handleRowClick(agency)}
                  sx={{ 
                    cursor: 'pointer',
                    '&:hover': {
                      backgroundColor: 'action.hover',
                    },
                  }}
                >
                  <TableCell>{agency.agency_id}</TableCell>
                  <TableCell>
                    <Typography variant="body1">{agency.agency_name}</Typography>
                    <Typography variant="caption" color="textSecondary">
                      {agency.agency_url}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">{agency.agency_phone}</Typography>
                    <Typography variant="caption" color="textSecondary">
                      {agency.agency_timezone}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      Stops: {agency.agency_metrics?.total_stops || 0}
                    </Typography>
                    <Typography variant="body2">
                      Routes: {agency.agency_metrics?.total_routes || 0}
                    </Typography>
                    <Typography variant="body2">
                      Trips: {agency.agency_metrics?.total_trips || 0}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {getFeatureChips(agency.agency_features)}
                  </TableCell>
                  <TableCell>
                    <Tooltip title="Last Route Update">
                      <Box display="flex" alignItems="center" gap={1}>
                        <Update fontSize="small" />
                        <Typography variant="caption">
                          {formatDate(agency.agency_metadata?.last_route_update)}
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
        count={totalAgencies}
        page={currentPage - 1}
        onPageChange={(e, newPage) => setCurrentPage(newPage + 1)}
        rowsPerPage={50}
        rowsPerPageOptions={[50]}
      />

      {/* Agency Details Dialog */}
      <Dialog 
        open={openDialog} 
        onClose={() => setOpenDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box display="flex" alignItems="center" gap={1}>
              <DirectionsBus color="primary" />
              <Typography variant="h6" component="div" fontWeight="bold">
                {selectedAgency?.agency_name}
              </Typography>
            </Box>
            <IconButton onClick={() => setOpenDialog(false)} size="small">
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedAgency && (
            <Box sx={{ display: 'grid', gap: 2, p: 1 }}>
              {/* Basic Information */}
              <Box>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Basic Information
                </Typography>
                <Box sx={{ display: 'grid', gap: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="text.secondary">
                      Agency ID
                    </Typography>
                    <Typography variant="body2" fontWeight="medium">
                      {selectedAgency.agency_id}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="text.secondary">
                      Timezone
                    </Typography>
                    <Typography variant="body2" fontWeight="medium">
                      {selectedAgency.agency_timezone}
                    </Typography>
                  </Box>
                </Box>
              </Box>

              <Divider />

              {/* Contact Information */}
              <Box>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Contact Information
                </Typography>
                <Box sx={{ display: 'grid', gap: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Phone fontSize="small" color="action" />
                    <Typography variant="body2">
                      {selectedAgency.agency_phone || "N/A"}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Language fontSize="small" color="action" />
                    <Typography variant="body2">
                      {selectedAgency.agency_url || "N/A"}
                    </Typography>
                  </Box>
                </Box>
              </Box>

              <Divider />

              {/* Metrics */}
              <Box>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  System Metrics
                </Typography>
                <Box sx={{ display: 'grid', gap: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="text.secondary">
                      Total Stops
                    </Typography>
                    <Typography variant="body2" fontWeight="medium">
                      {selectedAgency.agency_metrics?.total_stops || 0}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="text.secondary">
                      Total Routes
                    </Typography>
                    <Typography variant="body2" fontWeight="medium">
                      {selectedAgency.agency_metrics?.total_routes || 0}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="text.secondary">
                      Total Trips
                    </Typography>
                    <Typography variant="body2" fontWeight="medium">
                      {selectedAgency.agency_metrics?.total_trips || 0}
                    </Typography>
                  </Box>
                </Box>
              </Box>

              <Divider />

              {/* Features */}
              <Box>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Features
                </Typography>
                {getFeatureChips(selectedAgency.agency_features)}
              </Box>

              <Divider />

              {/* Metadata */}
              <Box>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  System Information
                </Typography>
                <Box sx={{ display: 'grid', gap: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Update fontSize="small" color="action" />
                    <Typography variant="body2">
                      Last Route Update: {formatDate(selectedAgency.agency_metadata?.last_route_update)}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Schedule fontSize="small" color="action" />
                    <Typography variant="body2">
                      Operating Hours: {selectedAgency.agency_metadata?.operating_hours || "N/A"}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Info fontSize="small" color="action" />
                    <Typography variant="body2">
                      Status: {selectedAgency.agency_status || "Active"}
                    </Typography>
                  </Box>
                </Box>
              </Box>
            </Box>
          )}
        </DialogContent>
      </Dialog>
    </Container>
  );
};

export default AgencyDashboard;
