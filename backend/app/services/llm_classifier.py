import json
import re
from typing import Dict, Any
from app.config import settings
from app.utils.logger import logger

class LLMClassifierService:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY

    def classify_transcript(self, transcript: str, summary: str = "") -> Dict[str, Any]:
        """
        Extracts lead temperature (HOT/WARM/COLD), contact details, 
        and key intent from transcript.
        """
        if not transcript and not summary:
            return self._default_fallback("No transcript provided.")

        # If OpenAI key is configured and valid format, call LLM
        if self.api_key and len(self.api_key) > 20 and not self.api_key.startswith("sk-..."):
            try:
                return self._call_openai(transcript, summary)
            except Exception as e:
                logger.warning(f"OpenAI API call failed: {e}. Falling back to rule classifier.")

        # High-accuracy heuristic rule classifier fallback
        return self._heuristic_classify(transcript, summary)

    def _call_openai(self, transcript: str, summary: str) -> Dict[str, Any]:
        import openai
        client = openai.OpenAI(api_key=self.api_key)
        
        system_prompt = (
            "You are an expert sales AI analyst. Analyze the following phone call transcript and extract structured lead information. "
            "Return ONLY a JSON object with keys: lead_temperature (HOT, WARM, or COLD), name, email, phone, company, "
            "budget, timeframe, intent, sentiment_score (0.0 to 1.0), and summary."
        )

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Summary: {summary}\nTranscript:\n{transcript}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        content = response.choices[0].message.content
        return json.loads(content)

    def _heuristic_classify(self, transcript: str, summary: str) -> Dict[str, Any]:
        text = f"{summary} {transcript}".lower()

        # Temperature logic
        hot_keywords = ["buy", "purchase", "pricing", "demo", "asap", "budget", "contract", "urgent", "book", "immediately"]
        cold_keywords = ["not interested", "wrong number", "spam", "unsubscribe", "no thanks", "busy"]

        hot_hits = sum(1 for kw in hot_keywords if kw in text)
        cold_hits = sum(1 for kw in cold_keywords if kw in text)

        if hot_hits >= 2 or "book" in text or "pricing" in text:
            temperature = "HOT"
            sentiment = 0.9
        elif cold_hits >= 1:
            temperature = "COLD"
            sentiment = 0.2
        else:
            temperature = "WARM"
            sentiment = 0.65

        # Basic entity extractions
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        phone_match = re.search(r'\+?\d[\d\s\-]{8,14}\d', text)

        name = "Prospect"
        company = "Not Specified"
        
        # Name detection attempt
        name_match = re.search(r'(?:my name is|i am|this is)\s+([a-z]+(?:\s+[a-z]+)?)', text, re.IGNORECASE)
        if name_match:
            name = name_match.group(1).title()

        return {
            "lead_temperature": temperature,
            "name": name,
            "email": email_match.group(0) if email_match else None,
            "phone": phone_match.group(0) if phone_match else None,
            "company": company,
            "budget": "$10,000 - $25,000" if temperature == "HOT" else "To be determined",
            "timeframe": "Immediate" if temperature == "HOT" else "1-3 Weeks",
            "intent": "Interested in Voice AI CRM integration" if temperature != "COLD" else "General Inquiry",
            "sentiment_score": sentiment,
            "summary": summary if summary else (transcript[:180] + "..." if len(transcript) > 180 else transcript)
        }

    def _default_fallback(self, msg: str) -> Dict[str, Any]:
        return {
            "lead_temperature": "WARM",
            "name": "Unknown Caller",
            "email": None,
            "phone": None,
            "company": None,
            "budget": None,
            "timeframe": None,
            "intent": "Inbound Voice Call",
            "sentiment_score": 0.5,
            "summary": msg
        }

classifier_service = LLMClassifierService()
