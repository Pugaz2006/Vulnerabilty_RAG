// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IUniswapV2Pair { function getReserves() external view returns (uint112, uint112, uint32); }

contract FertilizerPricing {
    IUniswapV2Pair public fertilizerUsdcPair;

    constructor(address _pair) { fertilizerUsdcPair = IUniswapV2Pair(_pair); }

    // VULNERABLE: Uses instantaneous reserves. An attacker can crash the AMM ratio,
    // call this function, and buy fertilizer tokens for pennies.
    function getFertilizerPrice() public view returns (uint256) {
        (uint112 reserve0, uint112 reserve1, ) = fertilizerUsdcPair.getReserves();
        require(reserve0 > 0 && reserve1 > 0, "Invalid reserves");
        return (uint256(reserve1) * 1e18) / uint256(reserve0);
    }
}