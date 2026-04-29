// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SingleSourceOracle {
    address public oracleAdmin;
    uint256 public currentAssetPrice;
    mapping(address => uint256) public userDeposits;

    constructor() {
        oracleAdmin = msg.sender;
        currentAssetPrice = 1000; // Default starting price
    }

    // 🔴 VULNERABLE FUNCTION
    // A single point of failure. No TWAP, no multi-sig, no aggregator.
    function updatePrice(uint256 newPrice) external {
        require(msg.sender == oracleAdmin, "Only Oracle Admin can update price");
        currentAssetPrice = newPrice;
    }

    function liquidate(address user) external {
        uint256 collateralValue = userDeposits[user] * currentAssetPrice;
        
        // If the oracleAdmin key is compromised, the attacker sets currentAssetPrice to 0.
        // Suddenly, EVERY user becomes liquidatable, and the attacker steals all collateral.
        require(collateralValue < 100, "User is safe"); 
        
        // ... liquidation logic executes here
    }
}