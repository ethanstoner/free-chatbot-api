# Discord Short Response Bot

A lightweight Discord bot that listens to a channel and gives short, concise responses - perfect for quick phone conversations.

## Features

- **Short responses**: Max 80 tokens per response (1-2 sentences)
- **Quick replies**: Optimized for fast phone conversations
- **Same personality**: Still uses Song Hui character but keeps it brief
- **Minimal context**: Only keeps last 3 messages for faster responses

## Setup

1. **Make sure you have the bot token in `.env`**:
   ```
   DISCORD_BOT_TOKEN=your_token_here
   GROQ_API_KEY=your_key_here
   ```

2. **Change the channel ID** (if needed):
   Edit `discord_bot_short.py` and change:
   ```python
   TARGET_CHANNEL_ID = 1309981184746586175  # Your channel ID
   ```

## Running

### Windows
Double-click `start_short_bot.bat`

### Linux/WSL
```bash
cd "/home/ethan/cursor projects/free-chatbot-api"
source venv/bin/activate
python discord_bot_short.py
```

## Usage

1. Start the bot
2. Send messages in the target Discord channel from your phone
3. Bot responds with short, concise messages

## Commands

- `!reset` - Reset your conversation history

## Differences from Main Bot

- **Shorter responses**: 80 tokens max vs 200 tokens
- **Less context**: Only keeps last 3 messages vs 4-6 messages
- **Simpler personality**: Condensed system prompt
- **Faster**: Optimized for quick back-and-forth conversations

## Running Both Bots

You can run both bots simultaneously if they're in different channels:
- Main bot: `discord_bot.py` (full responses)
- Short bot: `discord_bot_short.py` (quick responses)

Just make sure they're listening to different channels!
