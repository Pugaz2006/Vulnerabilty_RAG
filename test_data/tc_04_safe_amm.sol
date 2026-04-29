// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IRouter { function swapExactTokensForTokens(uint, uint, address[] calldata, address, uint) external; }

contract SafeSwapper {
    IRouter public router;
    constructor(address _router) { router = IRouter(_router); }

    function swapTokens(uint256 amountIn, uint256 minAmountOut, address[] calldata path) external {
        // SAFE: Front-running will cause the transaction to revert due to minAmountOut
        router.swapExactTokensForTokens(amountIn, minAmountOut, path, msg.sender, block.timestamp);
    }
}