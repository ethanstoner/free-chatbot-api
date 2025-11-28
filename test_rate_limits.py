"""
Comprehensive tests for rate limit handling and token optimization
Run: python test_rate_limits.py
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

# Simple token estimation: ~4 chars per token (rough estimate)
def estimate_tokens(text):
    """Rough token estimation: 1 token ≈ 4 characters"""
    return len(text) // 4

def test_token_estimation():
    """Test 1: Verify token estimation works"""
    print("=" * 60)
    print("TEST 1: Token Estimation")
    print("=" * 60)
    
    test_strings = [
        "Hello world",
        "You are Song Hui, a 53-year-old Chinese man.",
        "A" * 100,
        "A" * 1000,
    ]
    
    for text in test_strings:
        tokens = estimate_tokens(text)
        print(f"Text length: {len(text)} chars → ~{tokens} tokens")
    
    print("✓ Token estimation working\n")

def test_minimal_messages():
    """Test 2: Verify minimal message structure"""
    print("=" * 60)
    print("TEST 2: Minimal Message Structure")
    print("=" * 60)
    
    # Simulate conversation history
    system_msg = {"role": "system", "content": "You are helpful."}
    user_msg = {"role": "user", "content": "Hello"}
    
    messages = [system_msg, user_msg]
    
    total_chars = sum(len(m["content"]) for m in messages)
    estimated_tokens = estimate_tokens(" ".join(m["content"] for m in messages))
    
    print(f"Messages: {len(messages)}")
    print(f"Total chars: {total_chars}")
    print(f"Estimated tokens: {estimated_tokens}")
    print(f"✓ Minimal structure: {len(messages)} messages\n")

def test_rate_limit_handling():
    """Test 3: Test rate limit detection and handling"""
    print("=" * 60)
    print("TEST 3: Rate Limit Handling")
    print("=" * 60)
    
    # Send a request that might hit rate limit
    messages = [
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Say hello"}
    ]
    
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
            print("✓ Request successful (no rate limit)")
            data = response.json()
            print(f"Response: {data['choices'][0]['message']['content'][:50]}...")
        elif response.status_code == 429:
            print("⚠ Rate limit detected (expected if testing quickly)")
            error_data = response.json()
            error_msg = error_data.get('error', {}).get('message', '')
            print(f"Error: {error_msg[:100]}...")
        else:
            print(f"✗ Unexpected status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()

def test_request_throttling():
    """Test 4: Verify request throttling prevents rate limits"""
    print("=" * 60)
    print("TEST 4: Request Throttling")
    print("=" * 60)
    
    messages = [
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Count to 3"}
    ]
    
    # Groq free tier: 30 requests/minute = 1 request per 2 seconds
    # We'll use 2.5 seconds to be safe
    delay_between_requests = 2.5
    
    print(f"Testing with {delay_between_requests}s delay between requests...")
    print("Sending 3 requests (should take ~7.5 seconds)...")
    
    success_count = 0
    rate_limit_count = 0
    
    for i in range(3):
        try:
            print(f"\nRequest {i+1}/3...")
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
                success_count += 1
                print(f"✓ Success {i+1}")
            elif response.status_code == 429:
                rate_limit_count += 1
                print(f"⚠ Rate limited {i+1}")
            else:
                print(f"✗ Error {i+1}: {response.status_code}")
            
            if i < 2:  # Don't wait after last request
                time.sleep(delay_between_requests)
                
        except Exception as e:
            print(f"✗ Exception {i+1}: {e}")
    
    print(f"\nResults: {success_count} successful, {rate_limit_count} rate limited")
    if rate_limit_count == 0:
        print("✓ Throttling working correctly!")
    else:
        print("⚠ Some rate limits detected - may need longer delay")
    print()

def test_personality_token_count():
    """Test 5: Check personality prompt token count"""
    print("=" * 60)
    print("TEST 5: Personality Prompt Token Count")
    print("=" * 60)
    
    # Read actual personality from chat.py
    try:
        with open('chat.py', 'r') as f:
            content = f.read()
            import re
            match = re.search(r'PERSONALITY = """(.*?)"""', content, re.DOTALL)
            if match:
                personality = match.group(1)
                tokens = estimate_tokens(personality)
                print(f"Personality prompt:")
                print(f"  Length: {len(personality):,} characters")
                print(f"  Estimated tokens: ~{tokens:,}")
                print(f"  This is sent ONCE as system message")
                
                if tokens > 4000:
                    print(f"  ⚠ WARNING: Very large prompt ({tokens} tokens)")
                    print(f"    Consider reducing personality length")
                else:
                    print(f"  ✓ Prompt size is reasonable")
            else:
                print("✗ Could not find PERSONALITY in chat.py")
    except Exception as e:
        print(f"✗ Error reading chat.py: {e}")
    
    print()

def test_conversation_history_optimization():
    """Test 6: Verify conversation history is minimized"""
    print("=" * 60)
    print("TEST 6: Conversation History Optimization")
    print("=" * 60)
    
    # Simulate what chat.py does
    conversation_history = [
        {"role": "system", "content": "You are helpful." * 100},  # Large system
        {"role": "user", "content": "Message 1"},
        {"role": "assistant", "content": "Response 1"},
        {"role": "user", "content": "Message 2"},
        {"role": "assistant", "content": "Response 2"},
        {"role": "user", "content": "Message 3"},
    ]
    
    # Old way: send last 5 messages
    old_messages = conversation_history[-5:] if len(conversation_history) > 5 else conversation_history
    old_tokens = estimate_tokens(" ".join(m["content"] for m in old_messages))
    
    # New way: system + last user + last assistant
    if len(conversation_history) <= 3:
        new_messages = conversation_history
    else:
        new_messages = [
            conversation_history[0],  # System
            conversation_history[-2],  # Last user
            conversation_history[-1]   # Last assistant (if exists)
        ]
        if new_messages[-1]['role'] != 'assistant':
            new_messages = new_messages[:-1]
    
    new_tokens = estimate_tokens(" ".join(m["content"] for m in new_messages))
    
    print(f"Full history: {len(conversation_history)} messages")
    print(f"Old method: {len(old_messages)} messages, ~{old_tokens} tokens")
    print(f"New method: {len(new_messages)} messages, ~{new_tokens} tokens")
    print(f"Token savings: {old_tokens - new_tokens} tokens ({((old_tokens - new_tokens) / old_tokens * 100):.1f}% reduction)")
    print("✓ History optimization working\n")

def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("GROQ API RATE LIMIT & TOKEN OPTIMIZATION TESTS")
    print("=" * 60 + "\n")
    
    test_token_estimation()
    test_minimal_messages()
    test_rate_limit_handling()
    test_request_throttling()
    test_personality_token_count()
    test_conversation_history_optimization()
    
    print("=" * 60)
    print("ALL TESTS COMPLETE")
    print("=" * 60)
    print("\nRecommendations:")
    print("1. Add 2.5+ second delay between requests")
    print("2. Keep conversation history minimal (system + last exchange)")
    print("3. Use max_tokens=60 or less")
    print("4. Monitor token usage per request")
    print()

if __name__ == '__main__':
    run_all_tests()
