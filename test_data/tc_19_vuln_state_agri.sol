// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract FreightTracker {
    uint256[] public activeShipmentIds;
    mapping(uint256 => uint256) public shipmentIndex;

    function addShipment(uint256 shipmentId) external {
        activeShipmentIds.push(shipmentId);
        shipmentIndex[shipmentId] = activeShipmentIds.length - 1;
    }

    function fulfillShipment(uint256 shipmentId) external {
        uint256 indexToRemove = shipmentIndex[shipmentId];
        uint256 lastShipmentId = activeShipmentIds[activeShipmentIds.length - 1];

        // Swap the last element into the spot being removed
        activeShipmentIds[indexToRemove] = lastShipmentId;
        activeShipmentIds.pop();

        // VULNERABLE: 'lastShipmentId' was moved, but its index mapping was never updated!
        // Future attempts to fulfill 'lastShipmentId' will fail or remove the wrong item.
        delete shipmentIndex[shipmentId];
    }
}