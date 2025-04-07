import React from "react"; 

import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import DialogActions from '@mui/material/DialogActions';
import Grid from "@mui/material/Grid";
import InputAdornment from '@mui/material/InputAdornment';
import TextField from '@mui/material/TextField';

import "../css/PopUpModal.css";

/**
 * Component to add new batch details to the blockchain by interacting with the contracts.
 * Takes these details as input from the user.
 * 
 * @author syuki
 */
export default class ProductBatchForm extends React.Component {

    state = { 
        prodName: null,
        prodDesc: null,
        prodPrice: null,
        prodQty: null,
        currency: "₹",
        unit: "Kg"
    };

    addZeroesForDecimals(productPrice){
        return productPrice * 100;
    }

    createProductBatch(event){
        //Prevents reloading of the entire page after submission.
        event.preventDefault();
        this.props.showLoaderScreen();
        let formData = this.state;
        let updatedPrice = this.addZeroesForDecimals(formData.prodPrice);
        this.props.contractName.produceProduct(
            formData.prodName,
            formData.prodDesc,
            parseInt(updatedPrice),
            parseInt(formData.prodQty),
            this.props.currentAddress
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

    handleInput(input){
        const name = input.target.name;
        const newValue = input.target.value;
        this.setState({ [name]: newValue });
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
                <center>
                    <DialogTitle id="scroll-dialog-title">Enter Batch Details</DialogTitle>
                </center>
                <form onSubmit={(event) => this.createProductBatch(event)} className="form-grid"> 
                    <DialogContent dividers={true}>
                        <DialogContentText
                            id="scroll-dialog-description"
                            ref={null}
                            tabIndex={-1}
                        >
                            <Grid 
                                container 
                                color="secondary" 
                                justifyContent="center" 
                                direction={'column'} 
                                spacing={2}
                            >
                                <Grid item xs={12} style={{ color: "red"}}>
                                    <TextField 
                                        required 
                                        fullWidth 
                                        name="prodName"
                                        onChange={(event) => this.handleInput(event)}
                                        InputLabelProps={{
                                            style: {
                                            color: 'grey'
                                            } 
                                        }}
                                        variant="outlined" 
                                        label="Product Name" />
                                </Grid>
                                <Grid item xs={12}>
                                    <TextField 
                                        required 
                                        fullWidth 
                                        multiline
                                        name="prodDesc"
                                        onChange={(event) => this.handleInput(event)}
                                        InputLabelProps={{
                                            style: {
                                                color: 'grey'
                                            } 
                                        }}
                                        variant="outlined" 
                                        label="Product Description" />
                                </Grid>
                            </Grid>
                            <br />
                            <Grid 
                                container 
                                color="secondary" 
                                className="form-grid" 
                                // spacing={14}
                                justifyContent="center">
                                <Grid item xs={6}>
                                    <TextField 
                                        required 
                                        type="number"
                                        name="prodPrice"
                                        onChange={(event) => this.handleInput(event)}
                                        InputLabelProps={{
                                            style: {
                                                color: 'grey'
                                            } 
                                        }}
                                        inputProps={{
                                            min: 0.01,
                                            step: 0.01,
                                          }}
                                        InputProps={{
                                            endAdornment: (
                                                <InputAdornment position="end"> 
                                                    <div style={{ color: "grey"}}>₹</div>
                                                </InputAdornment>),
                                        }}
                                        variant="outlined" 
                                        label="Product Price" />
                                </Grid>
                                <Grid item xs={6}>
                                    <TextField 
                                        required 
                                        name="prodQty"
                                        onChange={(event) => this.handleInput(event)}
                                        type="number"
                                        InputLabelProps={{
                                            min: 1,
                                            pattern: "[0-9]*",
                                            style: {
                                                color: 'grey'
                                            } 
                                        }}
                                        InputProps={{
                                            endAdornment: (
                                                <InputAdornment position="end"> 
                                                    <div style={{ color: "grey"}}>Kg</div>
                                                </InputAdornment>),
                                        }}
                                        variant="outlined" 
                                        label="Product Quantity" />
                                </Grid>
                            </Grid>
                        </DialogContentText>
                    </DialogContent>
                    <center>
                        <div style={{ paddingBottom: "10px", paddingTop: "10px"}}>
                            <DialogActions>
                                <Grid 
                                    container 
                                    color="secondary" 
                                    className="form-grid"  
                                    justifyContent="center">
                                    <Grid item xs={3}>
                                        <Button 
                                            variant="outlined" 
                                            className="nf-button" 
                                            color="primary" 
                                            onClick={this.props.closePopup}>Close</Button>
                                    </Grid> 
                                    <Grid item xs={3}>
                                        <Button 
                                            variant="contained" 
                                            className="nf-button" 
                                            color="primary" 
                                            type="submit">Produce</Button>
                                    </Grid>
                                </Grid>
                            </DialogActions>
                        </div>
                    </center>
                </form>
            </Dialog>
        )
    }
};