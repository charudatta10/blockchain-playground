pragma solidity ^0.4.18;

contract RecordHandler {
    address creator;
    string record;

    event Record (string indexed record);
    
    function RecordHandler() public {
        creator = msg.sender;
    }
    
    function setRecord(string _record) public {
        record = _record;
        Record(_record);
    }
    
    function getRecord() public returns (string) {
        return record;
    }
}