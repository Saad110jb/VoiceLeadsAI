from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any
import uuid
from datetime import datetime

from app.config import settings
from app.services.llm_classifier import classifier_service
from app.services.email_service import email_service
from app.services.google_sheets import google_sheets_service
from app.api.v1.leads import load_leads_from_file, save_leads_to_file
from app.api.v1.n8n_relay import relay_to_n8n
from app.utils.logger import logger

router = APIRouter(prefix="/vapi", tags=["Vapi Webhook"])

@router.post("/call-phone")
async def make_outbound_phone_call(payload: Dict[str, Any]):
    """
    Triggers an outbound Vapi AI phone call to a given phone number.
    """
    phone_number = payload.get("phone_number")
    assistant_id = payload.get("assistant_id") or settings.VAPI_ASSISTANT_ID
    vapi_key = settings.VAPI_API_KEY

    if not phone_number:
        raise HTTPException(status_code=400, detail="phone_number is required (e.g. '+15551234567')")

    if not vapi_key or vapi_key == "your_vapi_private_key":
        logger.info(f"Vapi API key missing. Simulating outbound call to {phone_number}.")
        return {
            "status": "simulation",
            "message": f"Simulated outbound phone call initiated to {phone_number}. (Set VAPI_API_KEY in backend/.env to trigger live Vapi telephony)",
            "phone_number": phone_number,
            "assistant_id": assistant_id
        }

    import httpx
    url = "https://api.vapi.ai/call/phone"
    headers = {
        "Authorization": f"Bearer {vapi_key}",
        "Content-Type": "application/json"
    }
    phone_number_id = payload.get("phone_number_id") or settings.VAPI_PHONE_NUMBER_ID
    fallback_phone = settings.VAPI_PHONE_NUMBER or "+14422461201"

    body = {
        "assistantId": assistant_id,
        "customer": {
            "number": phone_number
        }
    }

    # Validate if phone_number_id is a complete 36-character UUID
    valid_uuid = False
    if phone_number_id:
        try:
            uuid.UUID(phone_number_id)
            valid_uuid = True
        except ValueError:
            valid_uuid = False

    if valid_uuid:
        body["phoneNumberId"] = phone_number_id
    elif fallback_phone:
        body["phoneNumber"] = {
            "twilioPhoneNumber": fallback_phone,
            "twilioAccountSid": "AC_VAPI_DEFAULT"
        }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(url, json=body, headers=headers)
            response.raise_for_status()
            logger.info(f"Successfully initiated Vapi outbound phone call to {phone_number}")
            return {
                "status": "success",
                "vapi_response": response.json()
            }
    except httpx.HTTPStatusError as exc:
        err_detail = exc.response.text
        logger.error(f"Vapi API returned status {exc.response.status_code}: {err_detail}")
        raise HTTPException(status_code=400, detail=f"Vapi API error: {err_detail}")
    except Exception as e:
        logger.error(f"Error calling Vapi Outbound API: {e}")
        raise HTTPException(status_code=500, detail=f"Vapi call failed: {str(e)}")

@router.post("/webhook")
async def handle_vapi_webhook(request: Request):
    """
    Primary webhook endpoint configured in Vapi Dashboard.
    Handles tool function calls (e.g. check_availability) and end-of-call data payloads.
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    message = body.get("message", body)
    msg_type = message.get("type", "")

    logger.info(f"Received Vapi Webhook event type: '{msg_type}'")

    # 1. Handle Vapi Function / Tool Calls
    if msg_type == "tool-calls" or msg_type == "function-call":
        return await _handle_tool_call(message)

    # 2. Handle End of Call Report
    if msg_type == "end-of-call-report":
        return await _handle_end_of_call(message)

    # 3. Status updates or transcripts
    return {"status": "received", "event_type": msg_type}

async def _handle_tool_call(message: Dict[str, Any]) -> Dict[str, Any]:
    tool_calls = message.get("toolCallList", []) or [message.get("functionCall")]
    results = []

    for tool in tool_calls:
        if not tool:
            continue
        tool_id = tool.get("id", "call_1")
        func_info = tool.get("function", tool)
        func_name = func_info.get("name", "")
        params = func_info.get("arguments", func_info.get("parameters", {}))

        if isinstance(params, str):
            import json
            try:
                params = json.loads(params)
            except Exception:
                params = {}

        logger.info(f"Processing Vapi Tool Call '{func_name}' with parameters: {params}")

        if func_name == "check_availability":
            date = params.get("date", "Tomorrow")
            result_payload = {
                "available": True,
                "date": date,
                "slots": ["10:00 AM EST", "02:00 PM EST", "04:30 PM EST"],
                "message": f"Slots are available for {date} at 10:00 AM, 2:00 PM, and 4:30 PM EST."
            }
        elif func_name == "book_appointment":
            name = params.get("name", "Prospect")
            time = params.get("time_slot", "10:00 AM EST")
            result_payload = {
                "success": True,
                "confirmation_id": f"CAL-{uuid.uuid4().hex[:6].upper()}",
                "message": f"Appointment confirmed for {name} at {time}."
            }
        else:
            result_payload = {"status": "success", "message": f"Tool {func_name} executed."}

        results.append({
            "toolCallId": tool_id,
            "result": result_payload
        })

    return {"results": results}

async def _handle_end_of_call(message: Dict[str, Any]) -> Dict[str, Any]:
    call_data = message.get("call", {})
    artifact = message.get("artifact", {})
    analysis = message.get("analysis", {})

    transcript = artifact.get("transcript") or call_data.get("transcript") or ""
    summary = analysis.get("summary") or call_data.get("summary") or ""
    recording_url = artifact.get("recordingUrl") or call_data.get("recordingUrl")

    # Run AI Classification & Entity Extraction
    extracted = classifier_service.classify_transcript(transcript, summary)

    new_lead = {
        "id": f"lead-{uuid.uuid4().hex[:6]}",
        "name": extracted.get("name", "Vapi Prospect"),
        "email": extracted.get("email"),
        "phone": extracted.get("phone"),
        "company": extracted.get("company"),
        "lead_temperature": extracted.get("lead_temperature", "WARM"),
        "summary": extracted.get("summary", summary),
        "budget": extracted.get("budget"),
        "timeframe": extracted.get("timeframe"),
        "intent": extracted.get("intent", "Inbound Call"),
        "sentiment_score": extracted.get("sentiment_score", 0.75),
        "call_duration_seconds": call_data.get("duration", 120),
        "recording_url": recording_url,
        "transcript": transcript,
        "status": "QUALIFIED" if extracted.get("lead_temperature") in ["HOT", "WARM"] else "NEW",
        "synced_to_gsheets": False,
        "synced_to_n8n": False,
        "email_sent": False,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Execute Sync Integrations
    new_lead["synced_to_gsheets"] = google_sheets_service.sync_lead(new_lead)
    new_lead["email_sent"] = email_service.send_lead_notification(new_lead)

    try:
        n8n_res = await relay_to_n8n(new_lead)
        new_lead["synced_to_n8n"] = n8n_res.get("relayed", False)
    except Exception as e:
        logger.error(f"Error triggering n8n relay: {e}")

    # Save to CRM persistence
    leads = load_leads_from_file()
    leads.append(new_lead)
    save_leads_to_file(leads)

    return {
        "status": "success",
        "message": "Call report processed and lead created.",
        "lead_id": new_lead["id"],
        "temperature": new_lead["lead_temperature"]
    }
