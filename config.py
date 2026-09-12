import os
import json
from typing import List
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
    CORS_ORIGINS: List[str] = ["*"]

    def __init__(self, **data):
        super().__init__(**data)
        raw_origins = os.getenv("CORS_ORIGINS", '["*"]')
        try:
            self.CORS_ORIGINS = json.loads(raw_origins)
        except Exception:
            self.CORS_ORIGINS = [raw_origins]

settings = Settings()
