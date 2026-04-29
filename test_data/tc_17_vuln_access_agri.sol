// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract QualityInspectorProxy {
    address public chiefInspector;
    bool public isCertified;

    // VULNERABLE: Missing 'initializer' modifier. Anyone can call this repeatedly.
    function initialize() external {
        chiefInspector = msg.sender;
    }

    function certifyBatch() external {
        require(msg.sender == chiefInspector, "Only Chief Inspector");
        isCertified = true;
    }
}