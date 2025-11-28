# Free Chatbot API

A production-ready Python chatbot with fully programmable personality system. Uses Groq API for fast, free AI responses. Perfect for creating custom chatbots with any personality you want.

## Features

- 🎭 **Fully Customizable Personality** - Program any character or personality you want
- ⚡ **Fast Responses** - Uses Groq API (200-500ms response time)
- 🚀 **Automatic Rate Limiting** - Never hits rate limits with intelligent throttling
- 💬 **Chat Channel Support** - Can respond in Discord channels or terminal
- 🐍 **Simple Python** - Easy to understand and modify
- 📦 **Production Ready** - Fully tested and optimized

## Quick Start

### 1. Setup

```bash
# Clone the repository
git clone https://github.com/ethanstoner/free-chatbot-api.git
cd free-chatbot-api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure

1. **Copy `.env.example` to `.env`:**
   ```bash
   cp .env.example .env
   ```

2. **Add your Groq API key to `.env`:**
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```
   Get your free API key at: https://console.groq.com/

### 3. Customize Personality

Edit `chat.py` and modify the personality variables:

```python
PERSONALITY_BACKGROUND = """Your character's background and history"""

PERSONALITY_CURRENT_STATE = """How your character acts now"""

PERSONALITY_RULES = """Speech patterns and behavior rules"""
```

See `personality.example.py` for detailed examples and templates.

### 4. Run

```bash
python chat.py
```

Type your message and press Enter. Type `quit` to exit.

## Rate Limits & Optimization

**Groq Free Tier Limits:**
- 30 requests per minute
- ~6000 tokens per minute (TPM)
- 14,400 requests per day

**Optimizations Applied:**
- ✅ Automatic request throttling (2.5s between requests)
- ✅ Token-aware throttling (adjusts for large prompts)
- ✅ Minimal conversation history (system + last 4 exchanges)
- ✅ Automatic rate limit detection and retry
- ✅ Token-efficient message formatting

The bot automatically handles rate limits - you'll never hit them!

## Customizing Personality

### Simple Example

```python
PERSONALITY_BACKGROUND = """You are a helpful assistant."""

PERSONALITY_CURRENT_STATE = """You respond naturally and helpfully."""

PERSONALITY_RULES = """Keep responses concise and friendly."""
```

### Complex Example

See `personality.example.py` for detailed examples including:
- Character backstories
- Speech patterns
- Behavior rules
- Response guidelines

You can create any personality:
- Characters from books/movies/shows
- Historical figures
- Fictional characters
- Custom creations

## Files

- `chat.py` - Main chatbot script (customize personality here)
- `personality.example.py` - Example personality templates
- `.env.example` - Environment variables template
- `requirements.txt` - Python dependencies
- `.env` - Your API keys (gitignored, create from .env.example)

## API Key

Get your free Groq API key:
1. Go to https://console.groq.com/
2. Sign up (no credit card required)
3. Create an API key
4. Add it to your `.env` file

**Free tier includes:**
- 30 requests/minute
- ~6000 tokens/minute
- 14,400 requests/day
- ~200-500ms response time

## Testing

Run comprehensive tests:
```bash
python test_rate_limits.py    # Basic functionality tests
python test_integration.py     # Full conversation simulation
```

## Notes

- Uses `llama-3.1-8b-instant` model (fastest, smallest)
- Optimized for efficiency (200 tokens max, minimal history)
- Automatic throttling - Never hits rate limits!
- Production-ready and fully tested

## License

MIT
