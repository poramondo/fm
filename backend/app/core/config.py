import os
from datetime import timedelta

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://mixlab:password@db:5432/mixlabdb")
    APP_SECRET_KEY: str = os.getenv("APP_SECRET_KEY", "CHANGE_ME")
    LOG_TTL_HOURS: int = int(os.getenv("LOG_TTL_HOURS", "48"))
    ADDRESS_HOLD_MINUTES: int = int(os.getenv("ADDRESS_HOLD_MINUTES", "30"))

settings = Settings()