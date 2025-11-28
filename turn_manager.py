"""
Turn Manager for Discord Bots
Manages turn-based responses when all bots are running together
"""

import sys
sys.dont_write_bytecode = True

import os
import time
import fcntl
import random
from pathlib import Path

# Shared state file location
TURN_STATE_FILE = Path(__file__).parent / '.turn_state'
TURN_LOCK_FILE = Path(__file__).parent / '.turn_lock'

# Bot identifiers
BOT_SONG_HUI = "SongHui"
BOT_HASSAN = "Hassan"
BOT_TRUMP = "Trump"

# Decay factor - each time a bot responds, their chance is multiplied by this
# Lower decay = less reduction per response = more even distribution
DECAY_FACTOR = 0.97  # Reduced to 0.97 for much better flow (only 3% reduction per response)

class TurnManager:
    """Manages turn-based responses for bots"""
    
    def __init__(self):
        self.ensure_state_file()
        # Cache for message selections (message_id -> selected_bot)
        self._message_selections = {}
    
    def ensure_state_file(self):
        """Ensure the state file exists"""
        if not TURN_STATE_FILE.exists():
            # Initialize with equal probabilities
            self.write_state(BOT_SONG_HUI, {BOT_SONG_HUI: 1.0, BOT_HASSAN: 1.0, BOT_TRUMP: 1.0})
    
    def read_state(self, lock_file=None):
        """Read current state from file (with optional lock file handle)"""
        # If lock_file is provided, we're already holding the lock
        if lock_file is not None:
            try:
                if TURN_STATE_FILE.exists():
                    with open(TURN_STATE_FILE, 'r') as f:
                        lines = f.read().strip().split('\n')
                        if len(lines) >= 4:
                            last_bot = lines[0]
                            probs = {
                                BOT_SONG_HUI: float(lines[1]),
                                BOT_HASSAN: float(lines[2]),
                                BOT_TRUMP: float(lines[3])
                            }
                            return last_bot, probs
                # Default state
                return BOT_SONG_HUI, {BOT_SONG_HUI: 1.0, BOT_HASSAN: 1.0, BOT_TRUMP: 1.0}
            except Exception as e:
                print(f"Error reading turn state: {e}", flush=True)
                return BOT_SONG_HUI, {BOT_SONG_HUI: 1.0, BOT_HASSAN: 1.0, BOT_TRUMP: 1.0}
        
        # Otherwise, acquire lock and read
        max_retries = 5
        for attempt in range(max_retries):
            try:
                TURN_LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
                TURN_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
                
                with open(TURN_LOCK_FILE, 'a+') as lock_f:
                    try:
                        fcntl.flock(lock_f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    except (IOError, OSError):
                        if attempt < max_retries - 1:
                            time.sleep(0.1)
                            continue
                        else:
                            fcntl.flock(lock_f.fileno(), fcntl.LOCK_EX)
                    
                    try:
                        if TURN_STATE_FILE.exists():
                            with open(TURN_STATE_FILE, 'r') as f:
                                lines = f.read().strip().split('\n')
                                if len(lines) >= 4:
                                    last_bot = lines[0]
                                    probs = {
                                        BOT_SONG_HUI: float(lines[1]),
                                        BOT_HASSAN: float(lines[2]),
                                        BOT_TRUMP: float(lines[3])
                                    }
                                    return last_bot, probs
                        # Default state
                        return BOT_SONG_HUI, {BOT_SONG_HUI: 1.0, BOT_HASSAN: 1.0, BOT_TRUMP: 1.0}
                    finally:
                        fcntl.flock(lock_f.fileno(), fcntl.LOCK_UN)
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(0.1)
                    continue
                else:
                    print(f"Error reading turn state: {e}", flush=True)
                    return BOT_SONG_HUI, {BOT_SONG_HUI: 1.0, BOT_HASSAN: 1.0, BOT_TRUMP: 1.0}
        return BOT_SONG_HUI, {BOT_SONG_HUI: 1.0, BOT_HASSAN: 1.0, BOT_TRUMP: 1.0}
    
    def write_state(self, last_bot, probabilities, lock_file=None):
        """Write state to file (with optional lock file handle)"""
        # If lock_file is provided, we're already holding the lock
        if lock_file is not None:
            try:
                with open(TURN_STATE_FILE, 'w') as f:
                    f.write(f"{last_bot}\n")
                    f.write(f"{probabilities[BOT_SONG_HUI]}\n")
                    f.write(f"{probabilities[BOT_HASSAN]}\n")
                    f.write(f"{probabilities[BOT_TRUMP]}\n")
                return
            except Exception as e:
                print(f"Error writing turn state: {e}", flush=True)
                return
        
        # Otherwise, acquire lock and write
        max_retries = 5
        for attempt in range(max_retries):
            try:
                TURN_LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
                TURN_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
                
                with open(TURN_LOCK_FILE, 'a+') as lock_f:
                    try:
                        fcntl.flock(lock_f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    except (IOError, OSError):
                        if attempt < max_retries - 1:
                            time.sleep(0.1)
                            continue
                        else:
                            fcntl.flock(lock_f.fileno(), fcntl.LOCK_EX)
                    
                    try:
                        with open(TURN_STATE_FILE, 'w') as f:
                            f.write(f"{last_bot}\n")
                            f.write(f"{probabilities[BOT_SONG_HUI]}\n")
                            f.write(f"{probabilities[BOT_HASSAN]}\n")
                            f.write(f"{probabilities[BOT_TRUMP]}\n")
                        return
                    finally:
                        fcntl.flock(lock_f.fileno(), fcntl.LOCK_UN)
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(0.1)
                    continue
                else:
                    print(f"Error writing turn state: {e}", flush=True)
    
    def select_responder(self, message_id=None):
        """Select which bot should respond to the current message (guarantees one response)"""
        try:
            # Use file-based lock to ensure only one bot updates probabilities per message
            max_retries = 10
            for attempt in range(max_retries):
                try:
                    TURN_LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
                    TURN_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(TURN_LOCK_FILE, 'a+') as lock_f:
                        try:
                            fcntl.flock(lock_f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                        except (IOError, OSError):
                            if attempt < max_retries - 1:
                                time.sleep(0.05)
                                continue
                            else:
                                fcntl.flock(lock_f.fileno(), fcntl.LOCK_EX)
                        
                        try:
                            # Read current state (we already have the lock, so pass None to skip locking)
                            last_bot, probabilities = self.read_state(lock_file=lock_f)
                            
                            # Ensure we have valid probabilities
                            if not probabilities:
                                probabilities = {BOT_SONG_HUI: 1.0, BOT_HASSAN: 1.0, BOT_TRUMP: 1.0}
                            
                            # Gradually recover probabilities (move them back toward 1.0)
                            # Faster recovery = better conversation flow
                            recovery_factor = 1.10  # Increased to 1.10 for even faster recovery
                            for bot in probabilities:
                                if probabilities[bot] < 1.0:
                                    probabilities[bot] = min(1.0, probabilities[bot] * recovery_factor)
                            
                            # Normalize probabilities to sum to 3
                            total = sum(probabilities.values())
                            if total == 0:
                                probabilities = {BOT_SONG_HUI: 1.0, BOT_HASSAN: 1.0, BOT_TRUMP: 1.0}
                                total = 3.0
                            
                            # Calculate normalized probabilities (sum to 1.0)
                            normalized = {k: v / total for k, v in probabilities.items()}
                            
                            # Make selection deterministic based on message_id so all bots get same result
                            if message_id:
                                # Use message_id to seed random for deterministic selection
                                import hashlib
                                # Create a deterministic seed from message_id
                                seed = int(hashlib.md5(str(message_id).encode()).hexdigest()[:8], 16)
                                local_random = random.Random(seed)
                            else:
                                local_random = random
                            
                            # Select a bot based on weighted random choice (guarantees one selection)
                            bots = list(normalized.keys())
                            weights = list(normalized.values())
                            selected_bot = local_random.choices(bots, weights=weights, k=1)[0]
                            
                            # Update probabilities - decrease selected bot's probability
                            new_probs = probabilities.copy()
                            new_probs[selected_bot] = probabilities[selected_bot] * DECAY_FACTOR
                            
                            # Ensure minimum probability (don't let it go below 0.3 for better flow)
                            # Higher minimum ensures conversation keeps flowing smoothly
                            if new_probs[selected_bot] < 0.3:
                                new_probs[selected_bot] = 0.3
                            
                            # Write updated state (while holding lock, so pass lock_file)
                            self.write_state(selected_bot, new_probs, lock_file=lock_f)
                            
                            return selected_bot
                        finally:
                            fcntl.flock(lock_f.fileno(), fcntl.LOCK_UN)
                    break  # Success, exit retry loop
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(0.05)
                        continue
                    else:
                        raise e
            # If we get here, something went wrong
            return random.choice([BOT_SONG_HUI, BOT_HASSAN, BOT_TRUMP])
        except Exception as e:
            print(f"Error in turn_manager.select_responder: {e}", flush=True)
            import traceback
            traceback.print_exc()
            # On error, return random bot
            return random.choice([BOT_SONG_HUI, BOT_HASSAN, BOT_TRUMP])
    
    def should_respond(self, bot_name, message_id=None):
        """Determine if this bot should respond based on turn system"""
        try:
            # Select which bot should respond (guarantees one response per message)
            # Use message_id to ensure all bots get the same selection for the same message
            selected_bot = self.select_responder(message_id)
            return selected_bot == bot_name
        except Exception as e:
            print(f"Error in turn_manager.should_respond: {e}", flush=True)
            import traceback
            traceback.print_exc()
            # On error, allow response (fail open)
            return True
    
    def reset_probabilities(self):
        """Reset all probabilities to equal (1.0 each)"""
        self.write_state(BOT_SONG_HUI, {BOT_SONG_HUI: 1.0, BOT_HASSAN: 1.0, BOT_TRUMP: 1.0})

# Global instance
_turn_manager = None

def get_turn_manager():
    """Get or create the turn manager instance"""
    global _turn_manager
    if _turn_manager is None:
        _turn_manager = TurnManager()
    return _turn_manager
