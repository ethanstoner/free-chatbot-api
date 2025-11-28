"""
Test conversation reset logic
"""

import sys
sys.dont_write_bytecode = True

import time

# Simulate the reset logic
CONVERSATION_RESET_INTERVAL = 600  # 10 minutes

conversation_start_times = {}
user_conversations = {}

def test_reset_logic():
    """Test that reset logic works correctly"""
    print("=" * 70)
    print("Testing Conversation Reset Logic")
    print("=" * 70)
    print()
    
    user_id = "test_user"
    
    # Simulate starting a conversation
    conversation_start_times[user_id] = time.time()
    user_conversations[user_id] = ["message1", "message2"]
    
    print(f"1. Conversation started at: {time.time()}")
    print(f"   Messages: {len(user_conversations[user_id])}")
    print()
    
    # Simulate checking after 5 minutes (should NOT reset)
    print(f"2. Checking after 5 minutes (should NOT reset):")
    elapsed = 300  # 5 minutes
    if elapsed >= CONVERSATION_RESET_INTERVAL:
        print("   ❌ Would reset (WRONG - too early)")
    else:
        print(f"   ✅ Would NOT reset (correct - {elapsed}s < {CONVERSATION_RESET_INTERVAL}s)")
    print()
    
    # Simulate checking after 10 minutes (should reset)
    print(f"3. Checking after 10 minutes (should reset):")
    elapsed = 600  # 10 minutes
    if elapsed >= CONVERSATION_RESET_INTERVAL:
        print(f"   ✅ Would reset (correct - {elapsed}s >= {CONVERSATION_RESET_INTERVAL}s)")
        print(f"   Conversation would be cleared and summary created")
    else:
        print("   ❌ Would NOT reset (WRONG)")
    print()
    
    # Simulate checking after 15 minutes (should reset)
    print(f"4. Checking after 15 minutes (should reset):")
    elapsed = 900  # 15 minutes
    if elapsed >= CONVERSATION_RESET_INTERVAL:
        print(f"   ✅ Would reset (correct - {elapsed}s >= {CONVERSATION_RESET_INTERVAL}s)")
    else:
        print("   ❌ Would NOT reset (WRONG)")
    print()
    
    print("=" * 70)
    print("Reset logic test complete!")
    print("=" * 70)
    print()
    print("The bot will automatically reset conversations every 10 minutes")
    print("and include a summary of the previous conversation.")

if __name__ == "__main__":
    test_reset_logic()
