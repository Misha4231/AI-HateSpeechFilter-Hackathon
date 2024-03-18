import discord
from discord.ext import commands
from collections import Counter
import re
import time

#intents = discord.Intents.all()
#intents.messages = True
#
#bot = commands.Bot(command_prefix='!', intents=intents)

# Threshold for spam detection
SPAM_THRESHOLD = 3
# Time in seconds for decay
DECAY_TIME = 30  

# Cache to store recent messages per user along with their timestamps
recent_messages = {}

k=False
    
#@bot.event
#async def on_message(message):
#    await onMessageScamCheck(message)


async def onMessageScamCheck(message):
    global k

    # Check for spam
    if is_spam(message):
        await message.delete()
        if not k:
            await message.channel.send(f"{message.author.mention}, please refrain from spamming.")
            k=True
        # Sprawdzanie, czy wiadomość zawiera spam
    if is_alot(message.content):
        await message.channel.send("Please, don't spam.")
        await message.delete()


    
def is_alot(content):
    # Normalizacja wiadomości do małych liter
    content = content.lower()
    
    # Sprawdzanie, czy wiadomość zawiera powtarzające się ciągi znaków (np. "aaaaa")
    if re.search(r'(\w)\1{3,}', content):
        return True
    return False

def is_spam(message):
    user_id = message.author.id
    content = message.content.lower()

    # Remove old messages from cache
    remove_old_messages()

    # Check if the user is in the cache
    if user_id in recent_messages:
        # Count occurrences of the user's last few messages
        count = sum(1 for msg, _ in recent_messages[user_id] if msg == content)
        # If the count exceeds the threshold, it's considered spam
        if count >= SPAM_THRESHOLD:
            
            return True
    else:
        k="n"
        # If the user is not in the cache, add them
        recent_messages[user_id] = []

    # Add the current message to the user's recent messages
    recent_messages[user_id].append((content, time.time()))

    return False

def remove_old_messages():
    global recent_messages  # Declare recent_messages as global
    current_time = time.time()
    for user_id, messages in recent_messages.items():
        recent_messages[user_id] = [(msg, timestamp) for msg, timestamp in messages if current_time - timestamp <= DECAY_TIME]

    # Remove empty entries from the cache
    recent_messages = {user_id: messages for user_id, messages in recent_messages.items() if messages}
