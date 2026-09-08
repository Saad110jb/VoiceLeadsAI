from fastapi import APIRouter, HTTPException
import httpx
from typing import Dict, Any
from datetime import datetime, timedelta

from app.config import settings
from app.utils.logger import logger

router = APIRouter(prefix="/n8n", tags=["n8n Automation Relay"])

@router.post("/relay")
async def relay_to_n8n(payload: Dict[str, Any]):
    """
    Relays structured lead data to n8n workflow webhook endpoint.
    Formats timestamps and headers to match Google Calendar & Google Sheet nodes.
    """
    webhook_url = settings.N8N_WEBHOOK_URL
    
    # Calculate ISO StartTime & EndTime for Google Calendar node
    now = datetime.now()
    tomorrow_start = (now + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
    tomorrow_end = tomorrow_start + timedelta(hours=1)

    # Format payload with both n8n & Google Sheet column schemas
    enriched_payload = {
        **payload,
        # Google Calendar required fields
        "startTime": payload.get("startTime") or tomorrow_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "endTime": payload.get("endTime") or tomorrow_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "start_time": tomorrow_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
        
        # Google Sheet 'lead_tracker' exact headers (Image 3)
        "Name": payload.get("name") or payload.get("Name") or "Prospect",
        "Email": payload.get("email") or payload.get("Email") or "N/A",
        "Phone": payload.get("phone") or payload.get("Phone") or "N/A",
        "Service": payload.get("intent") or payload.get("company") or "Voice Qualification",
        "Status": payload.get("lead_temperature") or payload.get("status") or "HOT",
        "Summary": payload.get("summary") or payload.get("notes") or "Inbound Voice Qualification Call",
        "notes": payload.get("summary") or "Inbound Voice Qualification Call",
        "Slot": payload.get("timeframe") or "10:00 AM EST",
        "Recording": payload.get("recording_url") or payload.get("recordingUrl") or "",
        "Timestamp": payload.get("created_at") or now.strftime("%Y-%m-%d %H:%M:%S")
    }

    initiate_call = payload.get("initiate_call", True)
    target_phone = payload.get("phone") or payload.get("Phone")
    call_result = None

    if initiate_call and target_phone:
        try:
            from app.api.v1.vapi_webhook import make_outbound_phone_call
            logger.info(f"n8n Relay triggered! Automatically initiating Vapi outbound call to {target_phone}")
            call_result = await make_outbound_phone_call({"phone_number": target_phone})
        except Exception as call_err:
            logger.warning(f"Auto outbound call from n8n relay failed: {call_err}")
            call_result = {"status": "failed", "error": str(call_err)}

    if not webhook_url or "your-n8n-instance" in webhook_url:
        logger.info("Default placeholder n8n webhook URL used. Simulating successful relay.")
        return {
            "status": "success",
            "relayed": True,
            "mode": "simulation",
            "message": "n8n relay simulation successful.",
            "outbound_call": call_result,
            "payload": enriched_payload
        }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(webhook_url, json={**enriched_payload, "initiate_call": initiate_call})
            response.raise_for_status()
            logger.info(f"Successfully relayed enriched lead payload to n8n webhook: {webhook_url}")
            return {
                "status": "success",
                "relayed": True,
                "n8n_status_code": response.status_code,
                "outbound_call": call_result,
                "response": response.json() if response.headers.get("content-type") == "application/json" else response.text
            }
    except Exception as e:
        logger.error(f"Failed to relay payload to n8n webhook: {e}")
        raise HTTPException(status_code=502, detail=f"Error forwarding payload to n8n: {str(e)}")
