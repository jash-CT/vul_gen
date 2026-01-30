use serde::{Deserialize, Serialize};
use sqlx::FromRow;
use uuid::Uuid;

#[derive(Debug, Serialize, Deserialize, FromRow)]
pub struct ExternalIntegration {
    pub id: Uuid,
    pub system_name: String,
    pub api_endpoint: String,
    pub auth_type: String,
    pub credentials: String,  // Encrypted/masked credentials
    pub is_active: bool,
    pub created_at: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CreateIntegrationRequest {
    pub system_name: String,
    pub api_endpoint: String,
    pub auth_type: String,
    pub credentials: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct WebhookPayload {
    pub source_system: String,
    pub event_type: String,
    pub payload_data: serde_json::Value,
}