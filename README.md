# 📅 EfficioMCP – Smart Calendar Assistant

EfficioMCP is an intelligent AI-powered assistant built with [LangGraph](https://github.com/langchain-ai/langgraph), [Google Calendar API](https://developers.google.com/calendar), and [MCP](https://github.com/mcptools) to help you manage your schedule through natural conversation.

It understands human-friendly date expressions like "today", "next Friday", "tomorrow at 3pm", and translates them into actionable calendar tasks.

---

## 🚀 Features

* ✅ Check your schedule by asking "What’s on my calendar today?"
* 🕐 Schedule events naturally like "Create an event next Monday at 2pm called Meeting"
* 📆 Automatically parses dates like "July 21st, 3pm"
* 🧠 Remembers the last 5 user and assistant messages for better context
* 🌐 Uses Google Calendar API (via Service Account)

---

## 🔧 Tech Stack

* Python 3.9+
* LangGraph (via LangChain)
* MCP (Message Chain Protocol)
* Google Calendar API
* Gemini LLM (via `langchain_google_genai`)
* `dateutil` for smart date parsing

---

## 🧹 Folder Structure

```
EfficioMCP/
├── calendar_client.py       # The LangGraph-based AI client interface
├── calendar_server.py       # The MCP tool server using Google Calendar API
├── .env                     # Environment variables for credentials
└── credentials.json         # Google service account credentials
```

---

## ✅ Setup Instructions

### 1. Clone this repository

```bash
git clone https://github.com/your-username/EfficioMCP.git
cd EfficioMCP
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` is missing, you can install manually:

```bash
pip install python-dotenv langchain langgraph mcp langchain-google-genai google-api-python-client google-auth python-dateutil
```

### 3. Set up Google Calendar API

#### a. Create a Service Account:

* Go to [Google Cloud Console](https://console.cloud.google.com/)
* Create a new project or use existing one
* Go to **IAM & Admin > Service Accounts**
* Create a new service account and download `credentials.json`

#### b. Enable Calendar API:

* In Google Cloud Console > APIs & Services > Library
* Enable **Google Calendar API** for your project

#### c. Share your calendar:

* Open [Google Calendar](https://calendar.google.com/)
* Under **My calendars**, click **Settings & sharing**
* Add the service account’s email (from `credentials.json`) with **Make changes and manage sharing** permission

### 4. Create a `.env` file

Create a `.env` file in the root directory:

```
GOOGLE_API_CREDENTIALS_PATH=credentials.json
CALENDAR_ID=primary
```

> `CALENDAR_ID` can be a calendar ID or `"primary"` for your main calendar.

---

## ▶️ Run the Assistant

```bash
python calendar_client.py
```

You’ll see:

```
🔔 Agent ready. Ask about your calendar (type 'exit' to quit).
You:
```

Now you can start chatting!

---

## 💬 Supported Prompts

```bash
You: what is my schedule today?
You: do I have anything tomorrow at 2pm?
You: schedule event called Project Demo on July 22 at 4pm
You: cancel event with ID abc123
You: find a free 60-minute slot tomorrow after 10am
```

---

## ⚙️ Customization

* You can change the LLM model inside `calendar_client.py` by modifying:

```python
ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-05-20")
```

* Modify date parsing rules in the `parse_date_time()` function to support more phrases.

---

## 💠 Troubleshooting

**❌ I don’t see the event in Google Calendar**

* Ensure time zone is specified in the API call (`Asia/Dhaka` for GMT+6)
* Confirm that the correct calendar ID is used
* Make sure the service account is **shared** on the calendar
* Check if the event is in a different timezone (UTC vs GMT+6)

**❌ Time parsing errors**

* Install `dateutil`: `pip install python-dateutil`
* Avoid ambiguous date phrases (e.g., “next month”)

---

---

## 🤛🏼 Author

**Sadman Labib**
Efficio AI Calendar Project – JavaFest Hackathon

---
