pragma solidity ^0.8.19; 

import {FunctionsClient} from "@chainlink/contracts/src/v0.8/functions/v1_0_0/FunctionsClient.sol";
import {ConfirmedOwner} from "@chainlink/contracts/src/v0.8/shared/access/ConfirmedOwner.sol";
import {Strings} from "@openzeppelin/contracts/utils/Strings.sol"; // OpenZeppelin for string utilities

contract HeartDiseaseOracle is FunctionsClient, ConfirmedOwner {
    using Strings for uint256;

    bytes32 public s_lastRequestId; 
    string public s_lastPredictionResult; 
    address public s_lastRequester; 
    bool public s_predictionStored; 

    bytes33 s_donId; 
    uint64 s_subscriptionId; 
    uint32 s_callbackGasLimit;

    event PredictionStored(address indexed requester, string result, bytes32 requestId); 
    event RequestSent(bytes32 indexed requestId);
    event RequestFulfilled(bytes32 indexed requestId, string result); 

    constructor(address router, bytes32 donId, uint64 subscriptionId)
        FunctionsClient(router) 
        ConfirmedOwner(msg.sender) 
    {
        s_donId = donId;
        s_subscriptionId = subscriptionId;
        s_callbackGasLimit = 300_000; 
    }

    function requestPredictionProcessing(string calldata prediction) external onlyOwner returns (bytes32 requestId) {
       
    }

    function fulfillRequest(
        bytes32 requestId,
        bytes memory response,
        bytes memory err
    ) internal override {
        // Handles the response or error from the Chainlink Functions execution.
        // Decodes the response and stores it in s_lastPredictionResult.
        // Sets s_predictionStored to true on success.
        // Emits PredictionStored or RequestFulfilled events.
    }


    function getLastPredictionResult() public view returns (string memory) {
        // Returns the value of s_lastPredictionResult.
    }

    
    function hasPredictionStored() public view returns (bool) {
        // Returns the value of s_predictionStored.
    }
}
