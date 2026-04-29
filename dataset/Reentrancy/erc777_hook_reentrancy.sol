// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IERC777 {
    function send(address recipient, uint256 amount, bytes calldata data) external;
}

contract ERC777HookReentrancy {
    IERC777 public advancedToken;
    mapping(address => uint256) public deposits;

    constructor(address _token) {
        advancedToken = IERC777(_token);
    }

    function deposit(uint256 amount) external {
        deposits[msg.sender] += amount;
    }

    // 🔴 VULNERABLE FUNCTION
    // Assumes token transfers don't hand over execution control
    function withdrawToken() external {
        uint256 amount = deposits[msg.sender];
        require(amount > 0, "No deposit");

        // The ERC777 token will call the attacker's 'tokensReceived' hook here!
        // The attacker can re-enter withdrawToken() infinitely.
        advancedToken.send(msg.sender, amount, "");

        // State update happens after the token transfer
        deposits[msg.sender] = 0;
    }
}