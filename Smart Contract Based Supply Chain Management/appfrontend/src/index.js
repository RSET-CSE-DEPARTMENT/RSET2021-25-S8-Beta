import React from "react";
import ReactDOM from "react-dom/client";
import { Dapp } from "./components/Dapp";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import CssBaseline from '@mui/material/CssBaseline';

const theme = createTheme({
    typography: {
        fontFamily: [
            '-apple-system',
            'BlinkMacSystemFont',
            '"Segoe UI"',
            'Roboto',
            '"Helvetica Neue"',
            'Arial',
            'sans-serif',
            '"Apple Color Emoji"',
            '"Segoe UI Emoji"',
            '"Segoe UI Symbol"',
          ].join(','),
    },
    
    palette: {
        background: {
            default: "#d4ccdd"
        },
        text: {
            primary: "#2D323F",
            secondary: "#FBFAFA",
        },
        primary: {
            main: "#92869F",
            text: "black",
        },
        secondary: {
            main: "#2D323F",
            text: "#FBFAFA"
        },
        info: {
            main: "#EDB043" 
        },
        warning: {
            main: "#938294"
        } 
    }
});

const root = ReactDOM.createRoot(document.getElementById("root"));

root.render(
  <React.StrictMode>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Dapp />
    </ThemeProvider>
  </React.StrictMode>
);
