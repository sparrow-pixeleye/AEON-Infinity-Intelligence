from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
import requests
from dotenv import load_dotenv
import tempfile
import utils

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'aeon_infinity_secret')
CORS(app)

# === Memory setup ===
if os.getenv("VERCEL"):
    MEMORY_FILE = os.path.join(tempfile.gettempdir(), "memory.json")
else:
    os.makedirs("data", exist_ok=True)
    MEMORY_FILE = os.path.join("data", "memory.json")

print(f"💾 Using memory file: {MEMORY_FILE}")

def load_memory():
    """Safely load memory and enforce list structure."""
    try:
        if not os.path.exists(MEMORY_FILE):
            print("📂 memory.json not found — creating a new one.")
            return []

        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, list):
            print("⚠️ memory.json contained invalid data (dict). Resetting file...")
            with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f)
            return []

        return data

    except (FileNotFoundError, json.JSONDecodeError):
        print("⚠️ memory.json missing or corrupted — recreating.")
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
        return []

def save_memory(messages):
    """Safely save conversation memory."""
    try:
        if len(messages) > 20:
            messages = messages[-20:]
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(messages, f, indent=2, ensure_ascii=False)
        print("✅ Memory saved successfully.")
    except Exception as e:
        print(f"❌ Failed to save memory: {e}")

# === Auto-clean memory on startup ===
try:
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r+', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, list):
                print("🧹 Startup: cleaning corrupted memory.json")
                f.seek(0)
                json.dump([], f)
                f.truncate()
except Exception as e:
    print(f"⚠️ Startup memory check skipped: {e}")

# === Web search detection ===
def should_use_web_search(message):
    message_lower = message.lower().strip()
    print(f"🔍 Analyzing for web search: '{message_lower}'")

    if any(op in message for op in ['+', '-', '*', '/']) and len(message.split()) <= 5:
        return False
    if len(message.split()) <= 2:
        return False

    triggers = [
        'latest', 'current', 'recent', 'news', 'today', 'breaking',
        'update on', 'what happened', 'current events', 'headlines',
        'weather in', 'stock price', 'crypto', 'bitcoin price',
        'sports scores', 'election results', 'live updates',
        'search for', 'find information about', 'look up',
        'who is', 'what is the latest', 'how to', 'best way to',
        'current situation', 'recent developments', 'trending', 'viral'
    ]
    for trigger in triggers:
        if trigger in message_lower:
            print(f"✅ Using web search: Trigger '{trigger}' found")
            return True

    entities = ['war', 'election', 'game', 'match', 'price', 'weather', 'movie', 'celebrity', 'company', 'stock', 'crypto']
    for trigger in entities:
        if trigger in message_lower:
            print(f"✅ Using web search: Entity '{trigger}' found")
            return True

    if len(message.split()) > 3:
        print("✅ Using web search: Substantial query")
        return True

    return False

# === Routes ===
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message', '').strip()
        files = request.json.get('files', [])
        mode = request.json.get('mode', 'auto')

        print(f"📨 Received: '{user_message}' | Mode: {mode} | Files: {len(files)}")

        if not user_message and not files:
            return jsonify({'error': 'Empty message'}), 400

        memory = load_memory()
        if not isinstance(memory, list):
            print("⚠️ Memory loaded as dict — resetting.")
            memory = []

        memory.append({'role': 'user', 'content': user_message, 'files': files})
        mode_used = mode
        response = None

        # Time/date handling
        if any(word in user_message.lower() for word in ['time', 'date', 'today', 'now']):
            t = utils.get_time_info()
            response = f"🕐 The current time is {t['time']} on {t['date']} ({t['timezone']})."
            mode_used = 'ai'

        # Math
        elif any(op in user_message for op in ['+', '-', '*', '/']) and any(
            w in user_message.lower() for w in ['calculate', 'compute', 'what is', 'how much is', 'solve']
        ):
            try:
                expr = user_message.lower()
                for p in ['what is', 'how much is', 'calculate', 'compute', 'solve', '?']:
                    expr = expr.replace(p, '')
                expr = expr.strip()
                result = eval(expr)
                response = f"🧮 The answer to {user_message} is **{result}**."
                mode_used = 'ai'
            except Exception as e:
                print(f"⚠️ Math eval failed: {e}")

        # Web search logic
        if response is None:
            if mode == 'web':
                result = utils.perplexity_search(user_message)
                if result:
                    response = f"🔍 **Live Web Search Results:**\n\n{result}\n\n*(Information from real-time sources)*"
                    mode_used = 'web'
                else:
                    response = "❌ I couldn't find relevant live information."
                    mode_used = 'web'

            elif mode == 'auto':
                if should_use_web_search(user_message):
                    result = utils.perplexity_search(user_message)
                    if result:
                        response = f"🔍 **Live Web Search Results:**\n\n{result}\n\n*(Information from real-time sources)*"
                        mode_used = 'web'
                    else:
                        print("⚠️ Web search failed; fallback to AI.")
                        mode_used = 'ai'
                else:
                    mode_used = 'ai'

        # File uploads (placeholder)
        if response is None and files:
            response = "📁 I received your files. File analysis isn’t implemented yet."
            mode_used = 'ai'

        # Fallback to AI (OpenRouter)
        if response is None:
            openrouter_key = os.getenv('OPENROUTER_API_KEY')
            if not openrouter_key:
                response = "🔑 OpenRouter API key not configured."
                mode_used = 'ai'
            else:
                sys_prompt = {
                    "role": "system",
                    "content": f"You are AEON ∞ — Infinity Intelligence by Apratim Mrinal. Mode: {mode}."
                }
                messages = [sys_prompt] + memory
                try:
                    api_resp = requests.post(
                        'https://openrouter.ai/api/v1/chat/completions',
                        headers={
                            'Authorization': f'Bearer {openrouter_key}',
                            'Content-Type': 'application/json'
                        },
                        json={
                            'model': 'meta-llama/llama-3.3-70b-instruct:free',
                            'messages': messages,
                            'temperature': 0.7,
                            'max_tokens': 2000
                        },
                        timeout=30
                    )
                    if api_resp.status_code == 200:
                        response = api_resp.json()['choices'][0]['message']['content']
                        mode_used = 'ai'
                    else:
                        response = f"❌ API error: {api_resp.status_code}"
                except Exception as e:
                    response = f"❌ Connection issue: {e}"
                    mode_used = 'ai'

        memory.append({'role': 'assistant', 'content': response})
        save_memory(memory)

        return jsonify({
            'response': response,
            'timestamp': utils.get_time_info()['timestamp'],
            'modeUsed': mode_used
        })

    except Exception as e:
        print(f"💥 Critical error in /chat: {e}")
        return jsonify({'error': f'Internal server error: {e}'}), 500

@app.route('/memory', methods=['GET', 'DELETE'])
def handle_memory():
    if request.method == 'GET':
        return jsonify(load_memory())
    elif request.method == 'DELETE':
        save_memory([])
        return jsonify({'status': 'Memory cleared'})

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    print("🚀 Starting AEON ∞ Server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
