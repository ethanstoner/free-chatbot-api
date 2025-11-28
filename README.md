# Free Chatbot API

A production-ready Python chatbot with fully programmable personality system. Uses Groq API for fast, free AI responses. Perfect for creating custom chatbots with any personality you want.

## Features

- **Fully Customizable Personality** - Program any character or personality you want
- **Fast Responses** - Uses Groq API (200-500ms response time)
- **Automatic Rate Limiting** - Never hits rate limits with intelligent throttling
- **Chat Channel Support** - Can respond in Discord channels or terminal
- **Simple Python** - Easy to understand and modify
- **Production Ready** - Fully tested and optimized

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

**Option A: Using .env file (Recommended)**

Edit your `.env` file and set the `PERSONALITY` variable:

```bash
PERSONALITY=You are a helpful and friendly AI assistant. You respond naturally and conversationally.
```

For multi-line personalities, you can use `\n` for newlines:
```bash
PERSONALITY="You are a helpful assistant.\n\nYou keep responses concise and friendly."
```

**Option B: Edit chat.py directly**

Edit `chat.py` and modify the default personality in the code.

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
- Automatic request throttling (2.5s between requests)
- Token-aware throttling (adjusts for large prompts)
- Minimal conversation history (system + last 4 exchanges)
- Automatic rate limit detection and retry
- Token-efficient message formatting

The bot automatically handles rate limits - you'll never hit them!

## Customizing Personality

### Simple Example (in .env)

```bash
PERSONALITY=You are a helpful assistant. You respond naturally and helpfully. Keep responses concise and friendly.
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

**Note:** The personality is loaded from the `PERSONALITY` environment variable in your `.env` file. If not set, a default friendly assistant personality is used.

## Files

- `chat.py` - Main chatbot script
- `personality.example.py` - Example personality templates
- `.env.example` - Environment variables template (includes personality config)
- `requirements.txt` - Python dependencies
- `.env` - Your API keys and personality (gitignored, create from .env.example)
- `shared_rate_limiter.py` - Rate limiting utilities (for advanced usage)
- `turn_manager.py` - Turn management for multiple bots (for advanced usage)

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

## Advanced Usage

The repository includes additional utilities:
- `shared_rate_limiter.py` - For coordinating API requests across multiple bot instances
- `turn_manager.py` - For managing turn-based responses when running multiple bots

These are optional and only needed for advanced multi-bot setups.

## Notes

- Uses `llama-3.1-8b-instant` model (fastest, smallest)
- Optimized for efficiency (200 tokens max, minimal history)
- Automatic throttling - Never hits rate limits!
- Production-ready and fully tested

## License

MIT
