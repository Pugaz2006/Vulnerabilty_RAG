// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract OrphanedStateVariable {
    mapping(address => uint256) public userBalances;
    uint256 public totalDeposits; // Global tracker

    function deposit() external payable {
        userBalances[msg.sender] += msg.value;
        totalDeposits += msg.value; // Kept in sync
    }

    function withdraw(uint256 amount) external {
        require(userBalances[msg.sender] >= amount, "Insufficient balance");
        userBalances[msg.sender] -= amount;
        totalDeposits -= amount; // Kept in sync
        payable(msg.sender).transfer(amount);
    }

    // 🔴 VULNERABLE FUNCTION
    // Forgets to update the global state variable
    function emergencyWithdraw() external {
        uint256 amountToRefund = userBalances[msg.sender];
        require(amountToRefund > 0, "No funds to withdraw");

        // User's balance is zeroed out
        userBalances[msg.sender] = 0;
        
        // BUG: 'totalDeposits -= amountToRefund' is missing!
        // The contract now believes it holds more ETH than it actually does.
        
        payable(msg.sender).transfer(amountToRefund);
    }
}