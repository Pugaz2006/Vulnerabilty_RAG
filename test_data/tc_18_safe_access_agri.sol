// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SafeQualityInspectorProxy {
    address public chiefInspector;
    bool public isCertified;
    bool private initialized;

    // SAFE: Can only be executed once
    function initialize() external {
        require(!initialized, "Already initialized");
        chiefInspector = msg.sender;
        initialized = true;
    }

    function certifyBatch() external {
        require(msg.sender == chiefInspector, "Only Chief Inspector");
        isCertified = true;
    }
}