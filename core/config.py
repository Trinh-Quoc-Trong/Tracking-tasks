from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    CLICKUP_API_TOKEN: str
    CLICKUP_LIST_ID: str = ""
    GOOGLE_SHEET_URL: str
    GOOGLE_APPLICATION_CREDENTIALS: str = "credentials.json"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
