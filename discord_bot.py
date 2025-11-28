"""
Discord Bot - Fully Customizable Personality
Run: python discord_bot.py
"""

import sys
sys.dont_write_bytecode = True

import os
import time
import requests
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Request throttling: Groq free tier allows 30 requests/minute, ~6000 tokens/minute
MIN_REQUEST_INTERVAL = 2.5  # seconds between requests
last_request_time = 0

def estimate_tokens(text):
    """Rough token estimation: 1 token ≈ 4 characters"""
    return len(text) // 4

def throttle_request(estimated_tokens=0):
    """Ensure minimum time between requests to avoid rate limits"""
    global last_request_time
    current_time = time.time()
    time_since_last = current_time - last_request_time
    
    min_interval = MIN_REQUEST_INTERVAL
    if estimated_tokens > 4000:
        min_interval = max(MIN_REQUEST_INTERVAL, estimated_tokens / 100)
    
    if time_since_last < min_interval:
        wait_time = min_interval - time_since_last
        if wait_time > 0.1:
            print(f"⏳ Throttling: waiting {wait_time:.1f}s to avoid rate limits...")
        time.sleep(wait_time)
    
    last_request_time = time.time()

# Load environment variables
load_dotenv()

# Configuration
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
TARGET_CHANNEL_ID = int(os.getenv('TARGET_CHANNEL_ID', '0'))
PERSONALITY = os.getenv('PERSONALITY', """You are a helpful and friendly AI assistant. 
You enjoy helping people and having conversations.

CURRENT STATE & BEHAVIOR:
- You respond naturally and conversationally
- You are friendly and approachable
- You keep responses concise (1-3 sentences usually)

RULES:
- Speak in COMPLETE SENTENCES with FULL THOUGHTS
- Keep responses CONCISE - 1-3 sentences usually
- NEVER answer your own questions
- DO NOT use asterisks, parentheses, or action descriptions
- You are a REAL PERSON, NOT an AI assistant
- Respond naturally to EVERYTHING people say
- Match their energy and language style""")

# Validate configuration
if not DISCORD_BOT_TOKEN:
    print("ERROR: DISCORD_BOT_TOKEN not found in .env file!")
    print("Please copy .env.example to .env and add your Discord bot token.")
    sys.exit(1)

if not GROQ_API_KEY:
    print("ERROR: GROQ_API_KEY not found in .env file!")
    print("Please copy .env.example to .env and add your Groq API key.")
    sys.exit(1)

# Setup Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Per-user conversation history
conversation_histories = {}

def get_conversation_history(user_id):
    """Get or create conversation history for a user"""
    if user_id not in conversation_histories:
        conversation_histories[user_id] = [
            {'role': 'system', 'content': PERSONALITY}
        ]
    return conversation_histories[user_id]

def reset_conversation_history(user_id):
    """Reset conversation history for a user"""
    conversation_histories[user_id] = [
        {'role': 'system', 'content': PERSONALITY}
    ]

@bot.event
async def on_ready():
    print(f'✅ Bot logged in as {bot.user}')
    if TARGET_CHANNEL_ID:
        print(f' channel ID: {TARGET_CHANNEL_ID}')
    else:
        print('⚠️  No TARGET_CHANNEL_ID set - bot will respond to all channels')

@bot.event
async def on_message(message):
    # Ignore bot's own messages
    if message.author == bot.user:
        return
    
    # Check if message is in target channel (if set)
    if TARGET_CHANNEL_ID and message.channel.id != TARGET_CHANNEL_ID:
        return
    
    # Check if bot is mentioned or message is a DM
    is_mentioned = bot.user in message.mentions
    is_dm = isinstance(message.channel, discord.DMChannel)
    
    # Only respond to mentions, DMs, or messages in target channel
    if not (is_mentioned or is_dm or TARGET_CHANNEL_ID):
        return
    
    # Process commands first
    await bot.process_commands(message)
    
    # Don't respond to commands (they handle their own responses)
    if message.content.startswith('!'):
        return
    
    # Get conversation history for this user
    conversation_history = get_conversation_history(message.author.id)
    
    # Add user message
    conversation_history.append({'role': 'user', 'content': message.content})
    
    # Keep history manageable (last 4 exchanges)
    if len(conversation_history) > 9:  # system + 4 exchanges
        conversation_history = [conversation_history[0]] + conversation_history[-8:]
        conversation_histories[message.author.id] = conversation_history
    
    # Estimate tokens and throttle
    estimated_tokens = estimate_tokens(PERSONALITY + message.content)
    throttle_request(estimated_tokens)
    
    # Show typing indicator
    async with message.channel.typing():
        # Make API request
        try:
            response = requests.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {GROQ_API_KEY}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'llama-3.1-8b-instant',
                    'messages': conversation_history,
                    'max_tokens': 200,
                    'temperature': 0.9
                },
                timeout=15
            )
            
            if response.status_code == 200:
                response_data = response.json()
                bot_response = response_data['choices'][0]['message']['content']
                
                # Add bot response to history
                conversation_history.append({'role': 'assistant', 'content': bot_response})
                
                # Split long messages (Discord limit is 2000 chars)
                if len(bot_response) > 2000:
                    chunks = [bot_response[i:i+2000] for i in range(0, len(bot_response), 2000)]
                    for chunk in chunks:
                        await message.channel.send(chunk)
                else:
                    await message.channel.send(bot_response)
                    
            elif response.status_code == 429:
                await message.channel.send("⏳ Rate limited! Please wait a moment...")
            else:
                await message.channel.send(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"Error: {e}")
            await message.channel.send(f"❌ Error occurred: {str(e)}")

@bot.command(name='ping')
async def ping(ctx):
    """Check if bot is responding"""
    await ctx.send('Pong!')

@bot.command(name='reset')
async def reset(ctx):
    """Reset conversation history"""
    reset_conversation_history(ctx.author.id)
    await ctx.send('✅ Conversation history reset!')

@bot.command(name='status')
async def status(ctx):
    """Check bot status"""
    status_msg = f"✅ Bot is online!\n"
    status_msg += f"📝 Personality loaded: {len(PERSONALITY)} characters\n"
    status_msg += f"💬 Active conversations: {len(conversation_histories)}"
    await ctx.send(status_msg)

if __name__ == '__main__':
    try:
        print("Starting Discord bot...")
        print(f"Personality loaded: {len(PERSONALITY)} characters")
        bot.run(DISCORD_BOT_TOKEN)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
