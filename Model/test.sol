// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Minimal interfaces for compilation
interface IUniswapV2Pair {
    function getReserves() external view returns (uint112 reserve0, uint112 reserve1, uint32 blockTimestampLast);
}

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

contract VulnerableVault {
    IERC20 public rewardStablecoin;
    IERC20 public farmToken;
    IUniswapV2Pair public ammOraclePair; 
    
    mapping(address => uint256) public userDeposits;

    constructor(address _rewardToken, address _farmToken, address _ammOraclePair) {
        rewardStablecoin = IERC20(_rewardToken);
        farmToken = IERC20(_farmToken);
        ammOraclePair = IUniswapV2Pair(_ammOraclePair);
    }

    // 1. Farmer deposits their tokens into the vault
    function depositYield(uint256 amount) external {
        require(amount > 0, "Cannot deposit 0");
        farmToken.transferFrom(msg.sender, address(this), amount);
        userDeposits[msg.sender] += amount;
    }

    // 2. THE ZERO-DAY VULNERABILITY: Spot Price Calculation
    function calculateReward(uint256 depositedAmount) public view returns (uint256) {
        // Reads instantaneous liquidity from the AMM
        (uint112 reserveUSD, uint112 reserveFarmToken, ) = ammOraclePair.getReserves();
        
        // Spot Price = USD in pool / Farm Tokens in pool
        // Highly vulnerable to Flash Loan manipulation in the same transaction block!
        uint256 spotPrice = uint256(reserveUSD) / uint256(reserveFarmToken);
        
        return depositedAmount * spotPrice;
    }

    // 3. Farmer claims their stablecoin reward
    function claimReward() external {
        uint256 depositedAmount = userDeposits[msg.sender];
        require(depositedAmount > 0, "No deposited tokens");

        // NOTE: The developer correctly updates state BEFORE the transfer.
        // This defeats Slither and SmartInv because it prevents Reentrancy.
        userDeposits[msg.sender] = 0; 
        
        uint256 finalReward = calculateReward(depositedAmount);
        rewardStablecoin.transfer(msg.sender, finalReward);
    }
}