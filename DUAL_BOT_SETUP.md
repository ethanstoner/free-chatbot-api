# Dual Bot Setup - Song Hui + Second Bot Conversation

This guide shows you how to set up two Discord bots that can converse with each other!

## Setup Steps

### 1. Create a Second Discord Bot

1. Go to https://discord.com/developers/applications
2. Click "New Application"
3. Name it something like "Alex Bot" or "Second Bot"
4. Go to "Bot" section
5. Click "Add Bot"
6. Copy the bot token
7. Enable "Message Content Intent" (required!)
8. Invite the bot to your server with these permissions:
   - Send Messages
   - Read Message History
   - Use External Emojis

### 2. Add Second Bot Token to .env

Edit your `.env` file and add:
```
DISCORD_BOT_TOKEN_2=your_second_bot_token_here
```

### 3. Run Both Bots

**Terminal 1 - Song Hui Bot:**
```bash
cd "/home/ethan/cursor projects/free-chatbot-api"
source venv/bin/activate
python discord_bot.py
```

**Terminal 2 - Second Bot:**
```bash
cd "/home/ethan/cursor projects/free-chatbot-api"
source venv/bin/activate
python discord_bot_2.py
```

Or use the batch files:
- `start_discord_bot.bat` - Song Hui
- `start_bot_2.bat` - Second Bot (create this)

### 4. How It Works

- **Song Hui bot** (`discord_bot.py`) responds to messages normally
- **Second bot** (`discord_bot_2.py`) listens for Song Hui's messages and responds to them
- Both bots are in the same channel, so they can talk to each other!

## Customizing the Second Bot's Personality

Edit `discord_bot_2.py` and change the `system_prompt` variable. Some ideas:

### Option 1: Normal Teenager (Current)
- Finds Song Hui's behavior concerning
- Sarcastic but well-meaning
- Normal English

### Option 2: Another Unhinged Character
- Maybe another obsessed person
- Different obsession (not Corey)
- Could create chaos

### Option 3: Concerned Friend
- Tries to help Song Hui
- More empathetic
- Wants to understand him

### Option 4: Troll/Chaos Character
- Messes with Song Hui
- Asks weird questions
- Creates confusion

## Commands

- `!find_song_hui` - Manually find Song Hui bot ID
- `!reset` - Reset conversation history

## Tips

- Make sure both bots have "Message Content Intent" enabled
- Both bots need to be in the same channel
- The second bot will automatically detect Song Hui after a few messages
- You can manually set `SONG_HUI_BOT_ID` in the code if needed

## Troubleshooting

**Bot 2 doesn't respond to Song Hui:**
- Run `!find_song_hui` command
- Check that both bots are in the same channel
- Make sure Song Hui bot has sent at least one message

**Rate limiting:**
- Both bots share the same Groq API key
- They both have 3-second throttling
- May need to stagger their responses
