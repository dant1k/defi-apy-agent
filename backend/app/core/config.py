"""Application configuration"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: str = "postgresql://genora:genora_pass@postgres:5432/genora_terminal"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # External APIs
    DEFILLAMA_API_URL: str = "https://api.llama.fi"
    DEXSCREENER_API_URL: str = "https://api.dexscreener.com"
    APTOS_INDEXER_URL: str = "https://api.mainnet.aptoslabs.com/v1/graphql"  # Aptos Indexer GraphQL (Level 3)
    APTOS_NODE_URL: str = "https://fullnode.mainnet.aptoslabs.com/v1"  # Aptos Node URL for token metadata
    HYPERION_API_URL: str = "https://hyperfluid-api.alcove.pro/v1/graphql"  # Hyperion GraphQL API
    
    # Scheduler
    SCHEDULER_ENABLED: bool = True
    REFRESH_DEXES_INTERVAL_MINUTES: int = 15
    REFRESH_POOLS_INTERVAL_MINUTES: int = 10
    TOP_DEXES_COUNT: int = 10
    
    # Cache TTL (seconds)
    CACHE_DEXES_TTL: int = 300
    CACHE_DEX_DETAIL_TTL: int = 300
    CACHE_POOLS_TTL: int = 120
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

