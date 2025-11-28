"""
Shared Rate Limiter for Multiple Discord Bots
Coordinates API requests across multiple bot processes using file-based locking
"""

import sys
sys.dont_write_bytecode = True

import os
import time
import fcntl
import asyncio
from pathlib import Path

# Shared state file location
RATE_LIMIT_FILE = Path(__file__).parent / '.rate_limit_state'
LOCK_FILE = Path(__file__).parent / '.rate_limit.lock'

# Groq API rate limits: 30 requests/minute, ~6000 tokens/minute
# When 2 bots run together, we need to share this limit more conservatively
MIN_REQUEST_INTERVAL = 6.0  # Increased to 6 seconds to be safe (30 req/min / 2 = 15 req/min per bot = 4 sec/req, but use 6 for safety)
MAX_TOKENS_PER_MINUTE = 6000
MAX_REQUESTS_PER_MINUTE = 30

class SharedRateLimiter:
    """Rate limiter that coordinates across multiple processes using file locking"""
    
    def __init__(self, bot_name="unknown"):
        self.bot_name = bot_name
        self.ensure_state_file()
    
    def ensure_state_file(self):
        """Ensure the state file exists"""
        if not RATE_LIMIT_FILE.exists():
            with open(RATE_LIMIT_FILE, 'w') as f:
                f.write(f"{time.time()}\n0\n")  # last_request_time, request_count
    
    def read_state(self):
        """Read current state from file (with lock)"""
        max_retries = 5
        for attempt in range(max_retries):
            try:
                # Create lock file if it doesn't exist
                LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
                RATE_LIMIT_FILE.parent.mkdir(parents=True, exist_ok=True)
                
                with open(LOCK_FILE, 'a+') as lock_f:
                    try:
                        fcntl.flock(lock_f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    except (IOError, OSError):
                        # Lock is held, wait a bit and retry
                        if attempt < max_retries - 1:
                            time.sleep(0.1)
                            continue
                        else:
                            # Last attempt, wait for lock
                            fcntl.flock(lock_f.fileno(), fcntl.LOCK_EX)
                    
                    try:
                        if RATE_LIMIT_FILE.exists():
                            with open(RATE_LIMIT_FILE, 'r') as f:
                                lines = f.read().strip().split('\n')
                                if len(lines) >= 2:
                                    last_time = float(lines[0])
                                    request_count = int(lines[1])
                                    return last_time, request_count
                        return 0.0, 0
                    finally:
                        fcntl.flock(lock_f.fileno(), fcntl.LOCK_UN)
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(0.1)
                    continue
                else:
                    print(f"[{self.bot_name}] Error reading state: {e}", flush=True)
                    return 0.0, 0
        return 0.0, 0
    
    def write_state(self, last_time, request_count):
        """Write state to file (with lock)"""
        max_retries = 5
        for attempt in range(max_retries):
            try:
                # Create directories if needed
                LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
                RATE_LIMIT_FILE.parent.mkdir(parents=True, exist_ok=True)
                
                with open(LOCK_FILE, 'a+') as lock_f:
                    try:
                        fcntl.flock(lock_f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    except (IOError, OSError):
                        # Lock is held, wait a bit and retry
                        if attempt < max_retries - 1:
                            time.sleep(0.1)
                            continue
                        else:
                            # Last attempt, wait for lock
                            fcntl.flock(lock_f.fileno(), fcntl.LOCK_EX)
                    
                    try:
                        with open(RATE_LIMIT_FILE, 'w') as f:
                            f.write(f"{last_time}\n{request_count}\n")
                        return  # Success
                    finally:
                        fcntl.flock(lock_f.fileno(), fcntl.LOCK_UN)
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(0.1)
                    continue
                else:
                    print(f"[{self.bot_name}] Error writing state: {e}", flush=True)
    
    async def wait_if_needed(self, estimated_tokens=0):
        """Wait if needed to respect rate limits"""
        current_time = time.time()
        
        # Read current state
        last_request_time, request_count = self.read_state()
        
        # Calculate time since last request
        time_since_last = current_time - last_request_time
        
        # Check if we need to wait
        min_interval = MIN_REQUEST_INTERVAL
        
        # If request is large, increase interval
        if estimated_tokens > 4000:
            min_interval = max(MIN_REQUEST_INTERVAL, estimated_tokens / 100)
        
        # Check per-minute limits - be more conservative (only allow 25 requests per minute to leave buffer)
        safe_max_requests = MAX_REQUESTS_PER_MINUTE - 5  # Leave 5 request buffer
        if request_count >= safe_max_requests:
            # Reset if a minute has passed
            if time_since_last >= 60:
                request_count = 0
            else:
                # Wait until minute resets
                wait_time = 60 - time_since_last
                if wait_time > 0.1:
                    print(f"[{self.bot_name}] ⏳ Rate limit: {request_count}/{safe_max_requests} requests this minute. Waiting {wait_time:.1f}s...", flush=True)
                    await asyncio.sleep(wait_time)
                    current_time = time.time()
                    time_since_last = current_time - last_request_time
                    request_count = 0
        
        # Wait for minimum interval
        if time_since_last < min_interval:
            wait_time = min_interval - time_since_last
            if wait_time > 0.1:
                print(f"[{self.bot_name}] ⏳ Throttling: waiting {wait_time:.1f}s (minimum {MIN_REQUEST_INTERVAL}s between requests)...", flush=True)
            await asyncio.sleep(wait_time)
            current_time = time.time()
        
        # Update state BEFORE making request
        new_request_count = request_count + 1 if time_since_last < 60 else 1
        self.write_state(current_time, new_request_count)
        
        return current_time
    
    def mark_rate_limited(self, wait_seconds=60):
        """Mark that we hit a rate limit and need to wait"""
        current_time = time.time()
        # Set last request time to current + wait, so next request waits
        self.write_state(current_time + wait_seconds, MAX_REQUESTS_PER_MINUTE)
        print(f"[{self.bot_name}] ⚠️ Rate limit hit! Marking state to wait {wait_seconds}s...", flush=True)

# Global instance (will be created per bot)
_rate_limiter = None

def get_rate_limiter(bot_name="unknown"):
    """Get or create the shared rate limiter instance"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = SharedRateLimiter(bot_name)
    return _rate_limiter
