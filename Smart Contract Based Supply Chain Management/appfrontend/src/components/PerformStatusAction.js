import React from "react"; 

import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogActions from '@mui/material/DialogActions';
import Grid from "@mui/material/Grid";

import {STATUS_ACTIONS} from './enum/ProductStatusEnum';

import "../css/PopUpModal.css";

/**
 * Component to update the status of a batch by interacting with the contracts. 
 * Takes product ID and the action to be performed as input props.
 * 
 * @author syuki
 */
export default class PerformStatusAction extends React.Component {

    getActionSpecificMethod(action){
        let method = null;
        if(action != null && this.props.contractName != null){
            switch(action) {
                case STATUS_ACTIONS[0]:
                    method = this.props.contractName["markProductReadyForPickup"];
                    break;
                case STATUS_ACTIONS[1]:
                    method = this.props.contractName["pickUpProduct"];
                    break;
                case STATUS_ACTIONS[2]:
                    method = this.props.contractName["releaseProductShipment"];
                    break;
                case STATUS_ACTIONS[3]:
                    method = this.props.contractName["receiveProductShipment"];
                    break;
                case STATUS_ACTIONS[4]:
                    method = this.props.contractName["markProductReadyForSale"];
                    break;
                case STATUS_ACTIONS[5]:
                    method = this.props.contractName["buyProduct"];
                    break;
                case STATUS_ACTIONS[6]:
                    method = this.props.contractName["sellProductToConsumer"];
                    break;
            }
        }
        return method;
    }

    confirmAction(){
        this.props.showLoaderScreen();
        const contractMethod = this.getActionSpecificMethod(this.props.action);
        if(contractMethod != null){
            contractMethod(
                this.props.productId
            )
            .then((receipt) => {
                this.props.setTransactionSuccess(true);
                console.log(receipt);
                this.props.hideLoaderScreen();
                this.props.closePopup();
            })
            .catch((error) => {
                this.props.setTransactionSuccess(false);
                console.log(error);
                this.props.hideLoaderScreen();
                this.props.closePopup();
            });
        }
        else {
            this.props.setTransactionSuccess(false);
            this.props.hideLoaderScreen();
            this.props.closePopup();
        }
    }

    toCamelCase(str) {
        return str.replace(
            /\w\S*/g,
            function(txt) {
              return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
            }
        );
    }

    render() {
        return(
            <Dialog
            open={this.props.open}
            aria-labelledby="scroll-dialog-title"
            aria-describedby="scroll-dialog-description"
            fullWidth
            onClose={this.props.closePopup}
            scroll="paper" 
            className="popup-modal">
                <div style={{ paddingBottom: "20px"}}>
                    <center>
                        <DialogTitle id="scroll-dialog-title">Confirm {this.toCamelCase(this.props.action)}?</DialogTitle>
                        <DialogActions>
                            <Grid container color="secondary" className="form-grid"  justifyContent="center" >
                                <Grid item xs={3}>
                                    <Button variant="outlined" className="nf-button" color="primary" onClick={this.props.closePopup}>Close</Button>
                                </Grid> 
                                <Grid item xs={3}>
                                    <Button variant="contained" className="nf-button" color="primary" onClick={this.confirmAction.bind(this)}>Confirm</Button>
                                </Grid>
                            </Grid>
                        </DialogActions>
                    </center>
                </div>
            </Dialog>
        )
    }
};