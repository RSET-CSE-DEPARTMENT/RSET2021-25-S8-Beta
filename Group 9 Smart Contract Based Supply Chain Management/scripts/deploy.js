const path = require("path");
var contracts = [];

async function main() {
  // This is just a convenience check
  if (network.name === "hardhat") {
    console.warn(
      "You are trying to deploy a contract to the Hardhat Network, which" +
        "gets automatically created and destroyed every time. Use the Hardhat" +
        " option '--network localhost'"
    );
  }

  // ethers is available in the global scope
  const [deployer] = await ethers.getSigners();
  console.log(
    "Deploying the contracts with the account:",
    await deployer.getAddress()
  );

  console.log("Account balance:", (await deployer.getBalance()).toString());

  await deployContract("SupplyChainLifecycle");
  await deployContract("Distributor");
  await deployContract("Producer");
  await deployContract("Retailer");
  await deployContract("Users");

  storeDeployedAddresses(contracts);
}

async function deployContract(contractNameString) {
  const contractName = await ethers.getContractFactory(contractNameString);
  const contractDeployable = await contractName.deploy();
  await contractDeployable.deployed();

  const contractInformation = {[contractNameString]: contractDeployable.address};
  contracts.push(contractInformation);

  console.log(contractNameString + " address:", contractDeployable.address);

  // We also save the contract's artifacts and address in the frontend directory to be accessed from there.
  saveFrontendFilesJSON(contractNameString);
}

function saveFrontendFilesJSON(contractNameString) {
  const fs = require("fs");
  const contractsDir = path.join(__dirname, "..", "appfrontend", "src", "contracts");

  if (!fs.existsSync(contractsDir)) {
    fs.mkdirSync(contractsDir);
  }

  const contractArtifact = artifacts.readArtifactSync(contractNameString);

  fs.writeFileSync(
    path.join(contractsDir, contractNameString + ".json"),
    JSON.stringify(contractArtifact, null, 2)
  );
}

function storeDeployedAddresses(contracts){
  const fs = require("fs");
  const contractsDir = path.join(__dirname, "..", "appfrontend", "src", "contracts");

  fs.writeFileSync(
    path.join(contractsDir, "contract-addresses.json"),
    JSON.stringify( contracts, undefined, 2)
  );
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
