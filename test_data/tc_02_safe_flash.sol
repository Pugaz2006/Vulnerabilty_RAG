// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IChainlinkOracle { function latestRoundData() external view returns (uint80, int256, uint256, uint256, uint80); }

contract SafeOracleLending {
    IChainlinkOracle public priceFeed;
    mapping(address => uint256) public collateral;

    constructor(address _feed) { priceFeed = IChainlinkOracle(_feed); }

    function getBorrowingPower(address user) public view returns (uint256) {
        (, int256 price, , , ) = priceFeed.latestRoundData();
        require(price > 0, "Invalid oracle price");
        // SAFE: A flash loan cannot alter the Chainlink aggregated price in one block
        return (collateral[user] * uint256(price)) / 1e18;
    }
}