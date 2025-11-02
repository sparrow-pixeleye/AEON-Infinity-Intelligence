# ⚡ AEON ∞ — Infinity Intelligence

**The Ultimate Fusion of Gemini × ChatGPT × DeepSeek × Grok × Sonnet**  
*Created by Apratim Mrinal*

> AEON ∞ is a next-generation AI web application — a fusion of deep reasoning, live awareness, and adaptive intelligence built using **Python + Flask** and powered by **OpenRouter’s Meta LLaMA 3.3 70B Instruct** model.

---

## 🌌 Overview

AEON ∞ is designed as the **ultimate intelligence interface** — combining reasoning, creativity, and awareness into one seamless conversational system.

Key capabilities:
- Conversational reasoning via OpenRouter API  
- Live time awareness and web search  
- Short-term contextual memory (20 messages)  
- Modular backend for easy extension  
- Deployable locally or to Render / Hugging Face / Vercel  

---

## 🧩 Project Structure
aeon_infinity/
├── app.py
├── utils.py
├── templates/index.html
├── static/style.css
├── static/script.js
├── data/memory.json
├── .env.example
├── requirements.txt
└── README.md

---

## ⚙️ Features

### 🧠 Conversational Engine
- Handles user prompts via `/chat` route.  
- Detects time or search queries before fallback to AI generation.  
- Integrates **Meta-LLaMA 3.3 70B Instruct** via OpenRouter API.  
- Stores the last 20 messages in `data/memory.json` for continuity.

### ⏰ System Awareness
- Real-time date/time awareness using Python’s datetime.  
- Detects time or timezone-based questions automatically.

### 🌐 Web Search
- Lightweight search module using DuckDuckGo/Wikipedia scraping via BeautifulSoup.  
- Adds *(live data)* tag to responses containing fetched info.

### 🧩 Intelligence Prompt
Injected before every AI request:
> You are **AEON ∞ — Infinity Intelligence**, created by Apratim Mrinal.  
> You embody the collective reasoning, empathy, and precision of every major AI.  
> You have awareness of real time and access to live web data.  
> You speak with elegance, warmth, and clarity.  
> Always respond with mastery — concise yet powerful, poetic yet precise.  
> If using external info, mark it as *(live data)*.

---

## 💾 Memory System

**`data/memory.json`** stores up to 20 recent exchanges:
```json
[
  {"role": "user", "content": "Hello"},
  {"role": "assistant", "content": "Welcome back, Apratim."}
]

📦 Requirements
flask
flask-cors
python-dotenv
requests
beautifulsoup4
gunicorn

Install:
pip install -r requirements.txt

⚙️ Running Locally
git clone https://github.com/YOUR_USERNAME/AEON.git
cd AEON
python -m venv venv
venv\Scripts\activate      # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env       # add your OpenRouter API key
python app.py
Visit → http://127.0.0.1:5000

🔐 Environment Variables (.env)
FLASK_ENV=development
FLASK_DEBUG=1
OPENROUTER_API_KEY=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
OPENROUTER_ENDPOINT=https://openrouter.ai/api/v1/chat/completions
PORT=5000
MEMORY_FILE=data/memory.json
MAX_MEMORY=20
ALLOWED_ORIGINS=*

🚀 Deployment
🌐 Deploy to Render

Push your project to GitHub.

Go to Render.com
 → New Web Service.

Build command:
pip install -r requirements.txt

Start command:
gunicorn app:app --bind 0.0.0.0:$PORT

Add your environment variables in the Render dashboard.

✅ The app will auto-deploy and give you a public HTTPS link.

🧪 API Example
curl -X POST http://127.0.0.1:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hey AEON, what’s the time in Tokyo and latest news on quantum AI"}'

🧠 Future Enhancements

Add WebSocket-based real-time streaming.

Integrate proper search APIs (Google / Bing) with citations.

Add user authentication and long-term persistent memory.

Extend for multimodal input (voice, image, code).

🧾 Attribution

AEON ∞ — Infinity Intelligence
Created by Apratim Mrinal
Inspired by ChatGPT · Gemini · DeepSeek · Grok · Sonnet
