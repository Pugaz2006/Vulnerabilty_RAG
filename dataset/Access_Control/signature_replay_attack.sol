// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SignatureReplay {
    mapping(address => uint256) public balances;

    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }

    // 🔴 VULNERABLE FUNCTION
    // Verifies the signature but doesn't track if it has been used before (no nonce)
    function withdrawWithSignature(
        address to, 
        uint256 amount, 
        uint8 v, 
        bytes32 r, 
        bytes32 s
    ) external {
        bytes32 messageHash = keccak256(abi.encodePacked(to, amount));
        bytes32 ethSignedMessageHash = keccak256(
            abi.encodePacked("\x19Ethereum Signed Message:\n32", messageHash)
        );

        // Recovers the signer's address
        address signer = ecrecover(ethSignedMessageHash, v, r, s);
        
        require(signer != address(0), "Invalid signature");
        require(balances[signer] >= amount, "Insufficient balance");

        balances[signer] -= amount;
        
        // BUG: The attacker captures the v, r, s values from the mempool
        // and calls this function 100 times. Because there is no 'nonce' mapping,
        // the signature remains permanently valid.
        payable(to).transfer(amount);
    }
}