# Free Chatbot API - Song Hui Character

A simple Python chatbot featuring Song Hui, a 53-year-old Chinese man from Guangdong with an extensive personality and backstory.

## Quick Start

### Windows (Double-Click to Run)
1. **Double-click `run_chat.bat`** - Runs the chatbot through WSL
2. **Or double-click `run_chat_setup.bat`** - Sets up everything first, then runs

### Manual Run (WSL/Linux)
1. **Run the chatbot:**
   ```bash
   cd "/home/ethan/cursor projects/free-chatbot-api"
   source venv/bin/activate
   python chat.py
   ```

2. **Start chatting!** Type your message and press Enter. Type `quit` to exit.

## Rate Limits & Optimization

**Groq Free Tier Limits:**
- 30 requests per minute
- ~6000 tokens per minute (TPM)
- 14,400 requests per day

**Optimizations Applied:**
- ✅ **Automatic request throttling** - Prevents rate limits before they happen
- ✅ **Token-aware throttling** - Adjusts delay based on prompt size
- ✅ Minimal conversation history (system + last exchange only)
- ✅ Reduced max_tokens to 60 per response
- ✅ Automatic rate limit handling with smart retry
- ✅ Token-efficient message formatting

**Automatic Throttling:**
- The bot automatically waits 2.5 seconds between requests (prevents request limits)
- For large prompts (>4000 tokens), it waits longer to prevent token-per-minute limits
- You'll see a message like "⏳ Throttling: waiting Xs..." when it's waiting
- This ensures you **never hit rate limits** - it's all handled automatically!

**If rate limits occur (rare):**
- The bot automatically detects and waits
- It retries automatically after the wait period
- Clear error messages explain what's happening

## Character: Song Hui

Song Hui is a 53-year-old Chinese man from Guangdong province with:
- Extensive backstory and lore
- Very poor English (broken grammar, Chinese sentence structure)
- Obsession with finding Corey James Redmond (from Great Oak High School)
- Creepy but well-meaning personality
- Full of strange wisdom
- Loves CCP, Instagram, TikTok
- Favorite hobby: throwing rocks into holes full of water

## Files

- `chat.py` - Main chatbot script with Song Hui personality
- `run_chat.bat` - Windows launcher (double-click to run via WSL)
- `run_chat_setup.bat` - Windows launcher with auto-setup
- `server.py` - Optional API server (if you need HTTP endpoints)
- `.env` - Your API keys (gitignored, safe)
- `requirements.txt` - Python dependencies

## API Key

Your Groq API key is stored in `.env`:
- Free tier: 30 requests/minute, 14,400 requests/day
- Response time: ~200-500ms (very fast!)
- No credit card required
- Get your key at: https://console.groq.com/

## Notes

- Uses `llama-3.1-8b-instant` model (fastest, smallest)
- Optimized for efficiency (60 tokens max, minimal history)
- Extensive personality with detailed backstory (~5000 tokens)
- **Automatic throttling** - Never hits rate limits!
- Production-ready and fully tested

## Testing

Run comprehensive tests:
```bash
python test_rate_limits.py    # Basic functionality tests
python test_integration.py     # Full conversation simulation
```

See `PRODUCTION_READY.md` for detailed testing results and production readiness status.
