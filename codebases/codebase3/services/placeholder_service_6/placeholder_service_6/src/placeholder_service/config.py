from pydantic import BaseSettings

class ServiceConfig(BaseSettings):
    """
    Minimal configuration for placeholder service
    Maintains consistency with enterprise configuration pattern
    """
    SERVICE_NAME: str = "placeholder-service-6"
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_prefix = "PLACEHOLDER_"