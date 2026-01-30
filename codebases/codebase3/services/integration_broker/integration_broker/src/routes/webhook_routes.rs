use axum::{
    routing::{post},
    Router,
    extract::State,
    Json,
};
use sqlx::SqlitePool;

use crate::models::integration::WebhookPayload;
use crate::services::webhook_service;

pub fn webhook_routes() -> Router<SqlitePool> {
    Router::new()
        .route("/webhooks/:system_name", post(handle_webhook))
}

async fn handle_webhook(
    State(pool): State<SqlitePool>,
    Json(payload): Json<WebhookPayload>
) -> Result<Json<serde_json::Value>, (axum::http::StatusCode, String)> {
    match webhook_service::process_webhook(&pool, payload).await {
        Ok(response) => Ok(Json(response)),
        Err(e) => Err((
            axum::http::StatusCode::INTERNAL_SERVER_ERROR, 
            format!("Webhook processing failed: {}", e)
        ))
    }
}