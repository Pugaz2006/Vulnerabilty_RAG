// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IUniswapV2Pair { function getReserves() external view returns (uint112, uint112, uint32); }

contract SpotPriceLending {
    IUniswapV2Pair public pair;
    mapping(address => uint256) public collateral;

    constructor(address _pair) { pair = IUniswapV2Pair(_pair); }

    function getBorrowingPower(address user) public view returns (uint256) {
        (uint112 reserve0, uint112 reserve1, ) = pair.getReserves();
        // VULNERABLE: Spot price manipulation via flash loan changes this ratio instantly
        return (collateral[user] * reserve0) / reserve1;
    }
}