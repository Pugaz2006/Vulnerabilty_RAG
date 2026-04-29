// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Mock interface for TWAP Oracle
interface ITWAPOracle { function consult(address token, uint amountIn) external view returns (uint amountOut); }

contract SafeFertilizerPricing {
    ITWAPOracle public twapOracle;
    address public fertilizerToken;

    constructor(address _oracle, address _token) { 
        twapOracle = ITWAPOracle(_oracle); 
        fertilizerToken = _token;
    }

    // SAFE: Reads from a Time-Weighted Average Price oracle.
    function getFertilizerPrice() public view returns (uint256) {
        return twapOracle.consult(fertilizerToken, 1e18);
    }
}