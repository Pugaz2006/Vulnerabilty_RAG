// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MsgSenderVault {
    address public owner;
    constructor() { owner = msg.sender; }

    function emergencyDrain() external {
        // SAFE: Authentication is bound to the exact caller
        require(msg.sender == owner, "Not authorized");
        payable(msg.sender).transfer(address(this).balance);
    }
}