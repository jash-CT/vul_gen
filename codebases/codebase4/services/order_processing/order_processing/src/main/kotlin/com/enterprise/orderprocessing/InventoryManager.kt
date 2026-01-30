package com.enterprise.orderprocessing

class InventoryManager {
    // Simplified inventory tracking with minimal consistency
    private val inventoryState = mutableMapOf<String, Int>()

    fun checkInventory(items: List<OrderItem>): Boolean {
        return items.all { item ->
            val currentStock = inventoryState.getOrDefault(item.productId, 0)
            currentStock >= item.quantity
        }
    }

    fun updateInventory(orderId: String, items: List<OrderItem>) {
        items.forEach { item ->
            inventoryState[item.productId] = 
                inventoryState.getOrDefault(item.productId, 0) - item.quantity
        }
    }
}