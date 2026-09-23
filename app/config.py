from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    whatsapp_token: str
    whatsapp_phone_number_id: str
    whatsapp_verify_token: str
    allowed_phone_number: str
    database_url: str = "sqlite+aiosqlite:///./projects.db"


settings = Settings()