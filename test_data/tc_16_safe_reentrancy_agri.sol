// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IERC777 { function send(address recipient, uint256 amount, bytes calldata data) external; }

contract SafeGrainSilo {
    IERC777 public grainToken;
    mapping(address => uint256) public storedGrain;
    bool private locked;

    modifier nonReentrant() {
        require(!locked, "No re-entrancy");
        locked = true;
        _;
        locked = false;
    }

    constructor(address _token) { grainToken = IERC777(_token); }

    function withdrawGrain() external nonReentrant {
        uint256 amount = storedGrain[msg.sender];
        require(amount > 0, "No grain in silo");

        // SAFE: Even though state is updated late, the mutex lock prevents the attack
        grainToken.send(msg.sender, amount, "");
        storedGrain[msg.sender] = 0;
    }
}