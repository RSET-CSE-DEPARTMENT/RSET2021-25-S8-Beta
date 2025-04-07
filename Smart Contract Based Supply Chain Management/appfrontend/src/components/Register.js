import React, { useEffect } from "react";
import { useNavigate } from 'react-router-dom';

import Button from '@mui/material/Button';
import Tooltip from '@mui/material/Tooltip';
import Typography from '@mui/material/Typography';
import Paper from "@mui/material/Paper";
import Backdrop from '@mui/material/Backdrop';
import IconButton from '@mui/material/IconButton';
import ArrowBackIosIcon from '@mui/icons-material/ArrowBackIos';
import Link from '@mui/material/Link';
import Grid from '@mui/material/Grid';
import GitHubIcon from '@mui/icons-material/GitHub';
import LinkedInIcon from '@mui/icons-material/LinkedIn';
import TwitterIcon from '@mui/icons-material/Twitter';
import Divider from '@mui/material/Divider';

import { USER_TYPES } from "./enum/UsersEnum";

import "../css/NewUser.css";

/**
 * Provides account types to users for address registration -
 *  - Producers, 
 *  - Distributors, 
 *  - Retailers.
 * 
 * @author syuki
 */
const Register = ({contract, currentAddress, isAuthenticated}) => {

    const navigate = useNavigate();

    useEffect(() => {
        if(isAuthenticated){
        navigate('/');
        }
    }, []);

    return (
        <div className="new-user-body">
            <Backdrop open className="backdrop-design">
                <Paper elevation={0} className="new-user-paper">
                    <IconButton color="inherit">
                        <ArrowBackIosIcon fontSize="large" aria-label="back" onClick={() => navigate(-1)} />
                    </IconButton>
                    <center>
                        <Typography component="h1" variant="h5" style={{ fontWeight: "500" }}>Register</Typography>
                        <p>Choose your account type for the address <b>{currentAddress}</b></p>
                        <Grid 
                            container 
                            color="secondary" 
                            justifyContent="center" 
                            direction={'column'} 
                            spacing={2}
                        >
                            <Grid item xs={12}>
                                <Tooltip arrow title="Create batches of various products." placement="right">
                                    <Button style={{ width: 200 }}
                                        variant="contained"
                                        color="primary"
                                        className="nf-button"
                                        onClick={() => navigate("/confirm-registration", {
                                            state: {
                                                type: USER_TYPES[0]
                                            }
                                        })}
                                    >
                                        Producer
                                    </Button>
                                </Tooltip>
                            </Grid>
                            <Grid item xs={12}>
                                <Tooltip arrow title="Buy batches from producer and sell to retailer." placement="right">
                                    <Button style={{ width: 200 }}
                                        variant="contained"
                                        color="primary"
                                        className="nf-button"
                                        onClick={() => navigate("/confirm-registration", {
                                            state: {
                                                type: USER_TYPES[1]
                                            }
                                        })}
                                    >
                                        Distributor
                                    </Button>
                                </Tooltip>
                            </Grid>
                            <Grid item xs={12}>
                                <Tooltip arrow title="Buy batches from distributor and sell to consumers." placement="right">
                                    <Button style={{ width: 200, marginBottom: 30 }}
                                        variant="contained"
                                        color="primary"
                                        className="button"
                                        onClick={() => navigate("/confirm-registration", {
                                            state: {
                                                type: USER_TYPES[2]
                                            }
                                        })}
                                    >
                                        Retailer
                                    </Button>
                                </Tooltip>
                            </Grid>
                        </Grid>
                        <Divider style={{ marginBottom: 20 }} />
                        {/* social media */}
                        <Grid container justifyContent="center">
                                <Grid item xs={2}>
                                    <Link className="ModalLink" href="https://github.com/Shira98" target="_blank" >{" "}<GitHubIcon /></Link>
                                </Grid>
                                <Grid item xs={1}> 
                                    <Link className="ModalLink" href="https://twitter.com/d_praneetha" target="_blank" >{" "}<TwitterIcon /></Link>
                                </Grid>
                                <Grid item xs={2}>
                                    <Link className="ModalLink" href="https://www.linkedin.com/in/praneetha-d-13996517a/" target="_blank">{"   "}
                                        <LinkedInIcon />
                                    </Link>
                                </Grid>
                            </Grid>
                            <br/>
                            Powered by <Link className="ModalLink" href="https://mui.com/" target="_blank" >material-ui</Link> and 
                            <Link className="ModalLink" href="https://reactjs.org/" target="_blank" 
                            > {" "}React</Link> &copy; {new Date().getFullYear()} 
                    </center>
                </Paper>
            </Backdrop>
        </div>
    );
 };

 export default Register;