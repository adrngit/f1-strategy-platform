from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    fastf1_cache_path: str


settings = Settings()