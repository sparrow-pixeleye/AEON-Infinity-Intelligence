import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os

def get_time_info():
    now = datetime.now()
    return {
        'time': now.strftime('%H:%M:%S'),
        'date': now.strftime('%A, %B %d, %Y'),
        'timezone': 'UTC',
        'timestamp': now.isoformat()
    }

def perplexity_search(query, max_results=5):
    """
    Perform web search using Perplexity AI API
    """
    api_key = "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"
    
    if not api_key:
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
        
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=payload,
            timeout=20
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            print(f"Perplexity API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Perplexity search error: {e}")
        return None

def web_search(query, max_results=3):
    """
    Fallback web search function
    """
    try:
        # Simple Wikipedia search first
        wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
        wiki_response = requests.get(wiki_url, timeout=10)
        
        if wiki_response.status_code == 200:
            data = wiki_response.json()
            return data.get('extract', 'No summary available.')
        
        # Fallback to DuckDuckGo instant answer
        ddg_url = f"https://api.duckduckgo.com/"
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
                return data['Abstract']
            elif data.get('Answer'):
                return data['Answer']
        
        return None
            
    except Exception as e:
        print(f"Web search error: {e}")
        return None

def format_response(text, message_type="assistant"):
    """Format responses with appropriate styling"""
    if message_type == "assistant":
        return f"**AEON ∞:** {text}"

    return text

