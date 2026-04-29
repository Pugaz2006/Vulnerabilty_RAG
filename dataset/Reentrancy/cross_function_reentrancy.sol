// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract CrossFunctionReentrancy {
    mapping(address => uint256) public userBalances;
    bool internal locked;

    modifier noReentrant() {
        require(!locked, "No re-entrancy");
        locked = true;
        _;
        locked = false;
    }

    function deposit() external payable {
        userBalances[msg.sender] += msg.value;
    }

    // 🔴 VULNERABLE ARCHITECTURE
    // Uses a reentrancy guard, but state is updated AFTER the call.
    function withdraw(uint256 amount) external noReentrant {
        require(userBalances[msg.sender] >= amount, "Insufficient balance");

        // External call hands control to the attacker's fallback function
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");

        // State update happens too late!
        userBalances[msg.sender] -= amount;
    }

    // 🔴 THE EXPLOIT VECTOR
    // Attacker re-enters HERE during the withdraw() external call.
    // They transfer the funds to a second wallet before the balance is decremented.
    function transfer(address to, uint256 amount) external {
        require(userBalances[msg.sender] >= amount, "Insufficient balance");
        userBalances[msg.sender] -= amount;
        userBalances[to] += amount;
    }
}