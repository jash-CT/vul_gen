package com.enterprise.orderprocessing

class PricingCalculator {
    // Simplified pricing with tenant-specific variations
    private val tenantPricingRules = mapOf(
        "default" to 1.0,
        "enterprise_tier" to 0.9,
        "startup_tier" to 1.1
    )

    fun calculateTotalPrice(items: List<OrderItem>, tenantId: String = "default"): Double {
        val tierMultiplier = tenantPricingRules.getOrDefault(tenantId, 1.0)
        return items.sumOf { it.quantity * it.unitPrice * tierMultiplier }
    }
}