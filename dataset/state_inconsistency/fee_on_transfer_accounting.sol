// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
}

contract FeeOnTransferAccounting {
    IERC20 public token;
    mapping(address => uint256) public balances;

    constructor(address _token) {
        token = IERC20(_token);
    }

    // 🔴 VULNERABLE FUNCTION
    // Fails to check balance before and after the transfer
    function deposit(uint256 amount) external {
        // If 'token' takes a 2% fee, the contract only receives 98% of 'amount'
        token.transferFrom(msg.sender, address(this), amount);
        
        // BUG: The contract records the full 100% in the user's ledger
        balances[msg.sender] += amount;
    }

    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        balances[msg.sender] -= amount;
        
        // The user withdraws more than they actually deposited, draining the pool
        token.transfer(msg.sender, amount);
    }
}