from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class VapiCall(BaseModel):
    id: Optional[str] = None
    orgId: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
    status: Optional[str] = None
    endedReason: Optional[str] = None
    recordingUrl: Optional[str] = None
    summary: Optional[str] = None
    transcript: Optional[str] = None

class VapiFunctionCallDetail(BaseModel):
    name: str
    parameters: Optional[Dict[str, Any]] = {}

class VapiFunctionCallPayload(BaseModel):
    functionCall: Optional[VapiFunctionCallDetail] = None
    call: Optional[VapiCall] = None

class VapiArtifact(BaseModel):
    messages: Optional[List[Dict[str, Any]]] = []
    transcript: Optional[str] = ""
    recordingUrl: Optional[str] = None

class VapiAnalysis(BaseModel):
    summary: Optional[str] = ""
    structuredData: Optional[Dict[str, Any]] = {}
    successEvaluation: Optional[str] = ""

class VapiWebhookMessage(BaseModel):
    type: str = Field(..., description="end-of-call-report, function-call, status-update, transcript")
    call: Optional[VapiCall] = None
    functionCall: Optional[VapiFunctionCallDetail] = None
    artifact: Optional[VapiArtifact] = None
    analysis: Optional[VapiAnalysis] = None
    timestamp: Optional[Any] = None

class AvailabilityRequest(BaseModel):
    date: Optional[str] = Field(None, example="2026-08-20")
    time_slot: Optional[str] = Field(None, example="14:00")
    timezone: Optional[str] = Field("UTC", example="EST")

class AvailabilityResponse(BaseModel):
    available: bool
    message: str
    suggested_slots: List[str]
