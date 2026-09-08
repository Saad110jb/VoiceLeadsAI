# 🎙️ VoiceLeads AI (VocalSync CRM)

> An Autonomous Voice AI Lead Generation, WebRTC Inbound/Outbound Caller, and Automated CRM Sync Pipeline.

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.11+-emerald.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0-009688.svg)
![React](https://img.shields.io/badge/React-18.2.0-61DAFB.svg)
![Vite](https://img.shields.io/badge/Vite-5.0.0-646CFF.svg)
![Vapi](https://img.shields.io/badge/Vapi-WebRTC_Voice_AI-purple.svg)
![n8n](https://img.shields.io/badge/n8n-Workflow_Automation-FF6D5A.svg)

---

## 📌 Executive Summary

**VoiceLeads AI (VocalSync CRM)** is a complete, full-stack voice-powered lead generation and CRM automation platform. It allows users to conduct real-time AI voice conversations directly in the browser via WebRTC (or over outbound phone calls), automatically extract prospect details (name, email, company, budget, timeframe, intent), compute AI lead qualification scores (HOT, WARM, COLD), and instantly synchronize leads across Google Sheets, SMTP Email notifications, n8n automation workflows, and a live web CRM dashboard.

---

## 🧰 Technologies & Tools Used ("What Things Are Used In It")

### 1. **Frontend Architecture**
- **[React 18](https://react.dev/)**: Component-based UI library for building the CRM web application.
- **[Vite](https://vitejs.dev/)**: Next-generation frontend build tool providing instant HMR and optimized production bundles.
- **`@vapi-ai/web`**: WebRTC browser SDK used to initiate, manage, and render real-time interactive voice calls with Vapi AI agents.
- **[Tailwind CSS](https://tailwindcss.com/)**: Utility-first CSS framework for modern responsive UI styling.
- **[Lucide React](https://lucide.dev/)**: Icon library for UI elements (mikes, call controls, lead temperature indicators, filters).
- **[Axios](https://axios-http.com/)**: Promise-based HTTP client for API communication between the React app and FastAPI backend.

### 2. **Backend Microservice**
- **[Python 3.11+](https://www.python.org/)**: Core programming language.
- **[FastAPI](https://fastapi.tiangolo.com/)**: High-performance, asynchronous web framework for building microservice endpoints and webhook ingestion handlers.
- **[Uvicorn](https://www.uvicorn.org/)**: Lightning-fast ASGI server implementation for async Python applications.
- **[Pydantic v2](https://docs.pydantic.dev/)**: Data validation and settings management using Python type hints.
- **[HTTPX](https://www.python-httpx.org/)**: Fully async HTTP client for outbound API requests (Vapi Telephony API & n8n webhook triggers).
- **[Pytest](https://docs.pytest.org/)**: Automated unit and integration testing suite for backend routers and services.

### 3. **AI Engine & Telephony**
- **[Vapi AI](https://vapi.ai/)**: Voice AI engine providing real-time WebRTC audio streaming, text-to-speech, speech-to-text, assistant context management, and phone call dispatching.
- **[OpenAI GPT API](https://openai.com/)**: Large Language Model integration for automated transcript analysis, entity extraction, sentiment analysis, and lead temperature scoring.

### 4. **Workflow & Automation Engine**
- **[n8n](https://n8n.io/)**: Self-hosted/cloud workflow automation tool.
- **Pre-configured Workflows**:
  - `vapi_lead_sync_workflow.json`: Automated webhook relay for qualified leads.
  - `calendar_booking_flow.json`: Calendar slot checking and automated meeting booking logic.

### 5. **Data Persistence & Integrations**
- **[Google Sheets API (`gspread`)](https://docs.gspread.org/)**: Real-time spreadsheet synchronization for lead logging with service account authentication (`oauth2client`).
- **SMTP Email Dispatcher**: Native Python `smtplib` implementation for instant, rich HTML email notifications sent to sales team leads via Gmail App Passwords.
- **JSON File Storage**: Local persistent fallback data storage (`leads.json`) ensuring zero data loss if external APIs are unreachable.

### 6. **DevOps & Infrastructure**
- **[Docker & Docker Compose](https://www.docker.com/)**: Multi-container orchestration powering the FastAPI backend service and self-hosted n8n instance concurrently.

---

## ⚡ What Is Happening In It (System Architecture & Flow)

```text
               +--------------------------------------------------+
               |  User / Prospect (WebRTC Browser / Phone Call)    |
               +------------------------+-------------------------+
                                        |
                   Real-time Voice Stream (Vapi WebRTC SDK)
                                        v
               +--------------------------------------------------+
               |           Vapi Voice AI Assistant Engine         |
               | (Executes System Prompts & Function Tool Calls)   |
               +------------------------+-------------------------+
                                        |
               Webhook Payloads: tool-calls / end-of-call-report
                                        v
               +--------------------------------------------------+
               |           FastAPI Microservice (Port 8000)       |
               +---+--------------------+---------------------+---+
                   |                    |                     |
                   v                    v                     v
          +-----------------+  +------------------+  +-------------------+
          | LLM Classifier  |  | Google Sheets    |  | SMTP Email Alert  |
          | Entity Extraction| | (gspread Sync)   |  | (Sales Manager)   |
          +-----------------+  +------------------+  +-------------------+
                   |
                   v
          +-----------------+
          | n8n Automation  |
          | Workflow Relay  |
          +-----------------+
                   |
                   v
          +--------------------------------------------------+
          |           React CRM Dashboard (Port 3000)        |
          |  (Live Stats, Audio Player, CSV Export, Filters) |
          +--------------------------------------------------+
```

### End-to-End Lifecycle of a Voice Lead:

1. **Voice Conversation**:
   - The prospect opens the web app and clicks **"Start AI Voice Call"** (or receives an outbound AI phone call).
   - `@vapi-ai/web` establishes a WebRTC audio connection to Vapi AI.

2. **Real-time AI Tool Execution**:
   - As the conversation occurs, Vapi can call backend function webhooks like `check_availability` or `book_appointment` to query available time slots and confirm meeting bookings live on the call.

3. **Call Completion & Webhook Ingestion**:
   - When the user hangs up, Vapi sends an `end-of-call-report` webhook payload containing the audio recording URL, duration, and full conversation transcript to FastAPI `/api/v1/vapi/webhook`.

4. **AI Entity Extraction & Lead Scoring**:
   - FastAPI passes the transcript to `LLMClassifierService` (powered by OpenAI).
   - Extracted fields: **Name, Email, Phone, Company, Budget, Timeframe, Primary Intent, Sentiment Score**.
   - Lead Temperature Scoring:
     - **HOT**: High budget, immediate timeframe, strong intent.
     - **WARM**: Expressed interest, moderate budget/timeframe.
     - **COLD**: Low intent, general inquiry, or budget mismatch.

5. **Multi-Channel Synchronized Pipeline**:
   - **Google Sheets**: Appends the lead data row directly to Google Sheets.
   - **SMTP Email Alert**: Generates an HTML notification email and dispatches it to sales reps.
   - **n8n Relay**: Posts structured lead JSON to the n8n automation engine for secondary workflows (CRM sync, Slack alerts, calendar invites).
   - **CRM Persistence**: Saves the lead into the local CRM database (`leads.json`).

6. **Interactive CRM Dashboard View**:
   - The React frontend fetches `/api/v1/leads` and presents:
     - Total Leads, Qualified Leads, Hot Leads, and Average Sentiment metrics.
     - Interactive filterable lead table (by Temperature & Search query).
     - Audio player component to listen to call recording URLs.
     - CSV export functionality for reporting.

---

## 📂 File & Directory Structure

```text
VoiceLeads AI/
├── automations/
│   ├── n8n_workflows/
│   │   ├── calendar_booking_flow.json      # n8n workflow for calendar slot booking
│   │   └── vapi_lead_sync_workflow.json    # n8n workflow for lead sync automation
│   └── vapi_prompts/
│       ├── system_prompt.md                # Vapi Assistant system instructions
│       └── tool_definitions.json           # Vapi function tool definitions
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── leads.py                # CRUD endpoints for leads & CSV export
│   │   │       ├── n8n_relay.py            # Async HTTP relay to n8n webhooks
│   │   │       └── vapi_webhook.py         # Handles tool-calls & end-of-call reports
│   │   ├── services/
│   │   │   ├── email_service.py            # SMTP HTML email dispatcher
│   │   │   ├── google_sheets.py            # Google Sheets API gspread integration
│   │   │   └── llm_classifier.py          # OpenAI GPT transcript entity extraction
│   │   ├── schemas/                        # Pydantic schemas for payload validation
│   │   ├── config.py                       # Application settings & environment loader
│   │   └── main.py                         # FastAPI app entry point & CORS configuration
│   ├── tests/                              # Pytest suite for webhooks and lead routes
│   ├── Dockerfile                          # Docker configuration for backend container
│   ├── requirements.txt                    # Python dependencies
│   └── run.py                              # Backend startup runner script
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── CallAudioPlayer.jsx         # Custom audio player for Vapi recordings
│   │   │   ├── LeadTable.jsx               # Searchable & filterable lead table
│   │   │   ├── Navbar.jsx                  # Header navigation component
│   │   │   ├── StatsOverview.jsx           # CRM dashboard metrics cards
│   │   │   └── VoiceCallButton.jsx         # WebRTC voice call controller & visualizer
│   │   ├── hooks/
│   │   │   ├── useLeads.js                 # Custom hook for lead data fetching & filters
│   │   │   └── useVapi.js                  # Custom hook for Vapi WebRTC SDK state
│   │   ├── services/
│   │   │   └── api.js                      # Axios HTTP client configuration
│   │   ├── App.jsx                         # Main React layout component
│   │   └── main.jsx                        # React root renderer
│   ├── package.json                        # Frontend dependencies & scripts
│   └── vite.config.js                      # Vite server configuration
├── docker-compose.yml                      # Container orchestration (FastAPI + n8n)
└── README.md                               # Project documentation
```

---

## 🛠️ Quickstart Setup Guide

### 1. Prerequisites
- **Python**: 3.10+
- **Node.js**: 18+ & npm
- **Docker & Docker Compose** (Optional, for containerized run)
- **Vapi API Account & Public Key** (Required for live voice calls)
- **OpenAI API Key** (Required for GPT entity extraction)

---

### 2. Environment Variables Configuration

#### Backend `.env` (`backend/.env`)
```env
PORT=8000
ENVIRONMENT=development

# OpenAI Credentials
OPENAI_API_KEY=sk-your-openai-api-key

# Vapi Credentials
VAPI_API_KEY=your_vapi_private_key
VAPI_ASSISTANT_ID=your_vapi_assistant_id
VAPI_PHONE_NUMBER_ID=your_vapi_phone_number_id

# n8n Automation Integration
N8N_WEBHOOK_URL=http://localhost:5678/webhook/vapi-call-complete

# SMTP Email Notification Credentials
SENDER_EMAIL=your_email@gmail.com
SENDER_APP_PASSWORD=your_gmail_app_password
NOTIFICATION_RECEIVER=sales_manager@gmail.com

# Google Sheets Configuration
GOOGLE_SERVICE_ACCOUNT_FILE=service_account.json
GOOGLE_SHEET_NAME=Leads Tracker
```

#### Frontend `.env` (`frontend/.env`)
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_VAPI_PUBLIC_KEY=your_vapi_public_key
VITE_VAPI_ASSISTANT_ID=your_vapi_assistant_id
```

---

### 3. Running Backend (FastAPI)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate environment (Windows)
venv\Scripts\activate
# Activate environment (Linux/macOS)
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Launch FastAPI server
python run.py
```
- API Server runs at **`http://localhost:8000`**
- Interactive Swagger API Docs available at **`http://localhost:8000/docs`**

---

### 4. Running Frontend (React + Vite)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```
- Web Application opens at **`http://localhost:3000`**

---

### 5. Running via Docker Compose

Launch both the **FastAPI Backend Microservice** and **Self-Hosted n8n Engine** simultaneously:

```bash
docker-compose up --build -d
```
- FastAPI Backend: `http://localhost:8000`
- n8n Automation Console: `http://localhost:5678`

---

## 📡 API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Server health check and timestamp |
| `POST` | `/api/v1/vapi/webhook` | Handles Vapi tool calls and end-of-call report payloads |
| `POST` | `/api/v1/vapi/call-phone` | Initiates an outbound AI phone call to a given phone number |
| `GET` | `/api/v1/leads` | Fetches all stored CRM leads (supports search & temperature query filters) |
| `GET` | `/api/v1/leads/stats` | Returns calculated CRM statistics (Total, Qualified, Hot, Avg Sentiment) |
| `GET` | `/api/v1/leads/export/csv` | Downloads all leads formatted as a CSV spreadsheet file |
| `DELETE` | `/api/v1/leads/{lead_id}` | Deletes a specific lead from CRM storage |
| `POST` | `/api/v1/n8n/trigger-webhook` | Manually triggers the n8n automation relay for a specific lead |

---

## 🧪 Testing & Verification

Run automated pytest unit tests:

```bash
cd backend
pytest tests/test_webhooks.py tests/test_leads.py
```

---

## 📄 License

This project is open-source software licensed under the [MIT License](LICENSE).
