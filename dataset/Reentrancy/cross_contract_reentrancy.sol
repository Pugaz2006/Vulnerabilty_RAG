// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract BankVault {
    mapping(address => uint256) public balances;
    address public rewardContract;

    function setRewardContract(address _reward) external {
        rewardContract = _reward;
    }

    // 🔴 VULNERABLE FUNCTION
    // State is updated late, but it affects another contract
    function withdrawAll() external {
        uint256 amount = balances[msg.sender];
        require(amount > 0, "No balance");

        // Control handed to attacker
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");

        // Attacker pauses execution here and calls RewardStrategy.claimRewards()

        balances[msg.sender] = 0;
    }
}

contract RewardStrategy {
    BankVault public vault;
    mapping(address => bool) public hasClaimed;

    constructor(address _vault) {
        vault = BankVault(_vault);
    }

    // 🔴 VULNERABLE ARCHITECTURE
    // Trusts the Vault's state, assuming it is always accurate
    function claimRewards() external {
        require(!hasClaimed[msg.sender], "Already claimed");
        
        // Reads the Vault's balance. During the cross-contract reentrancy attack,
        // the user has already withdrawn their ETH, but vault.balances() still reports the old amount!
        uint256 userBalance = vault.balances(msg.sender);
        require(userBalance > 0, "Must be a depositor");

        hasClaimed[msg.sender] = true;
        
        // Mints rewards based on a phantom balance
        // mintTokens(msg.sender, userBalance * 10);
    }
}