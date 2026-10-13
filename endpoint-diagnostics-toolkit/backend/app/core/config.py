from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    app_name: str = "Endpoint Diagnostics & IT Support Toolkit"
    version: str = "1.0.0"
    database_url: str = "sqlite:///./edst.db"
    demo_mode: bool = False
    show_hostname: bool = True
    model_config = SettingsConfigDict(env_file=".env", env_prefix="EDST_", extra="ignore")
settings = Settings()
