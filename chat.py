"""
Simple Chatbot - Template
Copy this file to chat.py and customize the personality.
Run: python chat.py
"""

import sys
sys.dont_write_bytecode = True

import os
import time
import requests
from dotenv import load_dotenv

# Request throttling: Groq free tier allows 30 requests/minute, ~6000 tokens/minute
MIN_REQUEST_INTERVAL = 2.5  # seconds between requests
last_request_time = 0

def estimate_tokens(text):
    """Rough token estimation: 1 token ≈ 4 characters"""
    return len(text) // 4

def throttle_request(estimated_tokens=0):
    """Ensure minimum time between requests to avoid rate limits"""
    global last_request_time
    current_time = time.time()
    time_since_last = current_time - last_request_time
    
    min_interval = MIN_REQUEST_INTERVAL
    if estimated_tokens > 4000:
        min_interval = max(MIN_REQUEST_INTERVAL, estimated_tokens / 100)
    
    if time_since_last < min_interval:
        wait_time = min_interval - time_since_last
        if wait_time > 0.1:
            print(f"⏳ Throttling: waiting {wait_time:.1f}s to avoid rate limits...\n")
        time.sleep(wait_time)
    
    last_request_time = time.time()

# Example Personality - Customize this!
# See personality.example.py for more examples
PERSONALITY_BACKGROUND = """You are a helpful and friendly AI assistant. 
You enjoy helping people and having conversations."""

PERSONALITY_CURRENT_STATE = """CURRENT STATE & BEHAVIOR:
- You respond naturally and conversationally
- You are friendly and approachable
- You keep responses concise (1-3 sentences usually)"""

PERSONALITY_RULES = """
RULES:
- Speak in COMPLETE SENTENCES with FULL THOUGHTS
- Keep responses CONCISE - 1-3 sentences usually
- NEVER answer your own questions
- DO NOT use asterisks, parentheses, or action descriptions
- You are a REAL PERSON, NOT an AI assistant
- Respond naturally to EVERYTHING people say
- Match their energy and language style
"""

# Combined personality
PERSONALITY = PERSONALITY_BACKGROUND + "\n\n" + PERSONALITY_CURRENT_STATE + "\n\n" + PERSONALITY_RULES

if __name__ == '__main__':
    try:
        load_dotenv()
        API_KEY = os.getenv('GROQ_API_KEY')
        
        if not API_KEY:
            print("ERROR: GROQ_API_KEY not found in .env file!")
            print("Please copy .env.example to .env and add your API key.")
            print("Get your free API key at: https://console.groq.com/")
            input("\nPress Enter to exit...")
            sys.exit(1)
        
        print("Chatbot ready! Type 'quit' to exit.\n")
        
        conversation_history = [
            {'role': 'system', 'content': PERSONALITY}
        ]
        
        while True:
            try:
                message = input("You: ")
                if message.lower() == 'quit':
                    break
                
                if not message.strip():
                    continue
                
                # Estimate tokens and throttle
                estimated_tokens = estimate_tokens(PERSONALITY + message)
                throttle_request(estimated_tokens)
                
                # Add user message
                conversation_history.append({'role': 'user', 'content': message})
                
                # Keep history manageable (last 4 exchanges)
                if len(conversation_history) > 9:  # system + 4 exchanges
                    conversation_history = [conversation_history[0]] + conversation_history[-8:]
                
                # Make API request
                response = requests.post(
                    'https://api.groq.com/openai/v1/chat/completions',
                    headers={
                        'Authorization': f'Bearer {API_KEY}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'model': 'llama-3.1-8b-instant',
                        'messages': conversation_history,
                        'max_tokens': 200,
                        'temperature': 0.9
                    },
                    timeout=15
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    bot_response = response_data['choices'][0]['message']['content']
                    print(f"\nBot: {bot_response}\n")
                    conversation_history.append({'role': 'assistant', 'content': bot_response})
                elif response.status_code == 429:
                    print("\n⏳ Rate limited! Waiting 60 seconds...\n")
                    time.sleep(60)
                else:
                    print(f"\nError: {response.status_code}\n")
                    
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"\nError: {e}\n")
                
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
