// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract InconsistentArrayMapping {
    address[] public activeUsers;
    mapping(address => uint256) public userIndex;
    mapping(address => bool) public isUserActive;

    function addUser() external {
        require(!isUserActive[msg.sender], "Already active");
        
        activeUsers.push(msg.sender);
        userIndex[msg.sender] = activeUsers.length - 1;
        isUserActive[msg.sender] = true;
    }

    // 🔴 VULNERABLE FUNCTION
    // State desynchronization between array and mapping
    function removeUser() external {
        require(isUserActive[msg.sender], "Not active");

        uint256 indexToRemove = userIndex[msg.sender];
        address lastUser = activeUsers[activeUsers.length - 1];

        // Swap the last user into the slot of the user being removed
        activeUsers[indexToRemove] = lastUser;
        
        // Remove the last element
        activeUsers.pop();

        // BUG: We moved 'lastUser' to a new index, but we forgot to update their mapping!
        // userIndex[lastUser] = indexToRemove; <-- MISSING

        isUserActive[msg.sender] = false;
        userIndex[msg.sender] = 0; // State is now corrupted for 'lastUser'
    }
}