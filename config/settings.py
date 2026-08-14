"""
Settings and configuration management for AI Trip Agent.
Supports multiple LLM providers and environment-based configuration.
"""

import os
from enum import Enum
from functools import lru_cache
from typing import Optional, Union

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    LMSTUDIO = "lmstudio"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"
    OLLAMA = "ollama"
    ABACUSAI = "abacusai"  # Add this line


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = Field(default="AI Trip Agent", description="Application name")
    app_version: str = Field(default="2.0.0", description="Application version")
    environment: str = Field(default="development", description="Environment (development/production)")
    debug: bool = Field(default=True, description="Debug mode")

    # API Server
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8001, description="API port")
    api_reload: bool = Field(default=True, description="Auto-reload on code changes")

    # LLM Configuration
    llm_provider: LLMProvider = Field(default=LLMProvider.LMSTUDIO, description="LLM provider to use")
    llm_temperature: float = Field(default=0.7, description="LLM temperature")
    llm_max_tokens: int = Field(default=2048, description="Maximum tokens for LLM response")
    llm_timeout: int = Field(default=120, description="LLM request timeout in seconds")

    # LM Studio (Local)
    lmstudio_api_url: str = Field(
        default="http://127.0.0.1:1234/v1",
        description="LM Studio API base URL"
    )
    lmstudio_model: str = Field(
        default="llama-3.2-1b-instruct",
        description="LM Studio model name"
    )

    # OpenAI
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    openai_model: str = Field(default="gpt-3.5-turbo", description="OpenAI model name")
    openai_api_base: Optional[str] = Field(default=None, description="OpenAI API base URL (for proxies)")

    # Anthropic (Claude)
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    anthropic_model: str = Field(
        default="claude-3-5-sonnet-20241022",
        description="Anthropic model name"
    )

    # Azure OpenAI
    azure_openai_api_key: Optional[str] = Field(default=None, description="Azure OpenAI API key")
    azure_openai_endpoint: Optional[str] = Field(default=None, description="Azure OpenAI endpoint")
    azure_openai_deployment: Optional[str] = Field(default=None, description="Azure OpenAI deployment name")
    azure_openai_api_version: str = Field(default="2024-02-15-preview", description="Azure OpenAI API version")

    # Ollama (Local alternative)
    ollama_api_url: str = Field(default="http://localhost:11434", description="Ollama API URL")
    ollama_model: str = Field(default="llama3.2", description="Ollama model name")

    # Abacus AI
    abacusai_api_key: Optional[str] = Field(default=None, description="Abacus AI API key")
    abacusai_model: str = Field(default="gpt-4o", description="Abacus AI model name")
    abacusai_api_url: str = Field(
        default="https://api.abacus.ai/v1",
        description="Abacus AI API base URL"
    )

    # Embeddings
    embedding_provider: str = Field(default="openai", description="Embedding provider (openai/huggingface)")
    embedding_model: str = Field(
        default="text-embedding-3-small",
        description="Embedding model name"
    )
    embedding_dimension: int = Field(default=1536, description="Embedding vector dimension")

    # ChromaDB
    chroma_host: str = Field(default="localhost", description="ChromaDB host")
    chroma_port: int = Field(default=8002, description="ChromaDB port")
    chroma_collection_name: str = Field(
        default="assam_travel_knowledge",
        description="ChromaDB collection name"
    )
    chroma_persist_directory: str = Field(
        default="./_chroma",
        description="ChromaDB persistence directory"
    )

    # RAG Configuration
    rag_chunk_size: int = Field(default=1000, description="Text chunk size for RAG")
    rag_chunk_overlap: int = Field(default=200, description="Text chunk overlap")
    rag_top_k: int = Field(default=5, description="Number of documents to retrieve")
    rag_similarity_threshold: float = Field(default=0.7, description="Similarity threshold for retrieval")

    # LangSmith (Experiment Tracking)
    langsmith_api_key: Optional[str] = Field(default=None, description="LangSmith API key")
    langsmith_project: str = Field(
        default="ai-trip-agent-poc",
        description="LangSmith project name"
    )
    langsmith_tracing: bool = Field(default=False, description="Enable LangSmith tracing")

    # Carbon Calculation
    carbon_api_enabled: bool = Field(default=True, description="Enable carbon calculation")
    carbon_default_emission_factor: float = Field(
        default=0.12,
        description="Default CO2 emission factor (kg CO2/km)"
    )

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )

    # Security
    cors_origins: Union[str, list[str]] = Field(
        default="http://localhost:8516,http://localhost:3000",
        description="CORS allowed origins (comma-separated string or list)"
    )
    api_key_header: str = Field(default="X-API-Key", description="API key header name")
    api_key: Optional[str] = Field(default=None, description="API key for authentication")

    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v

    # Cloud Deployment
    cloud_provider: Optional[str] = Field(default=None, description="Cloud provider (aws/gcp/azure)")
    static_ip: Optional[str] = Field(default=None, description="Static IP for deployment")
    domain_name: Optional[str] = Field(default=None, description="Domain name for deployment")
    
    def get_llm_config(self) -> dict:
        """Get LLM configuration based on selected provider."""
        if self.llm_provider == LLMProvider.LMSTUDIO:
            return {
                "provider": "lmstudio",
                "base_url": self.lmstudio_api_url,
                "model": self.lmstudio_model,
                "temperature": self.llm_temperature,
                "max_tokens": self.llm_max_tokens,
            }
        elif self.llm_provider == LLMProvider.OPENAI:
            return {
                "provider": "openai",
                "api_key": self.openai_api_key,
                "model": self.openai_model,
                "base_url": self.openai_api_base,
                "temperature": self.llm_temperature,
                "max_tokens": self.llm_max_tokens,
            }
        elif self.llm_provider == LLMProvider.ANTHROPIC:
            return {
                "provider": "anthropic",
                "api_key": self.anthropic_api_key,
                "model": self.anthropic_model,
                "temperature": self.llm_temperature,
                "max_tokens": self.llm_max_tokens,
            }
        elif self.llm_provider == LLMProvider.AZURE:
            return {
                "provider": "azure",
                "api_key": self.azure_openai_api_key,
                "endpoint": self.azure_openai_endpoint,
                "deployment": self.azure_openai_deployment,
                "api_version": self.azure_openai_api_version,
                "temperature": self.llm_temperature,
                "max_tokens": self.llm_max_tokens,
            }
        elif self.llm_provider == LLMProvider.OLLAMA:
            return {
                "provider": "ollama",
                "base_url": self.ollama_api_url,
                "model": self.ollama_model,
                "temperature": self.llm_temperature,
            }
        elif self.llm_provider == LLMProvider.ABACUSAI:
            return {
                "provider": "abacusai",
                "api_key": self.abacusai_api_key,
                "base_url": self.abacusai_api_url,
                "model": self.abacusai_model,
                "temperature": self.llm_temperature,
                "max_tokens": self.llm_max_tokens,
            }
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
    
    def get_chroma_url(self) -> str:
        """Get ChromaDB connection URL."""
        return f"http://{self.chroma_host}:{self.chroma_port}"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
