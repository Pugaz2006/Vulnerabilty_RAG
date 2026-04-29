// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

contract RebasingTokenVault {
    IERC20 public token;
    uint256 public totalShares;
    uint256 public cachedTotalTokens; // 🔴 Flawed architectural choice
    mapping(address => uint256) public shares;

    constructor(address _token) {
        token = IERC20(_token);
    }

    // 🔴 VULNERABLE FUNCTION
    // Relies on a cached balance instead of the actual current balance
    function deposit(uint256 amount) external {
        uint256 sharesToMint;

        if (totalShares == 0) {
            sharesToMint = amount;
        } else {
            // BUG: If the token rebases negatively (supply shrinks), cachedTotalTokens 
            // is now larger than the actual balance. New depositors get fewer shares 
            // than they deserve, and the vault becomes insolvent.
            sharesToMint = (amount * totalShares) / cachedTotalTokens;
        }

        token.transferFrom(msg.sender, address(this), amount);
        
        shares[msg.sender] += sharesToMint;
        totalShares += sharesToMint;
        cachedTotalTokens += amount; // Assumes 1:1 sync with token contract
    }
}