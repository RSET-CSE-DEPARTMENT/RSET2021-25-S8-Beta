import { BrowserRouter, Routes, Route } from "react-router-dom";

import "./App.css";
import Layout from "./pages/Layout";
import Home from "./pages/Home";
import StaticDashboard from "./pages/StaticDashboard";
import RealTimeDashboard from "./pages/RealTimeDashboard";
import BusDashboard from "./pages/BusDashboard";
import RouteDashboard from "./pages/RouteDashboard";
import CrewDashboard from "./pages/CrewDashboard";
import BusScheduleDashboard from "./pages/BusScheduleDashboard";
import DutyScheduleDashboard from "./pages/DutyScheduleDashboard";
import { ThemeProvider } from "@emotion/react";
import theme from "./theme";
import StopDashboard from "./pages/StopDashboard";
import StopTimesDashboard from "./pages/StopTimesDashboard";
import TripDashboard from "./pages/TripDashboard";
import AgencyDashboard from "./pages/AgencyDashboard";
import RouteDetails from "./pages/RouteDetails";
import TripDetails from "./pages/TripDetails";

function App() {
  return (
    <ThemeProvider theme={theme}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Home />} />

            <Route path="static" element={<StaticDashboard />} />
            <Route path="realtime" element={<RealTimeDashboard />} />

            <Route path="agency" element={<AgencyDashboard />} />
            <Route path="route" element={<RouteDashboard />} />
            <Route path="route/:routeId" element={<RouteDetails />} />
            <Route path="trip" element={<TripDashboard />} />
            <Route path="trip/:tripId" element={<TripDetails />} />
            <Route path="stop" element={<StopDashboard />} />
            <Route path="stopTimes" element={<StopTimesDashboard />} />
            <Route path="bus" element={<BusDashboard />} />
            <Route path="crew" element={<CrewDashboard />} />

            <Route path="bus-schedule" element={<BusScheduleDashboard />} />
            <Route path="duty-schedule" element={<DutyScheduleDashboard />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
