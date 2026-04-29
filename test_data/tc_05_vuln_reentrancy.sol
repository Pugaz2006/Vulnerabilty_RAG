// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract UnsafeBank {
    mapping(address => uint256) public balances;

    function withdraw() external {
        uint256 amount = balances[msg.sender];
        require(amount > 0, "No balance");
        
        // VULNERABLE: Control handed to attacker before state is updated
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");

        balances[msg.sender] = 0;
    }
}