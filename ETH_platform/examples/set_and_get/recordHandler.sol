pragma solidity ^0.4.20;


contract RecordHandler {

    address creator;
    string record;

    // !!!don't add indexed argument on string and bytes type
    event Record (string record); 
    
    function RecordHandler() public {
        creator = msg.sender;
    }
    
    function setRecord(string _record) public {
        record = _record;
        Record(record);
    }

    function getRecord() public returns (string) {
        return record;
    }
}