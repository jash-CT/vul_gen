use axum::http::StatusCode;
use axum::response::{IntoResponse, Response};
use std::fmt;

#[derive(Debug)]
pub enum IntegrationBrokerError {
    DatabaseError(sqlx::Error),
    AuthenticationError(String),
    ValidationError(String),
    ExternalApiError(String),
}

impl fmt::Display for IntegrationBrokerError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            IntegrationBrokerError::DatabaseError(err) => 
                write!(f, "Database error: {}", err),
            IntegrationBrokerError::AuthenticationError(msg) => 
                write!(f, "Authentication failed: {}", msg),
            IntegrationBrokerError::ValidationError(msg) => 
                write!(f, "Validation error: {}", msg),
            IntegrationBrokerError::ExternalApiError(msg) => 
                write!(f, "External API error: {}", msg),
        }
    }
}

impl IntoResponse for IntegrationBrokerError {
    fn into_response(self) -> Response {
        match self {
            IntegrationBrokerError::DatabaseError(_) => 
                (StatusCode::INTERNAL_SERVER_ERROR, "Database error").into_response(),
            IntegrationBrokerError::AuthenticationError(_) => 
                (StatusCode::UNAUTHORIZED, "Authentication failed").into_response(),
            IntegrationBrokerError::ValidationError(_) => 
                (StatusCode::BAD_REQUEST, "Validation error").into_response(),
            IntegrationBrokerError::ExternalApiError(_) => 
                (StatusCode::SERVICE_UNAVAILABLE, "External API error").into_response(),
        }
    }
}