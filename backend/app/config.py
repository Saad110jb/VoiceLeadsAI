import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "VoiceLeads AI Backend"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # OpenAI Credentials
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    
    # Vapi Credentials
    VAPI_API_KEY: Optional[str] = os.getenv("VAPI_API_KEY", "")
    VAPI_ASSISTANT_ID: Optional[str] = os.getenv("VAPI_ASSISTANT_ID", "b2bcd187-93c1-4830-bf36-e98d172e7546")
    VAPI_PHONE_NUMBER_ID: Optional[str] = os.getenv("VAPI_PHONE_NUMBER_ID", "6c2b10f2-d55d-4d50-aefc-fa20...")
    VAPI_PHONE_NUMBER: Optional[str] = os.getenv("VAPI_PHONE_NUMBER", "+14422461201")
    
    # n8n Automation Relay
    N8N_WEBHOOK_URL: Optional[str] = os.getenv("N8N_WEBHOOK_URL", "https://muhammadsaad001.app.n8n.cloud/webhook/vapi-call-complete")
    
    # SMTP Email Credentials
    SENDER_EMAIL: Optional[str] = os.getenv("SENDER_EMAIL", "ms0574203@gmail.com")
    SENDER_APP_PASSWORD: Optional[str] = os.getenv("SENDER_APP_PASSWORD", "nntp qbye ttai wola")
    NOTIFICATION_RECEIVER: Optional[str] = os.getenv("NOTIFICATION_RECEIVER", "ms0574203@gmail.com")
    
    # Google Sheets Integration
    GOOGLE_SERVICE_ACCOUNT_FILE: str = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json")
    GOOGLE_SHEET_NAME: str = os.getenv("GOOGLE_SHEET_NAME", "lead_tracker")
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
