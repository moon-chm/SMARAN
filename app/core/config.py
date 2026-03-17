from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "SMARAN API"
    VERSION: str = "1.0.0"
    
    NEO4J_URI: str = "neo4j+s://demo"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "demo"
    
    GROQ_API_KEY: str
    ELEVENLABS_API_KEY: str
    
    JWT_SECRET: str = "fallback_secret_for_demo_purposes_only"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
