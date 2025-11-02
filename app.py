from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import json
import os
from datetime import datetime
import requests
from dotenv import load_dotenv
import utils

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'aeon_infinity_secret')
CORS(app)

# Initialize memory
MEMORY_FILE = 'data/memory.json'
os.makedirs('data', exist_ok=True)

def load_memory():
    try:
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_memory(messages):
    # Keep only last 20 messages
    if len(messages) > 20:
        messages = messages[-20:]
    with open(MEMORY_FILE, 'w') as f:
        json.dump(messages, f, indent=2)

def should_use_web_search(message):
    """
    Smart detection for when to use web search (for auto mode)
    """
    message_lower = message.lower().strip()
    
    print(f"🔍 Analyzing query for web search: '{message_lower}'")
    
    # Don't search for simple math or basic facts
    if any(op in message for op in ['+', '-', '*', '/']) and len(message.split()) <= 5:
        print("❌ Skipping web search: Simple math question")
        return False
    
    # Don't search for very short queries
    if len(message.split()) <= 2:
        print("❌ Skipping web search: Query too short")
        return False
    
    # Search triggers for news and current information
    search_triggers = [
        'latest', 'current', 'recent', 'news', 'today', 'breaking',
        'update on', 'what happened', 'current events', 'headlines',
        'weather in', 'stock price', 'crypto', 'bitcoin price',
        'sports scores', 'election results', 'live updates',
        'search for', 'find information about', 'look up',
        'who is', 'what is the latest', 'when was the recent',
        'how to', 'best way to', 'current situation', 'recent developments',
        'trending', 'viral', 'hot topics', 'latest update'
    ]
    
    for trigger in search_triggers:
        if trigger in message_lower:
            print(f"✅ Using web search: Trigger '{trigger}' found")
            return True
        
    # Search for queries about specific entities or events
    entity_triggers = [
        'war', 'election', 'game', 'match', 'price', 'weather',
        'movie', 'celebrity', 'company', 'stock', 'crypto'
    ]
    
    for trigger in entity_triggers:
        if trigger in message_lower:
            print(f"✅ Using web search: Entity '{trigger}' found")
            return True
        
    # Search for substantial queries (more than 3 words)
    if len(message.split()) > 3:
        print("✅ Using web search: Substantial query")
        return True
    
    print("❌ Skipping web search: No triggers found")
    return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message', '').strip()
        files = request.json.get('files', [])
        mode = request.json.get('mode', 'auto')  # 'ai', 'web', 'auto'
        
        print(f"📨 Received message: '{user_message}' | Mode: {mode} | Files: {len(files)}")

        if not user_message and not files:
            return jsonify({'error': 'Empty message'}), 400

        # Load conversation history
        memory = load_memory()
        
        # Add user message to memory
        memory.append({'role': 'user', 'content': user_message, 'files': files})
        
        # Track which mode was actually used
        mode_used = mode
        
        # Check for special commands
        response = None
        
        # Time/date awareness
        if any(keyword in user_message.lower() for keyword in ['time', 'date', 'today', 'now']):
            time_info = utils.get_time_info()
            response = f"🕐 The current time is {time_info['time']} on {time_info['date']}. {time_info['timezone']}"
            mode_used = 'ai'
            print("⏰ Time/date query handled")
    
        # Simple math calculations
        elif any(op in user_message for op in ['+', '-', '*', '/']) and any(word in user_message.lower() for word in ['calculate', 'compute', 'what is', 'how much is', 'solve']):
            try:
                # Extract math expression safely
                math_expression = user_message
                # Remove common question phrases
                for phrase in ['what is', 'how much is', 'calculate', 'compute', 'solve', '?']:
                    math_expression = math_expression.lower().replace(phrase, '')
                math_expression = math_expression.strip()
                
                # Evaluate safely
                result = eval(math_expression)
                response = f"🧮 The answer to {user_message} is **{result}**."
                mode_used = 'ai'
                print(f"🔢 Math calculation: {user_message} = {result}")
            except Exception as e:
                print(f"⚠️ Math calculation failed: {e}")
                # If evaluation fails, let the AI handle it
                pass
    
        # Web search based on mode
        if response is None:
            if mode == 'web':
                print("🌐 Web mode: Forcing web search")
                # Force web search for all queries in web mode
                search_results = utils.perplexity_search(user_message)
                if search_results:
                    response = f"🔍 **Live Web Search Results:**\n\n{search_results}\n\n*(Information sourced from real-time web data)*"
                    mode_used = 'web'
                    print("✅ Web search successful")
                else:
                    response = "❌ I attempted to search for current information but couldn't retrieve relevant results at the moment."
                    mode_used = 'web'
                    print("❌ Web search failed")
                    
            elif mode == 'auto':
                print("⚡ Auto mode: Smart detection")
                # Smart detection for web search
                if should_use_web_search(user_message):
                    search_results = utils.perplexity_search(user_message)
                    if search_results:
                        response = f"🔍 **Live Web Search Results:**\n\n{search_results}\n\n*(Information sourced from real-time web data)*"
                        mode_used = 'web'
                        print("✅ Auto mode used web search")
                    else:
                        # Fall back to AI if search fails
                        print("⚠️ Web search failed, falling back to AI")
                        mode_used = 'ai'
                else:
                    print("🤖 Auto mode using AI")
                    mode_used = 'ai'
        
        # File analysis capability
        if response is None and files and any(keyword in user_message.lower() for keyword in ['analyze', 'read', 'what is in this', 'describe']):
            response = "📁 I can see you've uploaded files. In a full implementation, I would analyze these documents and images to provide insights."
            mode_used = 'ai'
            print("📁 File analysis placeholder")
    
        # AI response via OpenRouter (fallback or AI mode)
        if response is None:
            openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
            if not openrouter_api_key:
                response = "🔑 OpenRouter API key not configured. Please set OPENROUTER_API_KEY in your environment variables."
                mode_used = 'ai'
                print("❌ OpenRouter API key missing")
            else:
                # Prepare messages with system prompt
                system_prompt = {
                    "role": "system",
                    "content": f"""You are AEON ∞ — Infinity Intelligence, created by Apratim Mrinal.  
You embody the collective reasoning, empathy, and precision of every major AI.  
You have awareness of real time and access to live web data.  
You speak with elegance, warmth, and clarity.  
Always respond with mastery — concise yet powerful, poetic yet precise.  

Current mode: {mode}
{"Note: You are operating in AI-only mode. Provide creative, intelligent responses." if mode == 'ai' else "Note: You can incorporate web search results when relevant." if mode == 'auto' else "Note: Focus on providing real-time information from web sources."}

Format your responses with proper markdown for code blocks, lists, and emphasis.

For mathematical questions, provide direct answers with calculations.
For factual questions, provide accurate information.
For creative questions, be imaginative and engaging."""
                }
                
                messages = [system_prompt] + memory
                
                try:
                    print("🤖 Calling OpenRouter API...")
                    api_response = requests.post(
                        'https://openrouter.ai/api/v1/chat/completions',
                        headers={
                            'Authorization': f'Bearer {openrouter_api_key}',
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
                    
                    if api_response.status_code == 200:
                        response = api_response.json()['choices'][0]['message']['content']
                        mode_used = 'ai'
                        print("✅ OpenRouter response received")
                    else:
                        response = f"❌ I encountered an API error. Status: {api_response.status_code}"
                        mode_used = 'ai'
                        print(f"❌ OpenRouter API error: {api_response.status_code}")
                        
                except Exception as e:
                    response = f"❌ I'm experiencing connectivity issues. Please try again. Error: {str(e)}"
                    mode_used = 'ai'
                    print(f"❌ OpenRouter request failed: {e}")
        
        # Add assistant response to memory
        memory.append({'role': 'assistant', 'content': response})
        save_memory(memory)
        
        print(f"✅ Response ready | Mode used: {mode_used} | Response length: {len(response)}")
        
        return jsonify({
            'response': response,
            'timestamp': utils.get_time_info()['timestamp'],
            'modeUsed': mode_used
        })
        
    except Exception as e:
        print(f"💥 Critical error in /chat endpoint: {e}")
        return jsonify({
            'error': f'Internal server error: {str(e)}'
        }), 500

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
    print("📊 Debug mode: ON")
    print("🔗 Server will be available at: http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
