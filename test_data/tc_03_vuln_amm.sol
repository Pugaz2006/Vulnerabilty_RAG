// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IRouter { function swapExactTokensForTokens(uint, uint, address[] calldata, address, uint) external; }

contract UnsafeSwapper {
    IRouter public router;
    constructor(address _router) { router = IRouter(_router); }

    function swapTokens(uint256 amountIn, address[] calldata path) external {
        // VULNERABLE: amountOutMin is hardcoded to 0. Total slippage vulnerability.
        router.swapExactTokensForTokens(amountIn, 0, path, msg.sender, block.timestamp);
    }
}