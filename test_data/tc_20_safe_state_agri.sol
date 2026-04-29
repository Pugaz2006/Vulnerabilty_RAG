// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SafeFreightTracker {
    uint256[] public activeShipmentIds;
    mapping(uint256 => uint256) public shipmentIndex;

    function addShipment(uint256 shipmentId) external {
        activeShipmentIds.push(shipmentId);
        shipmentIndex[shipmentId] = activeShipmentIds.length - 1;
    }

    function fulfillShipment(uint256 shipmentId) external {
        uint256 indexToRemove = shipmentIndex[shipmentId];
        uint256 lastShipmentId = activeShipmentIds[activeShipmentIds.length - 1];

        activeShipmentIds[indexToRemove] = lastShipmentId;
        activeShipmentIds.pop();

        // SAFE: The mapping is properly synchronized with the array's new layout
        shipmentIndex[lastShipmentId] = indexToRemove;
        delete shipmentIndex[shipmentId];
    }
}