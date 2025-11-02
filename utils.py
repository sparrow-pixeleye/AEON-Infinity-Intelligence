import requests
from datetime import datetime
import json
import os

# === Environment-safe memory path ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Detect if running on Vercel (read-only root filesystem)
if os.getenv("VERCEL"):
    MEMORY_DIR = "/tmp"
else:
    MEMORY_DIR = os.path.join(BASE_DIR, "data")

# Final memory file path
MEMORY_PATH = os.path.join(MEMORY_DIR, "memory.json")

# Ensure directory exists (only works locally; /tmp always exists)
os.makedirs(MEMORY_DIR, exist_ok=True)

# === Time utilities ===
def get_time_info():
    now = datetime.now()
    return {
        "time": now.strftime("%H:%M:%S"),
        "date": now.strftime("%A, %B %d, %Y"),
        "timezone": "UTC",
        "timestamp": now.isoformat()
    }

# === Perplexity AI search ===
def perplexity_search(query, max_results=5):
    """
    Perform web search using Perplexity AI API.
    Returns AI-generated text or None on failure.
    """
    api_key = "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"
    if not api_key:
        print("❌ Perplexity API key missing.")
        return None

    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        prompt = f"""Please provide comprehensive, up-to-date information about: {query}.
        Include key facts, context, and relevant dates. Write clearly and concisely."""

        payload = {
            "model": "sonar",
            "messages": [
                {"role": "system", "content": "You are a helpful AI assistant with live web access."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1500,
            "temperature": 0.2
        }

        print(f"🌐 Searching Perplexity for: {query[:60]}...")
        resp = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=payload,
            timeout=20
        )

        if resp.status_code == 200:
            data = resp.json()
            result = data["choices"][0]["message"]["content"]
            print("✅ Perplexity search successful.")
            return result
        else:
            print(f"❌ Perplexity API error: {resp.status_code} - {resp.text}")
            return None
    except Exception as e:
        print(f"❌ Perplexity search failed: {e}")
        return None

# === Fallback web search ===
def web_search(query):
    """Simple fallback using Wikipedia or DuckDuckGo."""
    try:
        print(f"🔍 Fallback web search: {query}")
        wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
        wiki_resp = requests.get(wiki_url, timeout=10)

        if wiki_resp.status_code == 200:
            data = wiki_resp.json()
            if "extract" in data:
                print("✅ Wikipedia search successful.")
                return data["extract"]

        # Fallback: DuckDuckGo
        ddg_url = "https://api.duckduckgo.com/"
        params = {"q": query, "format": "json", "no_html": 1}
        ddg_resp = requests.get(ddg_url, params=params, timeout=10)

        if ddg_resp.status_code == 200:
            data = ddg_resp.json()
            if data.get("Abstract"):
                return data["Abstract"]
            if data.get("Answer"):
                return data["Answer"]

        print("❌ No fallback results found.")
        return None
    except Exception as e:
        print(f"❌ Web search error: {e}")
        return None

# === Formatting helper ===
def format_response(text, message_type="assistant"):
    """Format responses nicely for display."""
    if message_type == "assistant":
        return f"**AEON ∞:** {text}"
    return text

# === Memory helpers (renamed to avoid collision with app.py) ===
def load_json_memory():
    """Load conversation memory safely."""
    if not os.path.exists(MEMORY_PATH):
        return []
    try:
        with open(MEMORY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ensure memory is always a list
            return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        print("⚠️ memory.json corrupted. Returning empty list.")
        return []
    except Exception as e:
        print(f"❌ Error reading memory.json: {e}")
        return []

def save_json_memory(data):
    """Save conversation memory safely."""
    try:
        # Trim memory to last 20 messages
        if len(data) > 20:
            data = data[-20:]

        with open(MEMORY_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ memory.json saved at {MEMORY_PATH}")
    except Exception as e:
        print(f"❌ Error saving memory.json: {e}")
