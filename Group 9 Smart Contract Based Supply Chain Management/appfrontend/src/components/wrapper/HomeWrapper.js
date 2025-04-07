import React from "react";
import { useLocation } from 'react-router-dom';

import Home from "../Home";

/**
 * Wrapper component for home page to use certain hooks.
 * 
 * @author syuki
 */
const HomeWrapper = props => {
    //Checks for registration status received through navigate() right after
    //new user's successful registration. 
    const location = useLocation();
    
    if(location.state != null && location.state.auth != null) {
        return <Home isSuccessfullyRegistered={location.state.auth} newUserType={location.state.userType} {...props} /> 
    }
    // Not redirecting to "/new-user" right away as state update for existing users is asynchronous, props.isAuthenticated 
    // might not be updated by the time this executes, hence, multiple checks are used in the Home component instead.
    return <Home isSuccessfullyRegistered={null} newUserType={null} {...props} /> 
}

export default HomeWrapper;