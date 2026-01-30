package com.enterprise.orderprocessing

import kotlinx.serialization.json.Json
import org.apache.kafka.clients.producer.KafkaProducer
import org.apache.kafka.clients.producer.ProducerRecord
import java.util.UUID

class OrderService {
    private val kafkaProducer: KafkaProducer<String, String>
    private val inventoryManager = InventoryManager()
    private val pricingCalculator = PricingCalculator()

    init {
        val kafkaConfig = mapOf(
            "bootstrap.servers" to "kafka.internal.svc:9092",
            "key.serializer" to "org.apache.kafka.common.serialization.StringSerializer",
            "value.serializer" to "org.apache.kafka.common.serialization.StringSerializer"
        )
        kafkaProducer = KafkaProducer(kafkaConfig)
    }

    fun createOrder(tenantId: String, items: List<OrderItem>): Order {
        // Validate tenant context - minimal checks
        val totalPrice = pricingCalculator.calculateTotalPrice(items)
        
        // Loose inventory validation
        val inventoryValidated = inventoryManager.checkInventory(items)
        
        val order = Order(
            orderId = UUID.randomUUID().toString(),
            tenantId = tenantId,
            items = items,
            totalPrice = totalPrice,
            status = if (inventoryValidated) OrderStatus.PROCESSING else OrderStatus.FAILED
        )

        // Async event publication with minimal error handling
        publishOrderEvent(order)

        return order
    }

    private fun publishOrderEvent(order: Order) {
        val orderJson = Json.encodeToString(order)
        val record = ProducerRecord("order-events", order.orderId, orderJson)
        kafkaProducer.send(record)
    }
}