from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import uuid
import json
import os
from datetime import datetime

from app.schemas.lead_schema import LeadResponse, LeadCreate, LeadUpdate, LeadStats
from app.services.llm_classifier import classifier_service
from app.services.email_service import email_service
from app.services.google_sheets import google_sheets_service
from app.utils.logger import logger

router = APIRouter(prefix="/leads", tags=["Leads CRM"])

LEADS_FILE = "leads_data.json"

def load_leads_from_file() -> List[dict]:
    if not os.path.exists(LEADS_FILE):
        # Initial mock leads for immediate rich dashboard demo
        initial_mock = [
            {
                "id": "lead-saad-100",
                "name": "Muhammad Saad",
                "email": "muhammad110jb@gmail.com",
                "phone": "+923189663004",
                "company": "VoiceLeads Enterprise",
                "lead_temperature": "HOT",
                "summary": "Team member setup for automated outbound Vapi AI voice calls, Google Sheets tracking, and n8n workflow execution.",
                "budget": "$25,000 - $50,000",
                "timeframe": "Immediate (Active)",
                "intent": "Outbound Vapi Voice Agent & CRM Sync",
                "sentiment_score": 0.98,
                "call_duration_seconds": 240,
                "recording_url": "https://actions.google.com/sounds/v1/ambiences/office_space.ogg",
                "transcript": "Agent: Hello Muhammad Saad! Ready for outbound Voice AI integration test.\nMuhammad Saad: Yes, let us test outbound phone calling and n8n workflow execution.",
                "status": "QUALIFIED",
                "synced_to_gsheets": True,
                "synced_to_n8n": True,
                "email_sent": True,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "id": "lead-101",
                "name": "Marcus Vance",
                "email": "marcus.vance@apexglobal.io",
                "phone": "+1 (555) 234-8901",
                "company": "Apex Global Solutions",
                "lead_temperature": "HOT",
                "summary": "Urgent requirement for AI Voice agent to handle inbound qualification for 500+ daily leads. Budget approved.",
                "budget": "$25,000 - $50,000",
                "timeframe": "Immediate (This Week)",
                "intent": "Enterprise CRM & WebRTC Voice Integration",
                "sentiment_score": 0.94,
                "call_duration_seconds": 210,
                "recording_url": "https://actions.google.com/sounds/v1/ambiences/office_space.ogg",
                "transcript": "Agent: Thanks for calling VoiceLeads AI. How can I help today?\nMarcus: We are looking for an AI voice solution for our sales team to handle 500 daily inbound leads.",
                "status": "QUALIFIED",
                "synced_to_gsheets": True,
                "synced_to_n8n": True,
                "email_sent": True,
                "created_at": "2026-08-19 10:30:00"
            },
            {
                "id": "lead-102",
                "name": "Elena Rostova",
                "email": "elena.r@innovatetech.co",
                "phone": "+1 (555) 876-4321",
                "company": "InnovateTech Co.",
                "lead_temperature": "HOT",
                "summary": "Wants automated booking system integrated with Google Calendar and n8n webhooks. Requested callback from sales director.",
                "budget": "$10,000 - $25,000",
                "timeframe": "1-2 Weeks",
                "intent": "Automated Appointment Scheduling",
                "sentiment_score": 0.88,
                "call_duration_seconds": 165,
                "recording_url": "https://actions.google.com/sounds/v1/ambiences/office_space.ogg",
                "transcript": "Agent: Hi Elena, I can certainly check calendar availability for your team.\nElena: Perfect, we want to automate meeting bookings directly from incoming calls.",
                "status": "QUALIFIED",
                "synced_to_gsheets": True,
                "synced_to_n8n": True,
                "email_sent": True,
                "created_at": "2026-08-19 11:15:22"
            },
            {
                "id": "lead-103",
                "name": "David Sterling",
                "email": "dsterling@logisticsflow.net",
                "phone": "+1 (555) 432-9012",
                "company": "LogisticsFlow Net",
                "lead_temperature": "WARM",
                "summary": "Inquired about API pricing and customization features. Evaluating 2 other vendor options.",
                "budget": "$5,000 - $10,000",
                "timeframe": "1 Month",
                "intent": "API & Webhook Customization",
                "sentiment_score": 0.68,
                "call_duration_seconds": 130,
                "recording_url": None,
                "transcript": "David: What are your API call limits for the basic tier?\nAgent: We support scalable throughput up to 10,000 concurrent WebRTC calls.",
                "status": "CONTACTED",
                "synced_to_gsheets": True,
                "synced_to_n8n": False,
                "email_sent": True,
                "created_at": "2026-08-19 11:45:00"
            },
            {
                "id": "lead-104",
                "name": "Amanda Chen",
                "email": "amanda@solarpower.org",
                "phone": "+1 (555) 901-2345",
                "company": "SolarPower Direct",
                "lead_temperature": "COLD",
                "summary": "Calling to check if we provide customer support for residential hardware. Not aligned with B2B SaaS.",
                "budget": "N/A",
                "timeframe": "N/A",
                "intent": "Customer Support Inquiry",
                "sentiment_score": 0.35,
                "call_duration_seconds": 45,
                "recording_url": None,
                "transcript": "Amanda: Do you repair solar panel units?\nAgent: VoiceLeads AI is a voice automation platform for B2B lead generation.",
                "status": "ARCHIVED",
                "synced_to_gsheets": True,
                "synced_to_n8n": False,
                "email_sent": False,
                "created_at": "2026-08-19 12:10:05"
            }
        ]
        save_leads_to_file(initial_mock)
        return initial_mock
    try:
        with open(LEADS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading leads from file: {e}")
        return []

def save_leads_to_file(leads: List[dict]):
    try:
        with open(LEADS_FILE, "w", encoding="utf-8") as f:
            json.dump(leads, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving leads to file: {e}")

@router.get("", response_model=List[LeadResponse])
def get_leads(
    temperature: Optional[str] = Query(None, description="Filter by HOT, WARM, or COLD"),
    search: Optional[str] = Query(None, description="Search by name, company, email, or intent")
):
    leads = load_leads_from_file()
    
    if temperature:
        leads = [l for l in leads if l.get("lead_temperature", "").upper() == temperature.upper()]
    
    if search:
        s = search.lower()
        leads = [
            l for l in leads if
            s in l.get("name", "").lower() or
            s in l.get("company", "").lower() or
            s in (l.get("email") or "").lower() or
            s in (l.get("intent") or "").lower() or
            s in (l.get("summary") or "").lower()
        ]

    # Return sorted by newest first
    return sorted(leads, key=lambda x: x.get("created_at", ""), reverse=True)

@router.get("/stats", response_model=LeadStats)
def get_lead_stats():
    leads = load_leads_from_file()
    total = len(leads)
    hot = sum(1 for l in leads if l.get("lead_temperature") == "HOT")
    warm = sum(1 for l in leads if l.get("lead_temperature") == "WARM")
    cold = sum(1 for l in leads if l.get("lead_temperature") == "COLD")
    
    conversion = round((hot / total * 100), 1) if total > 0 else 0.0
    avg_dur = round(sum(l.get("call_duration_seconds", 0) for l in leads) / total, 1) if total > 0 else 0.0
    
    return LeadStats(
        total_leads=total,
        hot_leads=hot,
        warm_leads=warm,
        cold_leads=cold,
        conversion_rate=conversion,
        avg_call_duration_seconds=avg_dur
    )

@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(lead_id: str):
    leads = load_leads_from_file()
    for l in leads:
        if l["id"] == lead_id:
            return l
    raise HTTPException(status_code=404, detail="Lead not found")

from app.api.v1.n8n_relay import relay_to_n8n

@router.post("", response_model=LeadResponse)
async def create_lead(lead: LeadCreate):
    leads = load_leads_from_file()
    new_lead = lead.model_dump()
    new_lead["id"] = f"lead-{uuid.uuid4().hex[:6]}"
    new_lead["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_lead["synced_to_gsheets"] = False
    new_lead["synced_to_n8n"] = False
    new_lead["email_sent"] = False

    # Sync to GSheets & Email
    new_lead["synced_to_gsheets"] = google_sheets_service.sync_lead(new_lead)
    new_lead["email_sent"] = email_service.send_lead_notification(new_lead)
    
    try:
        n8n_res = await relay_to_n8n(new_lead)
        new_lead["synced_to_n8n"] = n8n_res.get("relayed", False)
    except Exception as e:
        logger.error(f"Error executing n8n relay: {e}")

    leads.append(new_lead)
    save_leads_to_file(leads)
    return new_lead

@router.put("/{lead_id}", response_model=LeadResponse)
def update_lead(lead_id: str, update: LeadUpdate):
    leads = load_leads_from_file()
    for idx, l in enumerate(leads):
        if l["id"] == lead_id:
            update_data = {k: v for k, v in update.model_dump().items() if v is not None}
            l.update(update_data)
            leads[idx] = l
            save_leads_to_file(leads)
            return l
    raise HTTPException(status_code=404, detail="Lead not found")

@router.delete("/{lead_id}")
def delete_lead(lead_id: str):
    leads = load_leads_from_file()
    filtered = [l for l in leads if l["id"] != lead_id]
    if len(filtered) == len(leads):
        raise HTTPException(status_code=404, detail="Lead not found")
    save_leads_to_file(filtered)
    return {"message": "Lead deleted successfully", "id": lead_id}

@router.post("/simulate-call", response_model=LeadResponse)
async def simulate_voice_call(
    name: str = "Jordan Lee",
    company: str = "Nexus Robotics",
    transcript: str = "Agent: VoiceLeads AI agent here. How can we support your team?\nCaller: We need an urgent AI solution for qualifying 200 leads a day with direct CRM synchronization and calendar booking.",
    summary: str = "Prospect requested urgent deployment of Voice AI agent for qualification."
):
    """Simulates an incoming Vapi call to test classification and workflow execution."""
    extraction = classifier_service.classify_transcript(transcript, summary)
    
    new_lead = {
        "id": f"lead-sim-{uuid.uuid4().hex[:4]}",
        "name": name if name else extraction.get("name", "Simulated Prospect"),
        "email": extraction.get("email") or f"{name.lower().replace(' ', '.')}@example.com",
        "phone": extraction.get("phone") or "+1 (555) 998-1122",
        "company": company if company else extraction.get("company", "Simulated Enterprise"),
        "lead_temperature": extraction.get("lead_temperature", "HOT"),
        "summary": extraction.get("summary", summary),
        "budget": extraction.get("budget", "$15,000"),
        "timeframe": extraction.get("timeframe", "Immediate"),
        "intent": extraction.get("intent", "WebRTC Calling & CRM Sync"),
        "sentiment_score": extraction.get("sentiment_score", 0.91),
        "call_duration_seconds": 180,
        "recording_url": "https://actions.google.com/sounds/v1/ambiences/office_space.ogg",
        "transcript": transcript,
        "status": "QUALIFIED",
        "synced_to_gsheets": False,
        "synced_to_n8n": False,
        "email_sent": False,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Dispatch integrations
    new_lead["synced_to_gsheets"] = google_sheets_service.sync_lead(new_lead)
    new_lead["email_sent"] = email_service.send_lead_notification(new_lead)

    try:
        n8n_res = await relay_to_n8n(new_lead)
        new_lead["synced_to_n8n"] = n8n_res.get("relayed", False)
    except Exception as e:
        logger.error(f"Error triggering n8n relay during simulation: {e}")

    leads = load_leads_from_file()
    leads.append(new_lead)
    save_leads_to_file(leads)
    return new_lead
