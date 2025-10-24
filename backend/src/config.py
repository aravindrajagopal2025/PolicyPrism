"""Application configuration using Pydantic Settings."""
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_name: str = "PolicyWarehouse"
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    secret_key: str
    
    # Database
    database_url: str
    database_pool_size: int = 20
    database_max_overflow: int = 10
    
    # Redis
    redis_url: str
    celery_broker_url: str
    celery_result_backend: str
    
    # Azure Storage
    azure_storage_connection_string: str | None = None
    azure_storage_container_name: str = "policy-pdfs"
    local_storage_path: str | None = "./storage/pdfs"
    
    # LLM Provider
    llm_provider: Literal["openai", "anthropic"] = "openai"
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    
    # Pydantic AI Configuration
    pydantic_ai_model: str = "gpt-4"
    pydantic_ai_temperature: float = 0.1
    pydantic_ai_max_tokens: int = 4000
    
    # Processing Configuration
    max_retries: int = 3
    retry_backoff_base: int = 2
    extraction_confidence_threshold: float = 0.85
    human_review_first_n_policies: int = 5
    
    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    
    # Logging
    log_level: str = "INFO"
    log_format: Literal["json", "text"] = "json"
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def use_azure_storage(self) -> bool:
        """Check if Azure Storage is configured."""
        return bool(self.azure_storage_connection_string and self.azure_storage_connection_string.strip())


# Global settings instance
settings = Settings()
