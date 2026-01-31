from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str = ""
    database_url: str = "sqlite:///./sarthi.db"
    chroma_path: str = "./chroma_db"
    max_tokens: int = 1000
    temperature: float = 0.7
    model_name: str = "gpt-4"
    secret_key: str = "your-secret-key-here"

    class Config:
        env_file = ".env"

settings = Settings()