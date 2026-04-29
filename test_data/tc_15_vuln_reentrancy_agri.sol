// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IERC777 { function send(address recipient, uint256 amount, bytes calldata data) external; }

contract GrainSilo {
    IERC777 public grainToken;
    mapping(address => uint256) public storedGrain;

    constructor(address _token) { grainToken = IERC777(_token); }

    function withdrawGrain() external {
        uint256 amount = storedGrain[msg.sender];
        require(amount > 0, "No grain in silo");

        // VULNERABLE: External hook triggered before state update
        grainToken.send(msg.sender, amount, "");

        storedGrain[msg.sender] = 0;
    }
}