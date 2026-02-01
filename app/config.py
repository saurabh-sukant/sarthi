from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    openai_api_key: str = ""
    # Use absolute paths so DB and Chroma are consistent regardless of CWD
    database_url: str = f"sqlite:///{BASE_DIR / 'sarthi.db'}"
    chroma_path: str = str(BASE_DIR / "chroma_db")
    max_tokens: int = 1000
    temperature: float = 0.7
    model_name: str = "gpt-4"
    secret_key: str = "your-secret-key-here"

    class Config:
        env_file = ".env"


settings = Settings()

# Normalize paths: if env or user provided relative paths, make them absolute
try:
    if settings.database_url and settings.database_url.startswith("sqlite:///"):
        db_path = settings.database_url.replace("sqlite:///", "")
        db_path_obj = Path(db_path)
        if not db_path_obj.is_absolute():
            settings.database_url = f"sqlite:///{str(BASE_DIR / db_path_obj)}"

    # Ensure chroma_path is absolute
    chroma_path_obj = Path(settings.chroma_path)
    if not chroma_path_obj.is_absolute():
        settings.chroma_path = str(BASE_DIR / chroma_path_obj)
except Exception:
    # Best-effort normalization; if anything fails, keep original settings
    pass