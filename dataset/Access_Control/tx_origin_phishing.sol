// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract TxOriginPhishing {
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    // 🔴 VULNERABLE FUNCTION
    // Uses tx.origin instead of msg.sender for authentication
    function transferOwnership(address newOwner) external {
        // If the real owner interacts with a hacker's contract, 
        // the hacker's contract can call this function.
        // tx.origin will still evaluate to the real owner, bypassing the check!
        require(tx.origin == owner, "Not authorized");
        
        owner = newOwner;
    }

    function withdrawAll(address payable recipient) external {
        require(msg.sender == owner, "Only owner");
        recipient.transfer(address(this).balance);
    }
}