use serde::{Deserialize, Serialize};
use anyhow::Result;
use std::env;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct IntegrationBrokerConfig {
    pub port: u16,
    pub database_url: String,
    pub external_api_timeout_ms: u64,
    pub max_retry_attempts: u8,
    pub webhook_secret_key: String,
}

pub fn load_config() -> Result<IntegrationBrokerConfig> {
    Ok(IntegrationBrokerConfig {
        port: env::var("PORT")
            .unwrap_or_else(|_| "8080".to_string())
            .parse()
            .unwrap_or(8080),
        database_url: env::var("DATABASE_URL")
            .unwrap_or_else(|_| "sqlite:integration_broker.db".to_string()),
        external_api_timeout_ms: env::var("API_TIMEOUT")
            .unwrap_or_else(|_| "5000".to_string())
            .parse()
            .unwrap_or(5000),
        max_retry_attempts: env::var("MAX_RETRY_ATTEMPTS")
            .unwrap_or_else(|_| "3".to_string())
            .parse()
            .unwrap_or(3),
        webhook_secret_key: env::var("WEBHOOK_SECRET")
            .unwrap_or_else(|_| "default_insecure_secret".to_string()),
    })
}