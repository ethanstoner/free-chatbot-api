# Free Chatbot API - Discord Bot

A production-ready Discord bot with fully programmable personality system. Uses Groq API for fast, free AI responses. Perfect for creating custom Discord bots with any personality you want.

## Features

- **Discord Bot** - Responds to messages in Discord channels, DMs, and mentions
- **Fully Customizable Personality** - Program any character or personality you want
- **Fast Responses** - Uses Groq API (200-500ms response time)
- **Automatic Rate Limiting** - Never hits rate limits with intelligent throttling
- **Per-User Memory** - Maintains separate conversation history for each user
- **Terminal Chat** - Also includes standalone terminal chat version
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

### 2. Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section and create a bot
4. **Enable "Message Content Intent" (required!)**
5. Copy the bot token
6. Invite bot to your server with appropriate permissions

### 3. Configure

1. **Copy `.env.example` to `.env`:**
   ```bash
   cp .env.example .env
   ```

2. **Add your API keys to `.env`:**
   ```
   DISCORD_BOT_TOKEN=your_discord_bot_token_here
   GROQ_API_KEY=your_groq_api_key_here
   TARGET_CHANNEL_ID=your_channel_id_here  # Optional: specific channel, or leave empty for all channels
   ```
   - Get Discord bot token: https://discord.com/developers/applications
   - Get Groq API key: https://console.groq.com/

### 4. Customize Personality

Edit your `.env` file and set the `PERSONALITY` variable:

```bash
PERSONALITY=You are a helpful and friendly AI assistant. You respond naturally and conversationally.
```

For multi-line personalities, you can use `\n` for newlines:
```bash
PERSONALITY="You are a helpful assistant.\n\nYou keep responses concise and friendly."
```

See `personality.example.py` for detailed examples and templates.

### 5. Run Discord Bot

#### Option A: Docker (Recommended)

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

#### Option B: Direct Python

```bash
python discord_bot.py
```

The bot will:
- Respond to messages in the target channel (if `TARGET_CHANNEL_ID` is set)
- Respond to DMs
- Respond when mentioned (@bot)
- Maintain separate conversation history per user

### Commands

- `!ping` - Check if bot is responding
- `!reset` - Reset your conversation history
- `!status` - Check bot status and active conversations

## Terminal Chat (Alternative)

If you want to use the chatbot in terminal instead of Discord:

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

- `discord_bot.py` - Discord bot (main)
- `chat.py` - Terminal chat version
- `personality.example.py` - Example personality templates
- `.env.example` - Environment variables template
- `requirements.txt` - Python dependencies
- `Dockerfile` - Docker image definition
- `docker-compose.yml` - Docker Compose configuration
- `shared_rate_limiter.py` - Rate limiting utilities (for advanced multi-bot setups)
- `turn_manager.py` - Turn management for multiple bots (for advanced multi-bot setups)

## API Keys

**Discord Bot Token:**
1. Go to https://discord.com/developers/applications
2. Create application and bot
3. Enable "Message Content Intent"
4. Copy token to `.env`

**Groq API Key:**
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

The repository includes additional utilities for running multiple bots:
- `shared_rate_limiter.py` - Coordinates API requests across multiple bot instances
- `turn_manager.py` - Manages turn-based responses when running multiple bots

These are optional and only needed for advanced multi-bot setups.

## Notes

- Uses `llama-3.1-8b-instant` model (fastest, smallest)
- Optimized for efficiency (200 tokens max, minimal history)
- Automatic throttling - Never hits rate limits!
- Production-ready and fully tested
- Per-user conversation memory (separate history for each Discord user)

## License

MIT
