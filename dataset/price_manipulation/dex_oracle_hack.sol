// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IDEX {
    function getSpotPrice() external view returns (uint256);
}

contract VulnerableLending {
    IDEX public oracle;
    mapping(address => uint256) public collateral;

    constructor(address _oracle) {
        oracle = IDEX(_oracle);
    }

    function depositCollateral() external payable {
        collateral[msg.sender] += msg.value;
    }

    // The vulnerability: Relying on a highly manipulatable spot price
    function borrowTokens() external {
        uint256 currentPrice = oracle.getSpotPrice();
        uint256 maxBorrow = collateral[msg.sender] * currentPrice;
        
        // Transfer logic here...
    }
}