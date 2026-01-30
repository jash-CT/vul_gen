package com.enterprise.orderprocessing

class PaymentIntegration {
    // Minimal payment processing stub
    fun processPayment(order: Order): Boolean {
        // Simulated payment processing with minimal validation
        return when {
            order.totalPrice < 0 -> false
            order.totalPrice > 10000 -> false
            else -> true
        }
    }
}