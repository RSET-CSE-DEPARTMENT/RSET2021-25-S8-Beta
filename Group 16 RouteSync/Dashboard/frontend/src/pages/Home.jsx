import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActionArea,
  Box,
  CircularProgress,
  Divider,
} from '@mui/material';
import {
  DirectionsBus,
  LocationOn,
  AccessTime,
  Route,
  Speed,
  AccessibilityNew,
  DirectionsBike,
  LocalParking,
  Schedule,
  People,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const API_URL = 'http://localhost:5000/api';

const Home = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    agencies: 0,
    routes: 0,
    stops: 0,
    trips: 0,
    stopTimes: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const [agenciesRes, routesRes, stopsRes, tripsRes, stopTimesRes] = await Promise.all([
        axios.get(`${API_URL}/agency`),
        axios.get(`${API_URL}/route`),
        axios.get(`${API_URL}/stop`),
        axios.get(`${API_URL}/trip`),
        axios.get(`${API_URL}/stop-times`),
      ]);

      setStats({
        agencies: agenciesRes.data.pagination.total,
        routes: routesRes.data.pagination.total,
        stops: stopsRes.data.pagination.total,
        trips: tripsRes.data.pagination.total,
        stopTimes: stopTimesRes.data.pagination.total,
      });
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ title, value, icon, color }) => (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" gap={2}>
          <Box
            sx={{
              backgroundColor: `${color}15`,
              borderRadius: '50%',
              p: 1,
              display: 'flex',
            }}
          >
            {icon}
          </Box>
          <Box>
            <Typography variant="h6" component="div">
              {value}
            </Typography>
            <Typography color="text.secondary" variant="body2">
              {title}
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  const QuickAccessCard = ({ title, description, icon, path, color }) => (
    <Card>
      <CardActionArea onClick={() => navigate(path)}>
        <CardContent>
          <Box display="flex" alignItems="center" gap={2}>
            <Box
              sx={{
                backgroundColor: `${color}15`,
                borderRadius: '50%',
                p: 1,
                display: 'flex',
              }}
            >
              {icon}
            </Box>
            <Box>
              <Typography variant="h6" component="div">
                {title}
              </Typography>
              <Typography color="text.secondary" variant="body2">
                {description}
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </CardActionArea>
    </Card>
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box mb={4}>
        <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
          Transit System Dashboard
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Overview of the transit system's data and analytics
        </Typography>
      </Box>

      {/* Statistics Section */}
      <Grid container spacing={3} mb={6}>
        <Grid item xs={12} md={2.4}>
          <StatCard
            title="Agencies"
            value={stats.agencies}
            icon={<DirectionsBus sx={{ color: '#1976d2' }} />}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} md={2.4}>
          <StatCard
            title="Routes"
            value={stats.routes}
            icon={<Route sx={{ color: '#2e7d32' }} />}
            color="#2e7d32"
          />
        </Grid>
        <Grid item xs={12} md={2.4}>
          <StatCard
            title="Stops"
            value={stats.stops}
            icon={<LocationOn sx={{ color: '#ed6c02' }} />}
            color="#ed6c02"
          />
        </Grid>
        <Grid item xs={12} md={2.4}>
          <StatCard
            title="Trips"
            value={stats.trips}
            icon={<AccessTime sx={{ color: '#9c27b0' }} />}
            color="#9c27b0"
          />
        </Grid>
        <Grid item xs={12} md={2.4}>
          <StatCard
            title="Stop Times"
            value={stats.stopTimes}
            icon={<Schedule sx={{ color: '#d32f2f' }} />}
            color="#d32f2f"
          />
        </Grid>
      </Grid>

      <Divider sx={{ my: 4 }} />

      {/* Quick Access Section */}
      <Typography variant="h5" component="h2" gutterBottom fontWeight="bold">
        Quick Access
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6} lg={4}>
          <QuickAccessCard
            title="Agencies"
            description="View and manage transit agencies"
            icon={<DirectionsBus sx={{ color: '#1976d2' }} />}
            path="/agency"
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} md={6} lg={4}>
          <QuickAccessCard
            title="Routes"
            description="Explore transit routes and their details"
            icon={<Route sx={{ color: '#2e7d32' }} />}
            path="/route"
            color="#2e7d32"
          />
        </Grid>
        <Grid item xs={12} md={6} lg={4}>
          <QuickAccessCard
            title="Stops"
            description="View stop locations and facilities"
            icon={<LocationOn sx={{ color: '#ed6c02' }} />}
            path="/stop"
            color="#ed6c02"
          />
        </Grid>
        <Grid item xs={12} md={6} lg={4}>
          <QuickAccessCard
            title="Trips"
            description="Monitor trips and schedules"
            icon={<AccessTime sx={{ color: '#9c27b0' }} />}
            path="/trip"
            color="#9c27b0"
          />
        </Grid>
        <Grid item xs={12} md={6} lg={4}>
          <QuickAccessCard
            title="Stop Times"
            description="Check arrival and departure times"
            icon={<Schedule sx={{ color: '#d32f2f' }} />}
            path="/stopTimes"
            color="#d32f2f"
          />
        </Grid>
        <Grid item xs={12} md={6} lg={4}>
          <QuickAccessCard
            title="Static Data"
            description="View static transit information"
            icon={<DirectionsBus sx={{ color: '#1976d2' }} />}
            path="/static"
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} md={6} lg={4}>
          <QuickAccessCard
            title="Real-Time Data"
            description="Monitor live transit updates"
            icon={<Speed sx={{ color: '#2e7d32' }} />}
            path="/realtime"
            color="#2e7d32"
          />
        </Grid>
        <Grid item xs={12} md={6} lg={4}>
          <QuickAccessCard
            title="Bus Management"
            description="Manage bus fleet and operations"
            icon={<DirectionsBus sx={{ color: '#ed6c02' }} />}
            path="/bus"
            color="#ed6c02"
          />
        </Grid>
        <Grid item xs={12} md={6} lg={4}>
          <QuickAccessCard
            title="Crew Management"
            description="Manage crew assignments and schedules"
            icon={<People sx={{ color: '#9c27b0' }} />}
            path="/crew"
            color="#9c27b0"
          />
        </Grid>
        <Grid item xs={12} md={6} lg={4}>
          <QuickAccessCard
            title="Bus Schedule"
            description="View and manage bus schedules"
            icon={<Schedule sx={{ color: '#d32f2f' }} />}
            path="/bus-schedule"
            color="#d32f2f"
          />
        </Grid>
        <Grid item xs={12} md={6} lg={4}>
          <QuickAccessCard
            title="Duty Schedule"
            description="Manage crew duty schedules"
            icon={<AccessTime sx={{ color: '#1976d2' }} />}
            path="/duty-schedule"
            color="#1976d2"
          />
        </Grid>
      </Grid>

      {/* Features Section */}
      <Box mt={6}>
        <Typography variant="h5" component="h2" gutterBottom fontWeight="bold">
          System Features
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" gap={2}>
                  <AccessibilityNew sx={{ color: '#1976d2' }} />
                  <Typography variant="h6">Accessibility</Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Track wheelchair accessibility and amenities across the transit system
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" gap={2}>
                  <Speed sx={{ color: '#2e7d32' }} />
                  <Typography variant="h6">Performance</Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Monitor service performance, delays, and reliability metrics
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" gap={2}>
                  <People sx={{ color: '#ed6c02' }} />
                  <Typography variant="h6">Ridership</Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Analyze passenger loads and ridership patterns
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default Home;