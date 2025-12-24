"""System settings configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """System settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # LLM API Configuration
    openai_api_key: str
    openai_api_base: str = "https://api.openai.com/v1"
    
    # Model Configuration
    proposer_model: str = "gpt-4-turbo-preview"
    solver_model: str = "gpt-4-turbo-preview"
    validator_model: str = "gpt-4-turbo-preview"
    
    # Generation Parameters
    temperature: float = 0.7
    max_tokens: int = 2000
    
    # System Configuration
    max_iterations: int = 10
    
    # Paths
    upload_dir: str = "data/uploads"
    output_dir: str = "data/outputs"
    log_dir: str = "logs"


# Global settings instance
settings = Settings()
