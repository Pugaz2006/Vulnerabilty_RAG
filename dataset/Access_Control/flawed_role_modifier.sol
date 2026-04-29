// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract FlawedRoleModifier {
    mapping(address => bool) public isAdmin;
    uint256 public treasuryFee;

    constructor() {
        isAdmin[msg.sender] = true;
        treasuryFee = 10;
    }

    // 🔴 VULNERABLE MODIFIER
    // Logical error: Requires the sender to NOT be an admin, or relies on a default zero-state
    modifier onlyAdmin() {
        // BUG: Developer accidentally used != instead of ==
        // Now, anyone who is NOT an admin can pass this check!
        require(!isAdmin[msg.sender], "Access Denied: Admins Only");
        _;
    }

    // 🔴 VULNERABLE FUNCTION
    // Protected by a broken modifier
    function setTreasuryFee(uint256 newFee) external onlyAdmin {
        require(newFee <= 100, "Fee too high");
        treasuryFee = newFee;
    }

    // Another variation: Missing the modifier entirely
    function grantAdmin(address newAdmin) external {
        // BUG: The developer forgot to add 'onlyAdmin' here!
        // Anyone can make themselves an admin.
        isAdmin[newAdmin] = true;
    }
}