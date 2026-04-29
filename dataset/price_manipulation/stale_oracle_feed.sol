// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IAggregatorV3 {
    function latestRoundData() external view returns (
        uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound
    );
}

contract StaleOracleFeed {
    IAggregatorV3 public priceFeed;
    mapping(address => uint256) public balances;

    constructor(address _priceFeed) {
        priceFeed = IAggregatorV3(_priceFeed);
    }

    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }

    // 🔴 VULNERABLE FUNCTION
    // Fails to validate if the price is stale
    function borrowAgainstCollateral(uint256 borrowAmount) external {
        // Only extracts the price, ignores timestamps and round IDs
        (, int256 price, , , ) = priceFeed.latestRoundData();
        require(price > 0, "Invalid price");

        uint256 collateralValue = balances[msg.sender] * uint256(price);
        
        // If the oracle hasn't updated in 24 hours, 'price' is stale.
        // The attacker borrows far more than their collateral is currently worth.
        require(collateralValue >= borrowAmount, "Insufficient collateral");

        // Proceed with token transfer...
    }
}