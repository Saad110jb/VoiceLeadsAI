import json
import os
from typing import Dict, Any, List
from app.config import settings
from app.utils.logger import logger

class GoogleSheetsService:
    def __init__(self):
        self.service_account_file = settings.GOOGLE_SERVICE_ACCOUNT_FILE
        self.sheet_name = settings.GOOGLE_SHEET_NAME
        self.client = None
        self._init_client()

    def _init_client(self):
        """Initializes gspread client if credentials exist."""
        if not os.path.exists(self.service_account_file):
            logger.info(f"Service account file '{self.service_account_file}' not found. Using local JSON fallback for GSheets.")
            return

        # Check for placeholder credentials to avoid PEM cryptography parse crash
        try:
            with open(self.service_account_file, "r", encoding="utf-8") as f:
                content = f.read()
                if "sample_key_id" in content or "MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC" in content:
                    logger.info("Notice: service_account.json contains placeholder credentials. Direct GSheets sync deferred to n8n workflow or valid service account key.")
                    self.client = None
                    return
        except Exception:
            pass

        try:
            import gspread
            if hasattr(gspread, 'service_account'):
                self.client = gspread.service_account(filename=self.service_account_file)
            else:
                from google.oauth2.service_account import Credentials
                scope = [
                    "https://spreadsheets.google.com/feeds",
                    "https://www.googleapis.com/auth/drive"
                ]
                creds = Credentials.from_service_account_file(self.service_account_file, scopes=scope)
                self.client = gspread.authorize(creds)
            logger.info("Successfully connected to Google Sheets API.")
        except Exception as e:
            logger.warning(f"Google Sheets authentication notice: {e}. Operating in local JSON fallback mode.")
            self.client = None

    def sync_lead(self, lead: Dict[str, Any]) -> bool:
        """Appends a qualified lead row matching lead_tracker columns: Name, Email, Phone, Service, Status, Summary, Slot, Recording, Timestamp."""
        row_data = [
            lead.get("name", "N/A"),
            lead.get("email", "N/A"),
            lead.get("phone", "N/A"),
            lead.get("intent", lead.get("company", "Voice Qualification")),
            lead.get("lead_temperature", "WARM"),
            lead.get("summary", ""),
            lead.get("timeframe", "10:00 AM EST"),
            lead.get("recording_url", ""),
            lead.get("created_at", "")
        ]

        if self.client:
            try:
                sheet = self.client.open(self.sheet_name).sheet1
                sheet.append_row(row_data)
                logger.info(f"Lead '{lead.get('name')}' appended to Google Sheet '{self.sheet_name}'.")
                return True
            except Exception as e:
                logger.error(f"Error appending to Google Sheet '{self.sheet_name}': {e}. Writing to fallback file.")

        # Fallback local persistence
        return self._write_to_backup_log(lead)

    def _write_to_backup_log(self, lead: Dict[str, Any]) -> bool:
        backup_path = "leads_gsheet_backup.json"
        leads_list = []

        if os.path.exists(backup_path):
            try:
                with open(backup_path, "r", encoding="utf-8") as f:
                    leads_list = json.load(f)
            except Exception:
                leads_list = []

        leads_list.append(lead)

        try:
            with open(backup_path, "w", encoding="utf-8") as f:
                json.dump(leads_list, f, indent=2)
            logger.info(f"Lead '{lead.get('name')}' saved to GSheets local backup: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to write lead to backup file: {e}")
            return False

google_sheets_service = GoogleSheetsService()
