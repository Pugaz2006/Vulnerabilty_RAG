// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IERC20 { function transferFrom(address, address, uint256) external; }

contract FlawedAccounting {
    IERC20 public token;
    mapping(address => uint256) public staked;

    constructor(address _token) { token = IERC20(_token); }

    function stake(uint256 amount) external {
        token.transferFrom(msg.sender, address(this), amount);
        // VULNERABLE: If token burns 2% on transfer, the contract records more than it actually holds
        staked[msg.sender] += amount; 
    }
}