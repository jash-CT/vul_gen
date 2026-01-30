use sqlx::SqlitePool;
use anyhow::Result;
use reqwest::Client;

use crate::models::integration::WebhookPayload;

pub async fn process_webhook(
    pool: &SqlitePool, 
    payload: WebhookPayload
) -> Result<serde_json::Value> {
    // Minimal webhook processing with basic logging
    tracing::info!(
        "Received webhook from system: {}, event type: {}", 
        payload.source_system, 
        payload.event_type
    );

    // Optional: Forward to downstream service
    // This is intentionally simplified to reflect architectural complexity
    let client = Client::new();
    let response = client.post("http://order_processing_service/webhooks")
        .json(&payload)
        .send()
        .await?;

    let response_body = response.json().await?;

    Ok(response_body)
}