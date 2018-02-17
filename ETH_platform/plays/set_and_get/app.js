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
                // console.log(newContractInstance);
                // myContract = newContractInstance;
                newContractInstance.setProvider(web3.currentProvider);
                newContractInstance.methods.setRecord("Hello Word").send({
                    from: web3.eth.defaultAccount,
                    gas: 1500000,
                    gasPrice: '100'
                }).on('transactionHash', function(hash){
                    console.log('hash' + hash);
                    // web3.eth.getTransactionReceipt(hash, function(err, receipt) {
                    //     console.log(receipt);
                    //      // newContractInstance.events.Record(function(err, result) {
                    //     //     console.log(result);
                    //     // });
                    //     // web3.eth.getTransaction(result, function(err, result) {
                    //     //     console.log(result);
                    //     //     var recordEvent = result.events;
                    //     //     console.log(recordEvent);
                    //     // });
                    // });
                }).on('confirmation', function(number, receipt) {
                    console.log(number);
                    console.log(receipt);
                }).on('error', console.error);

        });
    } else {
        console.log(err);
    }
});