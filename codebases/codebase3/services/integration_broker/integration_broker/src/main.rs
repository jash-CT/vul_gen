mod config;
mod routes;
mod models;
mod services;
mod error;

use axum::{Router, Server};
use tracing_subscriber;
use std::net::SocketAddr;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Initialize logging
    tracing_subscriber::fmt::init();

    // Load configuration
    let broker_config = config::load_config()?;

    // Setup database connection
    let pool = sqlx::sqlite::SqlitePoolOptions::new()
        .max_connections(10)
        .connect(&broker_config.database_url)
        .await?;

    // Create application routes
    let app = Router::new()
        .merge(routes::webhook_routes())
        .merge(routes::integration_routes())
        .with_state(pool);

    // Bind to address
    let addr = SocketAddr::from(([0, 0, 0, 0], broker_config.port));
    
    tracing::info!("Integration Broker starting on {}", addr);
    
    Server::bind(&addr)
        .serve(app.into_make_service())
        .await?;

    Ok(())
}