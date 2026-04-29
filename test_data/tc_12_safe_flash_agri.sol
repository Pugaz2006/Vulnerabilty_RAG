// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IERC20 { 
    function transfer(address to, uint256 amount) external returns (bool);
}

contract SafeCropInsurancePool {
    IERC20 public usdcToken;
    mapping(address => uint256) public userShares;
    uint256 public totalShares;
    uint256 public totalDepositedFunds; // Internal ledger

    constructor(address _token) { usdcToken = IERC20(_token); }

    function claimPayout() external {
        uint256 shares = userShares[msg.sender];
        require(shares > 0, "No shares");

        // SAFE: Uses strict internal accounting. Direct transfers do nothing.
        uint256 payout = (totalDepositedFunds * shares) / totalShares;

        userShares[msg.sender] = 0;
        totalShares -= shares;
        totalDepositedFunds -= payout;

        usdcToken.transfer(msg.sender, payout);
    }
}