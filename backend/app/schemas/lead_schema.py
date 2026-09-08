from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class LeadBase(BaseModel):
    name: str = Field(..., example="Sarah Connor")
    email: Optional[str] = Field(None, example="sarah@cyberdyne.com")
    phone: Optional[str] = Field(None, example="+15550199")
    company: Optional[str] = Field(None, example="Skynet Systems")
    lead_temperature: str = Field("WARM", description="HOT, WARM, or COLD")
    summary: str = Field("", description="AI Generated Call Summary")
    budget: Optional[str] = Field(None, example="$10k - $25k")
    timeframe: Optional[str] = Field(None, example="Immediate / 1-2 weeks")
    intent: Optional[str] = Field(None, example="Enterprise CRM Integration")
    sentiment_score: Optional[float] = Field(0.8, example=0.85)
    call_duration_seconds: Optional[int] = Field(0, example=145)
    recording_url: Optional[str] = Field(None, example="https://api.vapi.ai/recordings/sample.mp3")
    transcript: Optional[str] = Field(None, example="User: Hi, I need pricing info...")
    status: str = Field("NEW", description="NEW, QUALIFIED, CONTACTED, CONVERTED, ARCHIVED")

class LeadCreate(LeadBase):
    pass

class LeadUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    lead_temperature: Optional[str] = None
    summary: Optional[str] = None
    budget: Optional[str] = None
    timeframe: Optional[str] = None
    intent: Optional[str] = None
    sentiment_score: Optional[float] = None
    call_duration_seconds: Optional[int] = None
    recording_url: Optional[str] = None
    transcript: Optional[str] = None
    status: Optional[str] = None
    synced_to_gsheets: Optional[bool] = None
    synced_to_n8n: Optional[bool] = None
    email_sent: Optional[bool] = None

class LeadResponse(LeadBase):
    id: str
    created_at: str
    synced_to_gsheets: bool = False
    synced_to_n8n: bool = False
    email_sent: bool = False

    class Config:
        from_attributes = True

class LeadStats(BaseModel):
    total_leads: int
    hot_leads: int
    warm_leads: int
    cold_leads: int
    conversion_rate: float
    avg_call_duration_seconds: float
