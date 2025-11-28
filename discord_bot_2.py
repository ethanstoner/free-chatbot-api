"""
Discord Bot #2 - Different Personality
Converse with Song Hui bot
"""

import sys
sys.dont_write_bytecode = True

import os
import time
import asyncio
import requests
from dotenv import load_dotenv
import discord
from discord.ext import commands

# Load environment variables
load_dotenv()

# Configuration - YOU NEED A SECOND DISCORD BOT TOKEN FOR THIS
# Create a second bot at https://discord.com/developers/applications
DISCORD_BOT_TOKEN_2 = os.getenv('DISCORD_BOT_TOKEN_2')  # Second bot token
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
TARGET_CHANNEL_ID = 1309981184746586175  # Same channel as Song Hui
TARGET_SERVER_ID = 1309981184746586172

# Request throttling
MIN_REQUEST_INTERVAL = 3.0
last_request_time = 0
rate_limit_lock = asyncio.Lock()

# Conversation history per user
conversation_histories = {}

def get_conversation_history(user_id):
    """Get or create conversation history for a user"""
    if user_id not in conversation_histories:
        conversation_histories[user_id] = []
    return conversation_histories[user_id]

async def get_response(user_id, user_message, song_hui_message=None):
    """Get response from Groq API"""
    global last_request_time
    
    conversation_history = get_conversation_history(user_id)
    conversation_history.append({'role': 'user', 'content': user_message})
    
    # If Song Hui just messaged, include that context
    if song_hui_message:
        conversation_history.append({'role': 'assistant', 'content': f'Song Hui said: {song_hui_message}'})
    
    # Personality: Alex - Normal American teenager who finds Song Hui's behavior concerning
    system_prompt = """You are Alex, a 17-year-old American high school student. You're pretty normal - you like video games, hanging out with friends, typical teenager stuff. You're in a Discord server and there's this weird Chinese guy named Song Hui who keeps talking about some guy named Corey and seems really obsessed. You find his behavior kind of concerning and creepy, but you're also curious and sometimes try to be nice to him. You speak normal English (not broken). You're a bit sarcastic sometimes, but generally well-meaning. You respond naturally to what people say. Keep responses casual and conversational - 1-3 sentences usually. You're not mean, but you're honest about finding Song Hui's behavior weird."""
    
    # Build messages - keep it minimal
    messages_to_send = [
        {'role': 'system', 'content': system_prompt}
    ]
    # Only keep last 4 messages for context
    recent_history = conversation_history[-4:] if len(conversation_history) > 4 else conversation_history
    messages_to_send.extend(recent_history)
    
    # Throttle requests
    async with rate_limit_lock:
        current_time = time.time()
        time_since_last = current_time - last_request_time
        
        if time_since_last < MIN_REQUEST_INTERVAL:
            wait_time = MIN_REQUEST_INTERVAL - time_since_last
            await asyncio.sleep(wait_time)
        
        last_request_time = time.time()
    
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
                'messages': messages_to_send,
                'max_tokens': 150,
                'temperature': 0.9,
                'stream': False
            },
            timeout=15
        )
        
        if response.status_code == 200:
            bot_response = response.json()['choices'][0]['message']['content']
            if bot_response and bot_response.strip():
                conversation_history.append({'role': 'assistant', 'content': bot_response})
                return bot_response.strip()
            return "okay"
        else:
            return "hmm"
            
    except Exception as e:
        print(f"Error: {e}", flush=True)
        return "sorry, error"

# Set up Discord bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Track Song Hui's bot user ID (you'll need to set this)
SONG_HUI_BOT_ID = None  # Will be set when Song Hui bot is detected

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!', flush=True)
    print(f'Listening to channel ID: {TARGET_CHANNEL_ID}', flush=True)
    
    # Try to find Song Hui bot
    channel = bot.get_channel(TARGET_CHANNEL_ID)
    if channel:
        async for message in channel.history(limit=10):
            if message.author.name == "Song Hui" or "Song Hui" in str(message.author):
                global SONG_HUI_BOT_ID
                SONG_HUI_BOT_ID = message.author.id
                print(f'Found Song Hui bot: {SONG_HUI_BOT_ID}', flush=True)
                break

@bot.event
async def on_message(message):
    # Ignore messages from this bot itself
    if message.author == bot.user:
        return
    
    # Check if message is in target channel
    is_target_channel = message.channel.id == TARGET_CHANNEL_ID
    is_dm = isinstance(message.channel, discord.DMChannel)
    is_mention = bot.user in message.mentions
    
    # Check if this is Song Hui's message
    is_song_hui = SONG_HUI_BOT_ID and message.author.id == SONG_HUI_BOT_ID
    
    if is_target_channel or is_dm or is_mention or is_song_hui:
        # If Song Hui just messaged, respond to him
        if is_song_hui:
            async with message.channel.typing():
                response_text = await get_response(
                    message.author.id, 
                    "Song Hui just messaged in the channel",
                    song_hui_message=message.content
                )
                await message.channel.send(response_text)
        # Otherwise respond normally
        elif is_target_channel or is_dm or is_mention:
            async with message.channel.typing():
                response_text = await get_response(message.author.id, message.content)
                await message.channel.send(response_text)
    
    await bot.process_commands(message)

@bot.command(name='reset')
async def reset_conversation(ctx):
    """Reset conversation history"""
    conversation_histories[ctx.author.id] = []
    await ctx.send("Reset!")

@bot.command(name='find_song_hui')
async def find_song_hui(ctx):
    """Try to find Song Hui bot"""
    channel = ctx.channel
    async for message in channel.history(limit=20):
        if "Song Hui" in str(message.author.name) or message.author.bot:
            global SONG_HUI_BOT_ID
            SONG_HUI_BOT_ID = message.author.id
            await ctx.send(f"Found bot: {message.author.name} (ID: {SONG_HUI_BOT_ID})")
            return
    await ctx.send("Couldn't find Song Hui bot. Make sure it's in this channel.")

if __name__ == '__main__':
    if not DISCORD_BOT_TOKEN_2:
        print("ERROR: DISCORD_BOT_TOKEN_2 not found in .env file!")
        print("You need to create a second Discord bot and add its token to .env")
        print("Create one at: https://discord.com/developers/applications")
        sys.exit(1)
    
    if not GROQ_API_KEY:
        print("ERROR: GROQ_API_KEY not found in .env file!")
        sys.exit(1)
    
    try:
        bot.run(DISCORD_BOT_TOKEN_2)
    except Exception as e:
        print(f"Fatal error: {e}", flush=True)
        sys.exit(1)
