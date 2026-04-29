// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IERC20 {
    function balanceOf(address account) external view returns (uint256);
    function totalSupply() external view returns (uint256);
}

contract LPTokenPricingFlaw {
    IERC20 public lpToken;
    IERC20 public underlyingToken;

    constructor(address _lpToken, address _underlyingToken) {
        lpToken = IERC20(_lpToken);
        underlyingToken = IERC20(_underlyingToken);
    }

    // 🔴 VULNERABLE FUNCTION
    // Calculates LP price using easily manipulatable spot balances
    function getLPPrice() public view returns (uint256) {
        uint256 totalUnderlying = underlyingToken.balanceOf(address(lpToken));
        uint256 totalLP = lpToken.totalSupply();
        
        // Attacker flash-loans underlyingToken, sends it directly to lpToken address.
        // totalUnderlying skyrockets, making the return value massive.
        return totalUnderlying / totalLP; 
    }

    function borrowWithLP(uint256 lpAmount) external {
        uint256 lpValue = lpAmount * getLPPrice();
        
        // Attacker uses the artificially inflated lpValue to drain the contract
        // ... lending logic executes here
    }
}