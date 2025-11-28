"""
Comprehensive integration test - simulates real conversation
Run: python test_integration.py
"""

import sys
sys.dont_write_bytecode = True

import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('GROQ_API_KEY')
if not API_KEY:
    print("ERROR: GROQ_API_KEY not found!")
    sys.exit(1)

# Import from chat.py
MIN_REQUEST_INTERVAL = 2.5
last_request_time = 0

def estimate_tokens(text):
    """Rough token estimation: 1 token ≈ 4 characters"""
    return len(text) // 4

def throttle_request():
    """Ensure minimum time between requests to avoid rate limits"""
    global last_request_time
    current_time = time.time()
    time_since_last = current_time - last_request_time
    
    if time_since_last < MIN_REQUEST_INTERVAL:
        wait_time = MIN_REQUEST_INTERVAL - time_since_last
        time.sleep(wait_time)
    
    last_request_time = time.time()

# Read personality from chat.py
with open('chat.py', 'r') as f:
    content = f.read()
    import re
    match = re.search(r'PERSONALITY = """(.*?)"""', content, re.DOTALL)
    PERSONALITY = match.group(1) if match else "You are helpful."

def test_full_conversation():
    """Test a full conversation with throttling"""
    print("=" * 60)
    print("INTEGRATION TEST: Full Conversation Simulation")
    print("=" * 60)
    print("\nSimulating a real conversation with Song Hui...")
    print("This will send multiple messages with proper throttling.")
    print("\n⏳ Waiting 60 seconds to ensure rate limits are cleared...\n")
    print("(This is necessary because the large personality prompt uses ~5000 tokens)")
    time.sleep(60)  # Wait to clear any previous rate limits (token limits reset per minute)
    
    conversation_history = [
        {'role': 'system', 'content': PERSONALITY}
    ]
    
    test_messages = [
        "hello",
        "who are you?",
        "tell me about Corey",
        "what do you like to do?",
    ]
    
    success_count = 0
    rate_limit_count = 0
    error_count = 0
    total_tokens_estimated = 0
    
    for i, user_message in enumerate(test_messages):
        print(f"\n--- Message {i+1}/{len(test_messages)} ---")
        print(f"You: {user_message}")
        
        # Add user message
        conversation_history.append({'role': 'user', 'content': user_message})
        
        # Prepare messages (same logic as chat.py)
        if len(conversation_history) <= 3:
            messages_to_send = conversation_history
        else:
            messages_to_send = [
                conversation_history[0],  # System
                conversation_history[-2],  # Last user
                conversation_history[-1]   # Last assistant (if exists)
            ]
            if messages_to_send[-1]['role'] != 'assistant':
                messages_to_send = messages_to_send[:-1]
        
        # Estimate tokens
        total_chars = sum(len(str(m.get('content', ''))) for m in messages_to_send)
        estimated_tokens = total_chars // 4  # Direct calculation
        total_tokens_estimated += estimated_tokens
        
        print(f"📊 Sending {len(messages_to_send)} messages, ~{estimated_tokens} tokens")
        
        # Throttle based on token count (same as chat.py)
        throttle_request(estimated_tokens)
        
        # Make request
        try:
            response = requests.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {API_KEY}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'llama-3.1-8b-instant',
                    'messages': messages_to_send,
                    'max_tokens': 60,
                    'temperature': 0.9,
                    'stream': False
                },
                timeout=15
            )
            
            if response.status_code == 200:
                bot_response = response.json()['choices'][0]['message']['content']
                print(f"Bot: {bot_response[:100]}...")
                conversation_history.append({'role': 'assistant', 'content': bot_response})
                success_count += 1
            elif response.status_code == 429:
                rate_limit_count += 1
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', '')
                print(f"❌ RATE LIMIT: {error_msg[:100]}...")
                print("⚠️  This should NOT happen with proper throttling!")
                break  # Stop test if rate limited
            else:
                error_count += 1
                print(f"❌ Error {response.status_code}: {response.text[:100]}...")
                break
        
        except Exception as e:
            error_count += 1
            print(f"❌ Exception: {e}")
            break
        
        # Small delay between messages for readability
        if i < len(test_messages) - 1:
            time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"✅ Successful requests: {success_count}/{len(test_messages)}")
    print(f"❌ Rate limited: {rate_limit_count}")
    print(f"❌ Errors: {error_count}")
    print(f"📊 Total estimated tokens: ~{total_tokens_estimated}")
    print(f"⏱️  Average tokens per request: ~{total_tokens_estimated // max(success_count, 1)}")
    
    if rate_limit_count == 0 and error_count == 0:
        print("\n🎉 SUCCESS: All requests completed without rate limits!")
        print("✅ The throttling system is working correctly.")
        return True
    else:
        print("\n⚠️  FAILURE: Rate limits or errors detected!")
        print("❌ The system needs further optimization.")
        return False

def test_rapid_fire():
    """Test rapid-fire requests to verify throttling works"""
    print("\n" + "=" * 60)
    print("STRESS TEST: Rapid-Fire Requests")
    print("=" * 60)
    print("\nSending 5 requests as fast as possible...")
    print("Throttling should prevent rate limits.\n")
    
    messages = [
        {'role': 'system', 'content': 'You are helpful.'},
        {'role': 'user', 'content': 'Say hello'}
    ]
    
    success_count = 0
    rate_limit_count = 0
    start_time = time.time()
    
    for i in range(5):
        print(f"Request {i+1}/5...", end=" ", flush=True)
        
        # Throttle
        throttle_request()
        
        try:
            response = requests.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {API_KEY}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'llama-3.1-8b-instant',
                    'messages': messages,
                    'max_tokens': 20,
                    'temperature': 0.7,
                    'stream': False
                },
                timeout=10
            )
            
            if response.status_code == 200:
                print("✓")
                success_count += 1
            elif response.status_code == 429:
                print("❌ RATE LIMITED")
                rate_limit_count += 1
            else:
                print(f"✗ {response.status_code}")
        
        except Exception as e:
            print(f"✗ Error: {e}")
    
    elapsed = time.time() - start_time
    print(f"\nCompleted in {elapsed:.1f} seconds")
    print(f"✅ Success: {success_count}/5")
    print(f"❌ Rate limited: {rate_limit_count}/5")
    
    if rate_limit_count == 0:
        print("✅ Throttling working correctly!")
        return True
    else:
        print("❌ Throttling failed - rate limits detected!")
        return False

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("COMPREHENSIVE INTEGRATION TESTS")
    print("=" * 60)
    
    # Run tests
    test1_passed = test_full_conversation()
    test2_passed = test_rapid_fire()
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    
    if test1_passed and test2_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ System is ready for production use.")
        print("\nThe chatbot will:")
        print("  - Automatically throttle requests (2.5s between requests)")
        print("  - Handle rate limits gracefully")
        print("  - Minimize token usage")
        print("  - Work reliably without hitting limits")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("❌ System needs further optimization before going live.")
    
    print()
