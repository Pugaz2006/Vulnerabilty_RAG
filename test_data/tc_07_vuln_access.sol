// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract TxOriginVault {
    address public owner;
    constructor() { owner = msg.sender; }

    function emergencyDrain() external {
        // VULNERABLE: If owner is tricked into calling a malicious contract, tx.origin remains the owner
        require(tx.origin == owner, "Not authorized");
        payable(msg.sender).transfer(address(this).balance);
    }
}