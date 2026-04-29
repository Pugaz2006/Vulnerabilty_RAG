// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract UninitializedProxy {
    address public owner;
    uint256 public totalFunds;
    
    // 🔴 VULNERABLE FUNCTION
    // Missing the 'initializer' modifier or boolean check!
    function initialize() external {
        // Anyone can call this at any time to hijack the contract
        owner = msg.sender;
    }

    function deposit() external payable {
        totalFunds += msg.value;
    }

    function emergencyWithdraw() external {
        require(msg.sender == owner, "Only owner can withdraw");
        
        // The attacker hijacked the owner variable, so this succeeds.
        payable(owner).transfer(address(this).balance);
    }
}