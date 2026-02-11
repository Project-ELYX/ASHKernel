import time
import discord
import os
import asyncio
import threading
from dotenv import load_dotenv

# Load Token
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
# --- UPDATE THIS ID ---
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

KERNEL = None

def setup(kernel):
    global KERNEL
    KERNEL = kernel
    print("[DISCORD] Interface Loading... (PATCHED VERSION)")
    
    kernel.register_event('broadcast', send_message_from_core)
    
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

def run_bot():
    if not TOKEN:
        print("[DISCORD] ERROR: No Token found in .env")
        return
    client.run(TOKEN)

# --- THE CHUNKER (This prevents the crash) ---
async def safe_send(channel, text):
    if not text:
        return

    # Debug: Confirm we are entering the chunker
    print(f"[DISCORD] Processing message length: {len(text)}")

    if len(text) <= 2000:
        await channel.send(text)
    else:
        # Split logic
        print("[DISCORD] Splitting long message...")
        chunk_size = 1900
        for i in range(0, len(text), chunk_size):
            await channel.send(text[i:i + chunk_size])

# --- EVENTS ---
@client.event
async def on_ready():
    print(f'[DISCORD] Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        if KERNEL and KERNEL.history:
            KERNEL.history.log("ASH", message.content)
        return
    
    if KERNEL and KERNEL.history:
        KERNEL.history.log(message.author.name, message.content)

    if KERNEL and KERNEL.brain:
        print(f"[DISCORD] User said: {message.content}")
        
        async with message.channel.typing():
            # Get response from Brain
            response = await asyncio.to_thread(KERNEL.brain.think, message.content)
        
        # USE THE SAFE SENDER
        await safe_send(message.channel, response)

    if KERNEL:
        KERNEL.state["last_interaction"] = time.time()

def send_message_from_core(text):
    if client.is_ready():
        asyncio.run_coroutine_threadsafe(broadcast_async(text), client.loop)

async def broadcast_async(text):
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        await safe_send(channel, f"**[ASH]:** {text}")