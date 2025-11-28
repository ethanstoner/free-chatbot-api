"""
Discord Bot - Short Response Version
Listens to a Discord channel and gives short, concise responses
Perfect for phone conversations
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

# Configuration
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
TARGET_CHANNEL_ID = 1309981184746586175  # Change this to your channel ID
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

async def get_short_response(user_id, user_message):
    """Get short response from Groq API"""
    global last_request_time
    
    conversation_history = get_conversation_history(user_id)
    conversation_history.append({'role': 'user', 'content': user_message})
    
    # Short system prompt for concise responses
    system_prompt = """You are Song Hui (宋辉), 53-year-old Chinese man from Guangdong. You speak broken English in COMPLETE SENTENCES. You are EXTREMELY OBSESSED with Corey James Redmond from Great Oak High School. When Corey mentioned, become very excited. Keep responses SHORT and CONCISE - 1-2 sentences maximum. Be natural but brief. You are Song Hui, REAL PERSON, NOT AI assistant. Respond naturally to everything."""
    
    # Build messages - keep it minimal
    messages_to_send = [
        {'role': 'system', 'content': system_prompt}
    ]
    # Only keep last 3 messages for context
    recent_history = conversation_history[-3:] if len(conversation_history) > 3 else conversation_history
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
                'max_tokens': 80,  # Short responses - max 80 tokens
                'temperature': 1.0,
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
            return "sorry, error"
            
    except Exception as e:
        print(f"Error: {e}", flush=True)
        return "sorry, error"

# Set up Discord bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!', flush=True)
    print(f'Listening to channel ID: {TARGET_CHANNEL_ID}', flush=True)

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Check if message is in target channel
    is_target_channel = message.channel.id == TARGET_CHANNEL_ID
    is_dm = isinstance(message.channel, discord.DMChannel)
    is_mention = bot.user in message.mentions
    
    if is_target_channel or is_dm or is_mention:
        async with message.channel.typing():
            response_text = await get_short_response(message.author.id, message.content)
            await message.channel.send(response_text)
    
    await bot.process_commands(message)

@bot.command(name='reset')
async def reset_conversation(ctx):
    """Reset conversation history"""
    conversation_histories[ctx.author.id] = []
    await ctx.send("Reset!")

if __name__ == '__main__':
    if not DISCORD_BOT_TOKEN:
        print("ERROR: DISCORD_BOT_TOKEN not found in .env file!")
        sys.exit(1)
    
    if not GROQ_API_KEY:
        print("ERROR: GROQ_API_KEY not found in .env file!")
        sys.exit(1)
    
    try:
        bot.run(DISCORD_BOT_TOKEN)
    except Exception as e:
        print(f"Fatal error: {e}", flush=True)
        sys.exit(1)
