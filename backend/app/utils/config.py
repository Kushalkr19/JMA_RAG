from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://jma_user:jma_password@localhost:5432/jma_knowledge_base"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # AI/LLM
    openai_api_key: Optional[str] = None
    llama_model_path: Optional[str] = None
    
    # Vector embeddings
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    
    # File storage
    upload_dir: str = "data/uploads"
    deliverable_dir: str = "data/deliverables"
    template_dir: str = "templates"
    
    # Application
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"

settings = Settings()