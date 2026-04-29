// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IERC20 { 
    function balanceOf(address account) external view returns (uint256); 
    function transfer(address to, uint256 amount) external returns (bool);
}

contract CropInsurancePool {
    IERC20 public usdcToken;
    mapping(address => uint256) public userShares;
    uint256 public totalShares;

    constructor(address _token) { usdcToken = IERC20(_token); }

    function claimPayout() external {
        uint256 shares = userShares[msg.sender];
        require(shares > 0, "No shares");

        // VULNERABLE: Uses raw token balance. Attacker flash loans and directly transfers 
        // USDC to this contract to inflate 'currentPoolFunds' for one block.
        uint256 currentPoolFunds = usdcToken.balanceOf(address(this));
        uint256 payout = (currentPoolFunds * shares) / totalShares;

        userShares[msg.sender] = 0;
        totalShares -= shares;

        usdcToken.transfer(msg.sender, payout);
    }
}