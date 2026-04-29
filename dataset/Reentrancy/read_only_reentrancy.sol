// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// The "Safe" Pool (But its View function is vulnerable)
contract DefiPool {
    uint256 public totalEther;
    uint256 public totalTokens;
    mapping(address => uint256) public balances;

    // 🔴 VULNERABLE VIEW FUNCTION
    // Reports a manipulated price while withdraw() is pausing execution
    function getSpotPrice() public view returns (uint256) {
        if (totalTokens == 0) return 0;
        return (totalEther * 1e18) / totalTokens;
    }

    function removeLiquidity(uint256 lpTokens) external {
        uint256 ethOut = (totalEther * lpTokens) / totalTokens;
        
        // 1. Sends ETH (Control handed to attacker)
        (bool success, ) = msg.sender.call{value: ethOut}("");
        require(success, "ETH transfer failed");

        // 2. Attacker's fallback function triggers! 
        // At this exact millisecond, totalEther has NOT been decremented,
        // but the attacker already has the ETH. getSpotPrice() is now mathematically broken.
        // The attacker calls a completely separate Lending Protocol to borrow against this fake price.

        // 3. State is finally updated (Too late for the third-party protocol)
        totalEther -= ethOut;
        totalTokens -= lpTokens;
        balances[msg.sender] -= lpTokens;
    }
}