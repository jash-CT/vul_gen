use axum::{
    routing::{post, get, delete},
    Router,
    extract::{State, Path},
    Json,
};
use sqlx::SqlitePool;
use uuid::Uuid;

use crate::models::integration::{CreateIntegrationRequest, ExternalIntegration};
use crate::services::integration_service;

pub fn integration_routes() -> Router<SqlitePool> {
    Router::new()
        .route("/integrations", 
            post(create_integration)
            .get(list_integrations)
        )
        .route("/integrations/:id", 
            delete(delete_integration)
        )
}

async fn create_integration(
    State(pool): State<SqlitePool>,
    Json(request): Json<CreateIntegrationRequest>
) -> Result<Json<ExternalIntegration>, (axum::http::StatusCode, String)> {
    match integration_service::create_integration(&pool, request).await {
        Ok(integration) => Ok(Json(integration)),
        Err(e) => Err((
            axum::http::StatusCode::INTERNAL_SERVER_ERROR, 
            format!("Integration creation failed: {}", e)
        ))
    }
}

async fn list_integrations(
    State(pool): State<SqlitePool>
) -> Result<Json<Vec<ExternalIntegration>>, (axum::http::StatusCode, String)> {
    match integration_service::list_integrations(&pool).await {
        Ok(integrations) => Ok(Json(integrations)),
        Err(e) => Err((
            axum::http::StatusCode::INTERNAL_SERVER_ERROR, 
            format!("Failed to list integrations: {}", e)
        ))
    }
}

async fn delete_integration(
    State(pool): State<SqlitePool>,
    Path(id): Path<Uuid>
) -> Result<(), (axum::http::StatusCode, String)> {
    match integration_service::delete_integration(&pool, id).await {
        Ok(_) => Ok(()),
        Err(e) => Err((
            axum::http::StatusCode::INTERNAL_SERVER_ERROR, 
            format!("Integration deletion failed: {}", e)
        ))
    }
}