const { expect, assert } = require("chai");
const { loadFixture } = require("@nomicfoundation/hardhat-network-helpers");

describe("SupplyChainLifecycle contract deployment", function () {
    // We define a fixture to reuse the same setup in every test. We use
    // loadFixture to run this setup once, snapshot that state, and reset Hardhat
    // Network to that snapshot in every test.
    async function deployContractFixture() {
      const SupplyChainLifecycle = await ethers.getContractFactory("SupplyChainLifecycle");
      const [owner, producer, distributor, retailer] = await ethers.getSigners();
  
      // To deploy our contract, we just have to call SupplyChainLifecycle.deploy() and await
      // for it to be deployed(), which happens once its transaction has been
      // mined.
      const supplyChainLifecycleInstance = await SupplyChainLifecycle.deploy();
      await supplyChainLifecycleInstance.deployed();
  
      return { SupplyChainLifecycle, supplyChainLifecycleInstance, owner, producer, distributor, retailer };
    }

    async function addAProductFixture() {
      const { supplyChainLifecycleInstance, producer, distributor, retailer } = await loadFixture(deployContractFixture);
      await supplyChainLifecycleInstance.addProducer(producer.address);
      await supplyChainLifecycleInstance.connect(producer).produceProduct("Test Product","Test Desc", 12, 1, producer.address);

      return { supplyChainLifecycleInstance, producer, distributor, retailer };
    }

    describe("User additions", function () {
        
        it("Producer should be successfully added.", async function () {
          const { supplyChainLifecycleInstance, producer } = await loadFixture(deployContractFixture);
          await supplyChainLifecycleInstance.addProducer(producer.address);

          assert.equal(await supplyChainLifecycleInstance.connect(producer).isProducer(), true);
          assert.equal(await supplyChainLifecycleInstance.connect(producer).isDistributor(), false);
        });

        it("Distributor should be successfully added.", async function () {
            const { supplyChainLifecycleInstance, distributor } = await loadFixture(deployContractFixture);
            await supplyChainLifecycleInstance.addDistributor(distributor.address);
            
            assert.equal(await supplyChainLifecycleInstance.connect(distributor).isDistributor(), true);
            assert.equal(await supplyChainLifecycleInstance.connect(distributor).isProducer(), false);
          });

        it("Retailer should be successfully added.", async function () {
          const { supplyChainLifecycleInstance, retailer } = await loadFixture(deployContractFixture);
          await supplyChainLifecycleInstance.addRetailer(retailer.address);
          
          assert.equal(await supplyChainLifecycleInstance.connect(retailer).isRetailer(), true);
          assert.equal(await supplyChainLifecycleInstance.connect(retailer).isProducer(), false);
        });
    });
    
    describe("User actions", function () {
        
        it("Producer should be able to add a product to the chain.", async function () {
          const { supplyChainLifecycleInstance, owner, producer } = await loadFixture(deployContractFixture);
          await supplyChainLifecycleInstance.addProducer(producer.address);
          await supplyChainLifecycleInstance.connect(producer).produceProduct("Test Product","Test Desc", 12, 1, producer.address);
          const productDetailsArray = await supplyChainLifecycleInstance.getAllProductDetails();

          assert.equal(await supplyChainLifecycleInstance.connect(producer).isProducer(), true, 'Is not a producer.');
          assert.equal(productDetailsArray.length, 1, 'One product should have been returned.');
          assert.equal(productDetailsArray[0].productQuantity, 1, 'The quantity of the product stored should be 1.');
          assert.equal(productDetailsArray[0].productName, "Test Product", 'The name of the product stored should be - Test Product.');
          assert.equal(productDetailsArray[0].productId, 0, 'The ID of the product stored should be 0.');
          assert.equal(productDetailsArray[0].productStatus, 0, 'The product should be in PRODUCED status.');
        });

        it("Users should be able to fetch product details by ID.", async () => {
          const { supplyChainLifecycleInstance } = await loadFixture(addAProductFixture);
          const productDetails = await supplyChainLifecycleInstance.getProductDetails(0);
          
          assert.equal(productDetails.productQuantity, 1, 'The quantity of the product stored should be 1.');
          assert.equal(productDetails.productName, "Test Product", 'The name of the product stored should be - Test Product.');
          assert.equal(productDetails.productId, 0, 'The ID of the product stored should be 0.');
        });
    
        it("Producer should be able to enable the product for pick up.", async () => {
            const { supplyChainLifecycleInstance, producer } = await loadFixture(addAProductFixture);
            await supplyChainLifecycleInstance.connect(producer).markProductReadyForPickup(0);
            const productDetails = await supplyChainLifecycleInstance.getProductDetails(0);
    
            assert.equal(productDetails.productId, 0, 'The ID of the product stored should be 0.');
            assert.equal(productDetails.productStatus, 1, 'The product should be in READY FOR PICKUP status.');
        });

        it("Only a producer should be able to enable the product for pick up.", async () => {
          const { supplyChainLifecycleInstance, retailer } = await loadFixture(addAProductFixture);
          
          await expect(supplyChainLifecycleInstance.connect(retailer).markProductReadyForPickup(0)).to.be.revertedWith("Not a producer.");
        });
    
        it("Distributor should be able to pick up the product.", async () => {
            const { supplyChainLifecycleInstance, distributor } = await loadFixture(addAProductFixture);
            await supplyChainLifecycleInstance.addDistributor(distributor.address);
            await supplyChainLifecycleInstance.connect(distributor).pickUpProduct(0);
            const productDetails = await supplyChainLifecycleInstance.getProductDetails(0);
    
            assert.equal(productDetails.productId, 0, 'The ID of the product stored should be 0.');
            assert.equal(productDetails.productStatus, 2, 'The product should be in PICKED UP status.');
            assert.equal(productDetails.distributorAddress, distributor.address, 'The product should contain distributor address details.');
        });
    
        it("Distributor should be able to pay the producer.", async () => {
            const { supplyChainLifecycleInstance, distributor } = await loadFixture(addAProductFixture);
            await supplyChainLifecycleInstance.addDistributor(distributor.address);
            await supplyChainLifecycleInstance.connect(distributor).buyProduct(0);
            const productDetails = await supplyChainLifecycleInstance.getProductDetails(0);
    
            assert.equal(productDetails.productId, 0, 'The ID of the product stored should be 0.');
            assert.equal(productDetails.productStatus, 6, 'The product should be in PAID status.');
        });
    
        it("Distributor should be able to ship the product.", async () => {
            const { supplyChainLifecycleInstance, distributor } = await loadFixture(addAProductFixture);
            await supplyChainLifecycleInstance.addDistributor(distributor.address);
            await supplyChainLifecycleInstance.connect(distributor).releaseProductShipment(0);
            const productDetails = await supplyChainLifecycleInstance.getProductDetails(0);
    
            assert.equal(productDetails.productId, 0, 'The ID of the product stored should be 0.');
            assert.equal(productDetails.productStatus, 3, 'The product should be in SHIPMENT RELEASED status.');
        });
    
        it("Retailer should be able to receive the shipped product.", async () => {
            const { supplyChainLifecycleInstance, retailer } = await loadFixture(addAProductFixture);
            await supplyChainLifecycleInstance.addRetailer(retailer.address);
            await supplyChainLifecycleInstance.connect(retailer).receiveProductShipment(0);
            const productDetails = await supplyChainLifecycleInstance.getProductDetails(0);
    
            assert.equal(productDetails.productId, 0, 'The ID of the product stored should be 0.');
            assert.equal(productDetails.productStatus, 4, 'The product should be in SHIPMENT RECEIVED status.');
            assert.equal(productDetails.retailerAddresses, retailer.address, 'The product should contain retailer address details.');
        });
    
        it("Retailer should be able to pay the distributor.", async () => {
            const { supplyChainLifecycleInstance, retailer } = await loadFixture(addAProductFixture);
            await supplyChainLifecycleInstance.addRetailer(retailer.address);
            await supplyChainLifecycleInstance.connect(retailer).buyProduct(0);
    
            const productDetails = await supplyChainLifecycleInstance.getProductDetails(0);
    
            assert.equal(productDetails.productId, 0, 'The ID of the product stored should be 0.');
            assert.equal(productDetails.productStatus, 6, 'The product should be in PAID status.');
        });
    
        it("Retailer should be able to put the product up for sale.", async () => {
            const { supplyChainLifecycleInstance, retailer } = await loadFixture(addAProductFixture);
            await supplyChainLifecycleInstance.addRetailer(retailer.address);
            await supplyChainLifecycleInstance.connect(retailer).markProductReadyForSale(0);
            const productDetails = await supplyChainLifecycleInstance.getProductDetails(0);
    
            assert.equal(productDetails.productId, 0, 'The ID of the product stored should be 0.');
            assert.equal(productDetails.productStatus, 5, 'The product should be in READY FOR SALE status.');
        });
    
        it("Retailer should be able to sell the product to the consumer.", async () => {
            const { supplyChainLifecycleInstance, retailer } = await loadFixture(addAProductFixture);
            await supplyChainLifecycleInstance.addRetailer(retailer.address);
            await supplyChainLifecycleInstance.connect(retailer).sellProductToConsumer(0);
            const productDetails = await supplyChainLifecycleInstance.getProductDetails(0);
    
            assert.equal(productDetails.productId, 0, 'The ID of the product stored should be 0.');
            assert.equal(productDetails.productStatus, 7, 'The product should be in SOLD status.');
        });
    });  
});
