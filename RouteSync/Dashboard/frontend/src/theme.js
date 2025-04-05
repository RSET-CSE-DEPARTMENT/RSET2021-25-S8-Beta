import { createTheme } from "@mui/material/styles";

const theme = createTheme({
  palette: {
    primary: {
      main: "#007bff", // Custom primary color
    },
    secondary: {
      main: "#ff4081", // Custom secondary color
    },
    background: {
      default: "#f4f4f4",
    },
  },
  typography: {
    fontFamily: "DM Sans, sans-serif",
    h1: {
      fontSize: "2rem",
      fontWeight: 700,
    },
    body1: {
      fontSize: "1rem",
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: "8px", // Custom button styling
          textTransform: "none",
        },
      },
    },
  },
});

export default theme;
