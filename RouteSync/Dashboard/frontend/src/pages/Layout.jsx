import { useState } from "react";
import { Outlet, Link, useLocation } from "react-router-dom";
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
} from "@mui/material";
import {
  DirectionsBus,
  LocationOn,
  AccessTime,
  Route,
  Speed,
  Equalizer,
  Home,
  People,
  Schedule,
  DirectionsBike,
  LocalParking,
} from "@mui/icons-material";

const DRAWER_WIDTH = 250;

// Define color scheme for navigation items
const navColors = {
  home: "#1976d2",
  static: "#1976d2",
  realtime: "#2e7d32",
  agency: "#1976d2",
  route: "#2e7d32",
  trip: "#9c27b0",
  stop: "#ed6c02",
  stopTimes: "#d32f2f",
  bus: "#ed6c02",
  crew: "#9c27b0",
  busSchedule: "#d32f2f",
  dutySchedule: "#1976d2",
};

const Layout = () => {
  const location = useLocation();

  const navLinks = [
    {
      label: "Home",
      icon: <Home />,
      link: "/",
      color: navColors.home,
    },
    {
      label: "Static",
      icon: <Equalizer />,
      link: "/static",
      color: navColors.static,
    },
    {
      label: "Real-Time",
      icon: <Speed />,
      link: "/realtime",
      color: navColors.realtime,
    },
    {
      label: "Agencies",
      icon: <DirectionsBus />,
      link: "/agency",
      color: navColors.agency,
    },
    {
      label: "Routes",
      icon: <Route />,
      link: "/route",
      color: navColors.route,
    },
    {
      label: "Trips",
      icon: <AccessTime />,
      link: "/trip",
      color: navColors.trip,
    },
    {
      label: "Stops",
      icon: <LocationOn />,
      link: "/stop",
      color: navColors.stop,
    },
    {
      label: "Stop Times",
      icon: <Schedule />,
      link: "/stopTimes",
      color: navColors.stopTimes,
    },
    {
      label: "Bus",
      icon: <DirectionsBus />,
      link: "/bus",
      color: navColors.bus,
    },
    {
      label: "Crew",
      icon: <People />,
      link: "/crew",
      color: navColors.crew,
    },
    {
      label: "Bus Schedule",
      icon: <Schedule />,
      link: "/bus-schedule",
      color: navColors.busSchedule,
    },
    {
      label: "Duty Schedule",
      icon: <AccessTime />,
      link: "/duty-schedule",
      color: navColors.dutySchedule,
    },
  ];

  return (
    <Box sx={{ display: "flex" }}>
      {/* Permanent Drawer */}
      <Drawer
        variant="permanent"
        sx={{
          width: DRAWER_WIDTH,
          flexShrink: 0,
          "& .MuiDrawer-paper": {
            width: DRAWER_WIDTH,
            boxSizing: "border-box",
            borderRight: "1px solid rgba(0, 0, 0, 0.12)",
            backgroundColor: "#f8fafc",
          },
        }}
      >
        <Box sx={{ overflow: "auto", mt: 2 }}>
          <List>
            {navLinks.map((navlink, index) => {
              const isActive = location.pathname === navlink.link;
              return (
                <Link
                  key={`link${index}`}
                  style={{ textDecoration: "none", fontFamily: "DM Sans" }}
                  to={navlink.link}
                >
                  <ListItem disablePadding>
                    <ListItemButton
                      sx={{
                        backgroundColor: isActive
                          ? `${navlink.color}15`
                          : "transparent",
                        "&:hover": {
                          backgroundColor: `${navlink.color}15`,
                        },
                        borderLeft: isActive
                          ? `4px solid ${navlink.color}`
                          : "4px solid transparent",
                      }}
                    >
                      <ListItemIcon sx={{ color: navlink.color }}>
                        {navlink.icon}
                      </ListItemIcon>
                      <ListItemText
                        className="font-dm"
                        primary={navlink.label}
                        sx={{
                          color: isActive ? navlink.color : "rgb(51, 65, 85)",
                          "& .MuiTypography-root": {
                            fontSize: "0.875rem",
                            fontWeight: isActive ? 600 : 500,
                          },
                        }}
                      />
                    </ListItemButton>
                  </ListItem>
                </Link>
              );
            })}
          </List>
          <Divider />
        </Box>
      </Drawer>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: { xs: 2, sm: 3, md: 4 },
          width: { sm: `calc(100% - ${DRAWER_WIDTH}px)` },
          backgroundColor: "#ffffff",
          minHeight: "100vh",
        }}
      >
        <Outlet />
      </Box>
    </Box>
  );
};

export default Layout;
