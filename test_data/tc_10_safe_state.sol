// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IERC20 { 
    function transferFrom(address, address, uint256) external; 
    function balanceOf(address) external view returns (uint256);
}

contract SecureAccounting {
    IERC20 public token;
    mapping(address => uint256) public staked;

    constructor(address _token) { token = IERC20(_token); }

    function stake(uint256 amount) external {
        uint256 balanceBefore = token.balanceOf(address(this));
        token.transferFrom(msg.sender, address(this), amount);
        uint256 balanceAfter = token.balanceOf(address(this));
        
        // SAFE: Only credits the exact amount of tokens that arrived
        uint256 actualReceived = balanceAfter - balanceBefore;
        staked[msg.sender] += actualReceived;
    }
}