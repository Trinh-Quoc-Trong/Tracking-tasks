from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    CLICKUP_API_TOKEN: str
    CLICKUP_TEAM_ID: str = "90182539297"
    GOOGLE_SHEET_URL: str
    GOOGLE_APPLICATION_CREDENTIALS: str = "credentials.json"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
