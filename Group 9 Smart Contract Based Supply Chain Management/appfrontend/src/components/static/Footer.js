import React from "react"; 

import Link from '@mui/material/Link';
import Container from '@mui/material/Container';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import GitHubIcon from '@mui/icons-material/GitHub';
import LinkedInIcon from '@mui/icons-material/LinkedIn';
import TwitterIcon from '@mui/icons-material/Twitter';

import "../../css/Footer.css"; 
 
/**
 * Footer component. Present in every page when user is an authenticated one.
 * 
 * @author syuki
 */
export default function Footer({isAuthenticated}) {
    if(!isAuthenticated){
        return null;
    } else {
        return(
            <div>
                <center>
                    <footer>
                        <Container maxWidth="sm" > 
                            <Typography variant="body1" style={{ fontSize: 13}}> 
                            <div className="AppFooter">
                                {/* social media */}
                                <Grid container justifyContent="center">
                                    <Grid item xs={2}>
                                        <Link className="FooterLink" href="https://github.com/Shira98" target="_blank" >{" "}<GitHubIcon /></Link>
                                    </Grid>
                                    <Grid item xs={1}> 
                                        <Link className="FooterLink" href="https://twitter.com/d_praneetha" target="_blank" >{" "}<TwitterIcon /></Link>
                                    </Grid>
                                    <Grid item xs={2}>
                                        <Link className="FooterLink" href="https://www.linkedin.com/in/praneetha-d-13996517a/" target="_blank">{"   "}
                                            <LinkedInIcon />
                                        </Link>
                                    </Grid>
                                </Grid>
                                <br/>
                                Powered by <Link className="FooterLink" href="https://mui.com/" target="_blank" >material-ui</Link> and 
                                <Link className="FooterLink" href="https://reactjs.org/" target="_blank" 
                                > {" "}React</Link> &copy; {new Date().getFullYear()} 
                                </div>
                            </Typography> 
                        </Container>
                    </footer>
                </center>
            </div>
        );
    } 
};
