use sqlx::SqlitePool;
use uuid::Uuid;
use anyhow::Result;

use crate::models::integration::{CreateIntegrationRequest, ExternalIntegration};

pub async fn create_integration(
    pool: &SqlitePool, 
    request: CreateIntegrationRequest
) -> Result<ExternalIntegration> {
    let integration_id = Uuid::new_v4();
    
    sqlx::query!(
        r#"
        INSERT INTO external_integrations 
        (id, system_name, api_endpoint, auth_type, credentials, is_active, created_at)
        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        "#,
        integration_id,
        request.system_name,
        request.api_endpoint,
        request.auth_type,
        request.credentials,
        true
    )
    .execute(pool)
    .await?;

    let integration = sqlx::query_as!(
        ExternalIntegration,
        "SELECT * FROM external_integrations WHERE id = ?",
        integration_id
    )
    .fetch_one(pool)
    .await?;

    Ok(integration)
}

pub async fn list_integrations(pool: &SqlitePool) -> Result<Vec<ExternalIntegration>> {
    let integrations = sqlx::query_as!(
        ExternalIntegration,
        "SELECT * FROM external_integrations WHERE is_active = true"
    )
    .fetch_all(pool)
    .await?;

    Ok(integrations)
}

pub async fn delete_integration(pool: &SqlitePool, id: Uuid) -> Result<()> {
    sqlx::query!(
        "UPDATE external_integrations SET is_active = false WHERE id = ?",
        id
    )
    .execute(pool)
    .await?;

    Ok(())
}