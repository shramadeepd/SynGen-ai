"""
Configuration settings for SynGen AI Backend
"""
import os

class Settings:
    """Application settings"""
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://syngen_user:syngen_password@localhost:5432/syngen_ai")
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017/syngen_documents")
    
    # Security settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "syngen-ai-super-secret-jwt-key-change-in-production-12345")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # App settings
    APP_NAME: str = "SynGen AI"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # AI settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")

settings = Settings()