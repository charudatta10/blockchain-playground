var Web3 = require('web3');
const fs = require("fs");
const solc = require('solc');
var web3 = new Web3(new Web3.providers.HttpProvider("http://localhost:8545"));

web3.eth.getAccounts(function(err, result){
    if (!err) {
        web3.eth.defaultAccount = result[0];

        let source = fs.readFileSync('./recordHandler.sol', 'utf8');
        let compiledContract = solc.compile(source, 1);

        let abi = compiledContract.contracts[':RecordHandler'].interface;
        let bytecode = compiledContract.contracts[':RecordHandler'].bytecode;
        let myContract = new web3.eth.Contract(JSON.parse(abi), web3.eth.defaultAccount);

        myContract.deploy({data: bytecode}).send({
            from: web3.eth.defaultAccount, 
            gas: 1500000,
            gasPrice: '100'}).then(function(newContractInstance){

                newContractInstance.methods.setRecord("Hello Word").send({
                    from: web3.eth.defaultAccount,
                    gas: 1500000,
                    gasPrice: '100'
                }).on('transactionHash', function(hash){
                    console.log('hash' + hash);
                }).on('confirmation', function(number, receipt) {

                    newContractInstance.methods.getRecord().call().then(function(result){
                        console.log(result);
                    });
                    
                }).on('error', console.error);

        });
    } else {
        console.log(err);
    }
});