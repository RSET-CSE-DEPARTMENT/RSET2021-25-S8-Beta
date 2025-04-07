require("dotenv").config();
const express = require("express");
const cors = require("cors");
const connectDB = require("./db");
const compression = require("compression");

const agencyRoutes = require("./routes/agencyRoutes");
const routeRoutes = require("./routes/routeRoutes");
const tripRoutes = require("./routes/tripRoutes");
const stopRoutes = require("./routes/stopRoutes");
const stopTimesRoutes = require("./routes/stopTimesRoutes");

const app = express();
app.use(compression());
app.use(express.json());
app.use(cors());

connectDB();

app.use("/api/agency", agencyRoutes);
app.use("/api/route", routeRoutes);
app.use("/api/trip", tripRoutes);
app.use("/api/stop", stopRoutes);
app.use("/api/stop-times", stopTimesRoutes);

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
