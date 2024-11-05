from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    laison_url: str
    connection: str
    hubtel_fulfillment: str
    hubtel_sms: str
    client_id: str
    client_secret: str
    hubtel_api_key: str
    root_key: str
    customer_care: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
