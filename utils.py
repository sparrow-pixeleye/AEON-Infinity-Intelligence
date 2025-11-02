import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os
import tempfile


# === Detect environment and choose a safe writable path ===
def get_memory_path():
    """
    Returns a writable path for memory.json:
    - Local: ~/aeon_infinity_data/memory.json
    - Vercel (read-only FS): /tmp/memory.json
    """
    if os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV"):
        # Running on Vercel
        path = os.path.join(tempfile.gettempdir(), "memory.json")
        print(f"🧊 Detected Vercel environment — using temp file: {path}")
    else:
        # Local environment
        base_dir = os.path.join(os.path.expanduser("~"), "aeon_infinity_data")
        os.makedirs(base_dir, exist_ok=True)
        path = os.path.join(base_dir, "memory.json")
    return path


MEMORY_PATH = get_memory_path()


# === Time utilities ===
def get_time_info():
    now = datetime.now()
    return {
        'time': now.strftime('%H:%M:%S'),
        'date': now.strftime('%A, %B %d, %Y'),
        'timezone': 'UTC',
        'timestamp': now.isoformat()
    }


# === Perplexity AI search ===
def perplexity_search(query, max_results=5):
    """
    Perform web search using Perplexity AI API
    """
    api_key = "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"

    if not api_key:
        print("❌ Perplexity API key not found")
        return None

    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        # Enhanced prompt for better search results
        search_prompt = f"""Please provide comprehensive, accurate, and up-to-date information about: {query}

        Requirements:
        - Include the most recent information available
        - Cite key facts and figures when possible
        - Mention relevant dates, events, or developments
        - If discussing current events, note the timeliness
        - Provide context and background when helpful
        - Structure the response in a clear, readable format
        
        Focus on delivering valuable insights that answer the user's query thoroughly."""

        payload = {
            "model": "sonar",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant with access to real-time web search. Provide accurate, up-to-date information with proper context and citations when possible."
                },
                {
                    "role": "user",
                    "content": search_prompt
                }
            ],
            "max_tokens": 1500,
            "temperature": 0.2
        }

        print(f"🔍 Sending request to Perplexity API: {query[:50]}...")
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=payload,
            timeout=20
        )

        if response.status_code == 200:
            data = response.json()
            result = data['choices'][0]['message']['content']
            print(f"✅ Perplexity search successful: {len(result)} characters")
            return result
        else:
            print(f"❌ Perplexity API error: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"❌ Perplexity search error: {e}")
        return None


# === Fallback web search ===
def web_search(query, max_results=3):
    """
    Fallback web search function
    """
    try:
        print(f"🔍 Fallback web search: {query}")
        # Simple Wikipedia search first
        wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
        wiki_response = requests.get(wiki_url, timeout=10)

        if wiki_response.status_code == 200:
            data = wiki_response.json()
            result = data.get('extract', 'No summary available.')
            print("✅ Wikipedia search successful")
            return result

        # Fallback to DuckDuckGo instant answer
        ddg_url = "https://api.duckduckgo.com/"
        params = {
            'q': query,
            'format': 'json',
            'no_html': 1,
            'skip_disambig': 1
        }

        ddg_response = requests.get(ddg_url, params=params, timeout=10)
        if ddg_response.status_code == 200:
            data = ddg_response.json()
            if data.get('Abstract'):
                print("✅ DuckDuckGo search successful")
                return data['Abstract']
            elif data.get('Answer'):
                print("✅ DuckDuckGo answer found")
                return data['Answer']

        print("❌ Fallback search failed")
        return None

    except Exception as e:
        print(f"❌ Web search error: {e}")
        return None


# === Formatting ===
def format_response(text, message_type="assistant"):
    """Format responses with appropriate styling"""
    if message_type == "assistant":
        return f"**AEON ∞:** {text}"
    return text


# === Memory file helpers ===
def load_memory():
    """Load memory.json safely."""
    if not os.path.exists(MEMORY_PATH):
        return {}
    try:
        with open(MEMORY_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("⚠️ memory.json is corrupted; returning empty dict.")
        return {}
    except Exception as e:
        print(f"❌ Error reading memory.json: {e}")
        return {}


def save_memory(data):
    """Save data safely to memory.json."""
    try:
        with open(MEMORY_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ memory.json updated successfully at {MEMORY_PATH}")
    except Exception as e:
        print(f"❌ Error saving memory.json: {e}")
