// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract UnprotectedDelegatecall {
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    // 🔴 VULNERABLE FUNCTION
    // Allows any user to execute arbitrary logic within this contract's state
    function executeExternalLogic(address target, bytes memory data) external {
        // The attacker deploys a contract that contains a function overriding the owner:
        // function hijack() { owner = msg.sender; }
        // The attacker passes their contract address and the encoded 'hijack()' data here.
        
        (bool success, ) = target.delegatecall(data);
        
        require(success, "Delegatecall failed");
    }

    function destroyContract() external {
        require(msg.sender == owner, "Only owner can destroy");
        selfdestruct(payable(owner));
    }
}