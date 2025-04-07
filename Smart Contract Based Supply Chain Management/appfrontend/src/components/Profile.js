import React, { useState, useEffect } from "react"; 
import { ethers } from "ethers";
import Button from '@mui/material/Button';
import Menu from '@mui/material/Menu';


import "../css/Profile.css";

/**
 * Component for the profile page. Fetches profile details from the registered user's account.
 * 
 * @author syuki
 */
export default ({ currentAddress, userType, close, open, anchorEl, profilePicturePath }) => {
    
    const [balance, setBalance] = useState();

     async function getUserAccountBalance(){
        const provider = new ethers.providers.Web3Provider(window.ethereum);
        const accountBalance = await provider.getBalance(currentAddress);
        // Fixing the account balance to 4 decimal units.
        setBalance(parseFloat(ethers.utils.formatEther(accountBalance)).toFixed(4));
    }

    useEffect(() => {
        getUserAccountBalance();
    }, [])

    return(
        <Menu
                className="profile-menu"
                anchorEl={anchorEl}
                keepMounted
                disableScrollLock={true}
                PaperProps={{
                    style: {
                        transform: 'translateX(-10px) translateY(60px)',
                        padding: "10px 30px 20px 30px"
                    }
                }}
                open={open}
                onClose={close}
        >
            <div>
                <center>
                    <img className="profile-picture" src={profilePicturePath} alt="profile picture" />
                    <br/>
                    <Button 
                        variant="outlined" 
                        style={{ color: "#03989E", borderColor: "#03989E" }}
                        disabled={true}>
                        {userType}
                    </Button>
                </center>
                <br/>
                <div className="profile-details">
                    <div style={{ paddingBottom: "24px" }}>
                        <h4>Account Address</h4> 
                        <p>{currentAddress}</p>
                    </div>
                    <div>
                        <h4>Account Balance</h4> 
                        {/* fetch user account balance */}
                        <p>{balance} <b>ETH</b></p>
                    </div>
                </div>
            </div>
        </Menu>
    );
};