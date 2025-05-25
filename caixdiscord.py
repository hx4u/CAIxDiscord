import os
import io
import sys
import time
import json
import signal
import random
import asyncio
import discord
import platform
import argparse
from discord.ext import commands
from discord.ui import Button, View
from PyCharacterAI import get_client
from PyCharacterAI.exceptions import SessionClosedError

light_green = '\033[92m'
light_blue = '\033[94m'
blue = '\033[34m'
purple = '\033[38;5;129m'
red = '\033[91m' 
dark_red = '\033[38;5;52m'
bright_red = '\033[91m'
light_pink = '\033[95m'
grey = '\033[90m'
reset = '\033[0m'

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
client = None
chat = None
me = None
selected_voice_id = None
current_time =  "0"
#signal.signal(signal.SIGALRM, timeout_handler)

def print_error(e):
    print(f"\n{grey}{current_time}{red}ERRO {reset} <-> An error occurred: {e}")

def clear_screen():
    # Check OS and clear screen accordingly
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')
        
def load_config():
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print_error(e)
        return None
        
def display_help():
    help_text = (
        "                                                                                                  \n"
        "    .aMMMb  .aMMMb  dMP                    _____                                                  \n"
        "   dMP VMP dMP dMP amr  ooooooo  ooooo  __|__   |__  __  ______  ______  _____  _____      _      \n"   
        "  dMP     dMMMMMP dMP    `8888    d8'  |     |     ||__||   ___||   ___||  _  ||   __| _ _| |     \n"   
        " dMP.aMP dMP dMP dMP       Y888..8P    |      |    ||  | `-.`-. |   |__ | |_| ||  |   | |_| |     \n"  
        " VMMMP* dMP dMP dMP         `8888'     |______|  __||__||______||______||_____||__|   |___|_|     \n"
        "                           .8PY888.       |_____|                                                 \n"
        "   Character X            d8'  `888b                                                              \n"
        "           Ai Discord   o888o  o88888o    A Character AI to Discord api with TTS integration.     \n"
        "                                                                                                  \n"
        "                                          Credits: LiteKira (kil_l_y) @hx4u - Version 1.0         \n"
        " Usage: python caixdiscord.py [options]                                                           \n"
        " Options:                                                                                         \n"
        "   --options          Show this help message and exit.                                            \n"
        "   --name             Set the character's name.                                                   \n"
        "   --timeout          Set the timeout for when selecting a voice (default 9 seconds).             \n"
        "   --unexpected_replying Percentage chance (0-100) for the bot to randomly reply to messages.     \n"
        "                                                                                                  \n"
        )
    print(help_text)
    
def parse_args():
    parser = argparse.ArgumentParser(description="A Character AI to Discord api with TTS integration.")
    parser.add_argument('--options', '-o', action='store_true', help="Show the advanced options screen.")
    parser.add_argument('--name', '-n', type=str, help="Set the character's name.")
    parser.add_argument('--timeout', '-t', type=int, default=9, help="Set the timeout for when selecting a voice (default 9 seconds).")
    parser.add_argument('--unexpected_replying', '-u', '-un', type=int, default=0, help="Percentage chance (0-100) for the bot to randomly reply to messages.")
    return parser.parse_args()
    
args = parse_args()
name = args.name
timeout = args.timeout
unexpected_replying = args.unexpected_replying

config = load_config()
BOTS_DISCORD_TOKEN = config["BOTS_DISCORD_TOKEN"]
HTTP_AUTHORIZATION = config["HTTP_AUTHORIZATION"]
CHARACTER_INURL_ID = config["CHARACTER_INURL_ID"]
HISTORIES_INURL_ID = config["HISTORIES_INURL_ID"]
AIS_NAME_FOR_VOICE = args.name or config["AIS_NAME_FOR_VOICE"]

global bot_token
global http_auth
global cai_urlid
global thread_id
global voicename

bot_token = BOTS_DISCORD_TOKEN
http_auth = HTTP_AUTHORIZATION
cai_urlid = CHARACTER_INURL_ID
thread_id = HISTORIES_INURL_ID
voicename = AIS_NAME_FOR_VOICE
token = bot_token

if args.options:
    clear_screen()
    display_help()
    sys.exit(0)

def get_input_with_timeout(prompt, timeout):
    signal.alarm(timeout)
    try:
        user_input = input(prompt)
        signal.alarm(0)
        return user_input
    except TimeoutException:
        return None
        
@bot.command(name="commands")
async def help_command(ctx):
    help_text = (
        "**Available Commands:**\n"
        "`!chat [message]` — Chat with the character.\n"
        "`@name [message]` — Mention the bot to chat.\n"
        "`!image [prompt]` — Generates some images.\n"
        "`!commands` — Show this help message.\n"
        "Click 🔊  under bot message to generate speech."
    )
    await ctx.send(help_text)
    
class TTSButton(Button):
    def __init__(self, chat_id, turn_id, candidate_id, voicename, voice_id):
        super().__init__(emoji="🔊", style=discord.ButtonStyle.primary)
        self.chat_id = chat_id
        self.turn_id = turn_id
        self.candidate_id = candidate_id
        self.CHARACTER_NAME = voicename
        self.voice_id = voice_id  # Pass the selected voice ID
    async def callback(self, interaction: discord.Interaction):
        # Disable the button immediately after clicking
        self.disabled = True
        # Update the message to show the disabled button
        await interaction.response.edit_message(view=self.view)
        try:
            # Generate the speech using the passed voice_id
            speech = await client.utils.generate_speech(
                self.chat_id, self.turn_id, self.candidate_id, self.voice_id
            )
            # Save the speech to a file
            filepath = f"voice_{self.turn_id}.mp3"
            with open(filepath, "wb") as f:
                f.write(speech)
            # Send the audio file as a follow-up
            await interaction.followup.send(
                content="``Generated TTS:``",
                file=discord.File(filepath),
                ephemeral=True  # Optional: You can set ephemeral=False to make it visible to everyone
            )
            # Clean up the audio file after sending
            os.remove(filepath)
        except Exception as e:
            # Handle errors and inform the user
            current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            print_error(e)

async def find_voice_id():
    global selected_voice_id
    client = await get_client(token=http_auth)
    try:
        voices = await client.utils.search_voices(voicename)
        if not voices:
            current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            print(f"{grey}{current_time}{light_blue} INFO {reset}     No voices found for character: {voicename}")
            return None
        if token == "0":
            selected_voice_id = voices[0].voice_id
            current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            print(f"{grey}{current_time}{light_green} EXEC {reset} <-> Selected voice ID: {selected_voice_id} for character: {voicename}")
            return selected_voice_id
        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        print(f"{grey}{current_time}{light_blue} INFO {reset}     Found voices for {voicename}:")
        
        user_input = get_input_with_timeout(f"{grey}{current_time}{light_green} USER {reset} >-- Select a voice ID from list? (Defaults to first voice found)." + " (Y/n): ", timeout)
        
        if user_input != None:
            user_input = user_input.lower()
            
            if user_input == 'y':
                count = 0
                current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                print(f"")
                print(f"{grey}╔═{reset}num: voice-identifier:         voice-name:")
                for voice in voices:
                    print(f"{grey}║#{reset} {count:02}: {voice.voice_id}: {voice.name}")
                    count += 1
                print(f"{grey}╚════════════════════════════════════════════╗")
                user_input = input(f"{grey}{current_time}{light_green} USER {reset} <-> Select a voice (#): ").lower()
                
                if user_input.isdigit():
                    voice_select = int(user_input)
                    selected_voice_id = voices[voice_select].voice_id
                    return selected_voice_id
                else:
                    print(f"{grey}{current_time}{light_blue} INFO {reset}     Must be a number... Using voice 0.")
                    selected_voice_id = voices[0].voice_id
                    return selected_voice_id
                    
            if user_input == 'n':
                current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                print(f"{grey}{current_time}{light_green} EXEC {reset} --> OK... Using voice 0.")
                selected_voice_id = voices[0].voice_id
                return selected_voice_id
                
            if user_input == None:
                current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                print(f"{grey}{current_time}{light_green} EXEC {reset} <-> No response... defaulting to voice 0.")
                selected_voice_id = voices[0].voice_id
                return selected_voice_id
            else:
                current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                print(f"{grey}{current_time}{light_green} EXEC {reset} --> Incorrect response... defaulting to voice 0.")          
                selected_voice_id = voices[0].voice_id
                return selected_voice_id
            
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
        
# Make sure to set the voice_id during on_ready to ensure it's set before usage
@bot.event
async def on_ready():
    global client, chat, me
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    print(f"{grey}{current_time}{blue} EXEC {reset} --> Logged in as {light_blue} {bot.user}")
    client = await get_client(token=http_auth)
    chat = await client.chat.fetch_chat(thread_id)
    me = await client.account.fetch_me()

    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    print(f"{grey}{current_time}{blue} EXEC {reset} --> Authenticated as {light_green}@{me.username}")
    
    # Fetch voice_id after bot logs in
    voice_id = await find_voice_id()
    
    if voice_id:
        print(f"{grey}{current_time}{blue} EXEC {reset} --> Voice ID for {voicename}: {voice_id}")
    else:
        print(f"{grey}{current_time}{red} ERRO {reset} <-> Could not find voice ID.")
    print(f"{grey}{current_time}{light_blue} INFO {reset}     API is active and bot is ready.")

# Update on_message to use the dynamic voice_id
@bot.event
async def on_message(message):
    client = await get_client(token=http_auth)  # Use AI_TOKEN instead of token
    if message.author == bot.user:
        return
        
    if unexpected_replying > 0 and random.randint(1, 100) <= unexpected_replying:
        # Handle unexpected replies
        user_message = message.content
#        reply, chat_id, turn_id, candidate_id = await client.chat.send_message(cai_urlid, thread_id, user_message)
        reply, chat_id, turn_id, candidate_id = await client.chat.send_message(cai_urlid, chat.chat_id, user_message)

        if reply:
            # Create a TTS button after the reply
            tts_button = TTSButton(chat_id, turn_id, candidate_id)
            view = View(timeout=None)  # Disable timeout so the button stays active
            view.add_item(tts_button)
            await message.channel.send(reply, view=view)
        else:
            await message.channel.send("``- could not get response -``")
    
    # Handle replies to the bot's messages
    if message.reference and message.reference.resolved.author == bot.user:
        user_message = message.content
        reply, chat_id, turn_id, candidate_id = await client.chat.send_message(cai_urlid, chat.chat_id, user_message)
        if reply:
            tts_button = TTSButton(chat_id, turn_id, candidate_id)
            view = View(timeout=None)
            view.add_item(tts_button)
            await message.channel.send(reply, view=view)
        else:
            await message.channel.send("``- could not get response -``")
            
    elif bot.user.mentioned_in(message):
        user_message = message.content
        reply, chat_id, turn_id, candidate_id = await client.chat.send_message(cai_urlid, chat.chat_id, user_message)
        if reply:
            tts_button = TTSButton(chat_id, turn_id, candidate_id)
            view = View(timeout=None)
            view.add_item(tts_button)
            await message.channel.send(reply, view=view)
        else:
            await message.channel.send("``- could not get response -``")
            
    if message.content.startswith("!chat"):
        user_message = message.content[len("!chat "):]
        if user_message:
            reply, chat_id, turn_id, candidate_id = await client.chat.send_message(cai_urlid, chat.chat_id, user_message)
            if reply:
                tts_button = TTSButton(chat_id, turn_id, candidate_id)
                view = View(timeout=None)
                view.add_item(tts_button)
                await message.channel.send(reply, view=view)
            else:
                await message.channel.send("``- could not get response -``")
        else:
            await message.channel.send("Please provide a message after ``!chat``")
    
    elif message.content.startswith("!image"):
        prompt = message.content[len("!image "):]
        if prompt:
            image_url = await generate_image_from_prompt(prompt)
            if image_url:
                await message.channel.send(f"{image_url}")
            else:
                await message.channel.send("``- could not generate image -``")
        else:
            await message.channel.send("Please provide a prompt after ``!image``")
            
async def send_character_message(message):
    try:
        answer = await client.chat.send_message(http_auth, cai_urlid, message)
        reply_text = answer.get_primary_candidate().text

        # Use voice_id instead of selected_voice_id
        view = View()
        view.add_item(TTSButton(
            chat.chat_id,
            answer.turn_id,
            answer.get_primary_candidate().candidate_id,
            answer.author_name,
            voice_id  # Use the voice_id parameter
        ))

        await message.channel.send(content=reply_text, view=view)
        
    except SessionClosedError:
        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        print(f"{grey}{current_time}{light_blue} INFO {reset}     Session closed. Try again later.")
    except Exception as e:
        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        print(f"{grey}{current_time}{red} ERRO {reset} <-> {e}")
        
async def main():
    client = await get_client(token=token)
    me = await client.account.fetch_me()
    print(f'Authenticated as @{me.username}')
    chat, greeting_message = await client.chat.create_chat(character_id)
    print(f"[{greeting_message.author_name}]: {greeting_message.get_primary_candidate().text}")
    try:
        while True:
            message = input(f"[{me.name}]: ")
            answer = await client.chat.send_message(character_id, chat.chat_id, message, streaming=True)
            printed_length = 0
            async for message in answer:
                if printed_length == 0:
                    print(f"[{message.author_name}]: ", end="")
                text = message.get_primary_candidate().text
                print(text[printed_length:], end="")
                printed_length = len(text)
            print("\n")
    except SessionClosedError:
        print("session closed. Bye!")
    finally:
        await client.close_session()

bot.run(bot_token)
