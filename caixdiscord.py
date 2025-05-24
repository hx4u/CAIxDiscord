import platform
import asyncio
import json
import discord
import random
import argparse
from discord.ext import commands
from discord.ui import Button, View
from PyCharacterAI import get_client
import os
import time

gre = '\033[92m'
blu = '\033[94m'
blue = '\033[34m'
purple = '\033[38;5;129m'
red = '\033[91m' 
dark_red = '\033[38;5;52m'
bright_red = '\033[91m'
light_pink = '\033[95m'
grey = '\033[90m'
reset = '\033[0m'

def clear_screen():
    # Check OS and clear screen accordingly
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

# Load configuration from config.json
def load_config():
    with open('config.json', 'r') as f:
        config = json.load(f)
    return config

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
        "   --name             Set the character's name.                                                   \n"
        "   --timeout          Set the timeout for when selecting a voice (default 9 seconds).             \n"
        "   --unexpected_replying Percentage chance (0-100) for the bot to randomly reply to messages.     \n"
        "                                                                                                  \n"
        )
    print(help_text)

async def chat_with_character(token, character_id, user_message, history_thread_id):
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    client = await get_client(token=token)

    try:
        # Fetch account information
        me = await client.account.fetch_me()
        print(f"{grey}{current_time}{gre} USER {reset} <-> Logged in as @{me.username}")

        # Create or continue a chat using the provided history_thread_id
        chat, greeting = await client.chat.create_chat(character_id, history_thread_id)

        # You can uncomment this line if you want to print the greeting message
        # print(f"{grey}{current_time}{blu} INFO {reset} <-> {greeting.author_name}: {greeting.get_primary_candidate().text}")

        # Send the user message, passing history_thread_id to maintain conversation continuity
        async for response in client.chat.send_message(character_id, chat.chat_id, user_message, history_thread_id):
            # Ensure that the response is valid before accessing primary candidate
            if hasattr(response, 'get_primary_candidate'):
                reply = response.get_primary_candidate().text
                print(f"{grey}{current_time}{blu} INFO {reset} <-> {response.author_name}: {reply}")
                return reply, chat.chat_id, response.turn_id, response.get_primary_candidate().candidate_id
            else:
                print(f"{grey}{current_time}{red} ERROR{reset} <-> No primary candidate found in response.")

    except Exception as e:
        print(f"{grey}{current_time}{red} ERROR{reset} <-> An error occurred: {e}")
        return None, None, None, None
    
    finally:
        # Ensure the session is properly closed after the operation
        await client.close_session()


# Function to find and select the voice ID
async def find_voice_id(cai_client, voicename):
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    try:
        voices = await cai_client.utils.search_voices(voicename)

        if not voices:
            print("No voices found.")
            return None

        # Select the first voice by default
        selected_voice_id = voices[0].voice_id
        print(f"{grey}{current_time}{blu} INFO {reset} <-- Selected voice ID: {selected_voice_id}")
        return selected_voice_id

    except Exception as e:
        print("{grey}{current_time}{red} ERROR{reset} <-> Error: {e}")
        return None

# Function to search voice packs
async def search_voice_packs(cai_client, voicename):
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    try:
        voices = await cai_client.utils.search_voices(voicename)

        if voices:
            print(f"{grey}{current_time}{blu} INFO {reset} <-> Found {len(voices)} voice packs for {voicename}.")
            print(f"{grey}╔═{reset}num: voice-identifier:         voice-name:")
            for idx, voice in enumerate(voices[:99]):  # Display up to 99 voice packs
                # Format numbers 0-9 with leading zeros
                print(f"{grey}║#{reset}{str(idx + 1).zfill(2)}: {voice.voice_id}, {voice.name}")
            print(f"{grey}╚═══════════════════════════════════╗{reset}")
            # Prompt user to select a voice pack
            selection = input(f"Please select a voice pack (1-{len(voices)}): ").strip()

            if selection.isdigit():
                selection_index = int(selection) - 1
                if 0 <= selection_index < len(voices):
                    selected_voice_id = voices[selection_index].voice_id
                    print(f"{grey}{current_time}{blu} INFO {reset} <-- Selected voice pack: {voices[selection_index].name} ({selected_voice_id})")
                    return selected_voice_id
                else:
                    print(f"{grey}{current_time}{blu} INFO {reset} <-> Invalid selection. Using default voice pack.")
                    return voices[0].voice_id
            else:
                print(f"{grey}{current_time}{blu} INFO {reset} <-> Invalid input. Using default voice pack.")
                return voices[0].voice_id
        else:
            print(f"{grey}{current_time}{red} ERROR{reset} <-> No voice packs found.")
            return None
    except Exception as e:
        print(f"{grey}{current_time}{red} ERROR{reset} <-> Error searching for voice packs: {e}")
        return None

# Discord Bot Setup
config = load_config(

# Extract values from the config
TOKEN = config.get("BOTS_DISCORD_TOKEN")
AI_TOKEN = config.get("HTTP_AUTHORIZATION")
CHARACTER_ID = config.get("CHARACTER_INURL_ID")
HISTORY_THREAD_ID = config.get("HISTORIES_INURL_ID")  # Load history thread ID from config
history_thread_id = HISTORY_THREAD_ID
VOICENAME = config.get("AIS_NAME_FOR_VOICE")

# Command-line argument parsing
parser = argparse.ArgumentParser(description="Discord Bot with Unexpected Reply Feature.")
parser.add_argument("--unexpected_reply", type=int, default=0, help="Chance of unexpected reply (0 to 100).")
parser.add_argument("--name", type=str, help="Override the voice name from the config.")
parser.add_argument('--clear', '-c', action='store_true', help="Clear the screen on start.")

args = parser.parse_args()
global unexpected_replying
unexpected_replying = args.unexpected_reply

# Use --name flag if provided, otherwise use the name from config.json
voice_name = args.name if args.name else VOICENAME

# Create bot instance
intents = discord.Intents.default()
intents.message_content = True  # Make sure to enable this intent for reading message content
bot = commands.Bot(command_prefix="!", intents=intents)

# Select voice on bot startup
selected_voice_id = None
async def setup_voice():
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    global selected_voice_id
    cai_client = await get_client(token=AI_TOKEN)
    
    # Ask user if they want to search for voice packs
    user_input = input(f"{grey}{current_time}{gre} USER {reset} --> Would you like to search for voice packs? (Y/n): ").strip().lower()

    if user_input == "y":
        selected_voice_id = await search_voice_packs(cai_client, voice_name)

    if not selected_voice_id:
        selected_voice_id = await find_voice_id(cai_client, voice_name)
    await cai_client.close_session()

@bot.event
async def on_ready():
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    print(f"{grey}{current_time}{gre} USER {reset} --> Logged in as {bot.user.name} ({bot.user.id})")
    print(f"{grey}{current_time}{blu} INFO {reset} <-- AI History ID : {HISTORY_THREAD_ID}")
    await setup_voice()

# TTS Button
class TTSButton(Button):
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    def __init__(self, chat_id: str, turn_id: str, candidate_id: str):
        super().__init__(label="🔊", style=discord.ButtonStyle.green)
        self.chat_id = chat_id
        self.turn_id = turn_id
        self.candidate_id = candidate_id
        self.disabled = False  # Button is initially enabled

    async def callback(self, interaction: discord.Interaction):
        # Generate TTS audio
        tts_audio = await generate_tts(self.chat_id, self.turn_id, self.candidate_id)
        
        # If TTS audio is generated, send it and disable the button
        if tts_audio:
            await interaction.response.send_message("", file=discord.File(tts_audio, filename="TTS.mp3"))

            # Disable the button after TTS has been generated and sent
            self.disabled = True
            # Update the view to reflect the disabled state of the button
            view = View(timeout=None)  # Disable timeout so the button remains disabled
            view.add_item(self)  # Re-add the button to the view
            await interaction.message.edit(view=view)
        else:
            await interaction.response.send_message("Sorry, something went wrong with TTS generation.")

async def generate_tts(chat_id: str, turn_id: str, candidate_id: str):
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    try:
        cai_client = await get_client(token=AI_TOKEN)
        
        # Generate speech from the character's reply using the selected voice
        speech = await cai_client.utils.generate_speech(
            chat_id, turn_id, candidate_id, selected_voice_id
        )

        # Save the TTS speech as an audio file
        filepath = "voice.mp3"
        with open(filepath, 'wb') as f:
            f.write(speech)

        await cai_client.close_session()
        return filepath

    except Exception as e:
        print(f"{grey}{current_time}{red} ERROR{reset} <-> Error generating TTS: {e}")
        return None

async def generate_tts(chat_id: str, turn_id: str, candidate_id: str):
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    try:
        cai_client = await get_client(token=AI_TOKEN)
        
        # Generate speech from the character's reply using the selected voice
        speech = await cai_client.utils.generate_speech(
            chat_id, turn_id, candidate_id, selected_voice_id
        )

        # Save the TTS speech as an audio file
        filepath = "voice.mp3"
        with open(filepath, 'wb') as f:
            f.write(speech)

        await cai_client.close_session()
        return filepath

    except Exception as e:
        print(f"{grey}{current_time}{red} ERROR{reset} <-> Error generating TTS: {e}")
        return None

# Function to generate an image from a prompt
async def generate_image_from_prompt(prompt):
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    try:
        cai_client = await get_client(token=AI_TOKEN)

        # Generate image from the prompt
        images = await cai_client.utils.generate_image(prompt)

        if images:
            image_url = images[0]  # Take the first image URL
            print(f"{grey}{current_time}{blu} INFO {reset} <-> Generated image URL: {image_url}")
            return image_url
        else:
            print(f"{grey}{current_time}{red} ERROR{reset} <-> No images generated.")
            return None

    except Exception as e:
        print(f"Error generating image: {e}")
        return None

# Function to check if the bot should send an unexpected reply
def should_send_unexpected_reply(probability):
    return random.random() < probability / 100

# Ping command and !chat command
@bot.event
async def on_message(message):
    client = await get_client(token=token)
    if message.author == bot.user:
        return
        
    if unexpected_replying > 0 and random.randint(1, 100) <= unexpected_replying:
        #reply, chat_id, turn_id, candidate_id = await chat_with_character(AI_TOKEN, CHARACTER_ID, user_message, HISTORY_THREAD_ID)
        reply, chat_id, turn_id, candidate_id = await client.chat.send_message(character_id, chat.chat_id, user_message, history_thread_id)
        if reply:
            # Create a TTS button after the reply
            tts_button = TTSButton(chat_id, turn_id, candidate_id)
            view = View(timeout=None)  # Disable timeout so the button stays active
            view.add_item(tts_button)
            await message.channel.send(reply, view=view)
        else:
            await message.channel.send("``- could not get response -``")
    
    if message.reference and message.reference.resolved.author == bot.user:
        user_message = message.content
        #reply, chat_id, turn_id, candidate_id = await chat_with_character(AI_TOKEN, CHARACTER_ID, user_message, HISTORY_THREAD_ID)
        reply, chat_id, turn_id, candidate_id = await client.chat.send_message(character_id, chat.chat_id, user_message, history_thread_id)
        if reply:
            # Create a TTS button after the reply
            tts_button = TTSButton(chat_id, turn_id, candidate_id)
            view = View(timeout=None)  # Disable timeout so the button stays active
            view.add_item(tts_button)
            await message.channel.send(reply, view=view)
        else:
            await message.channel.send("``- could not get response -``")
            
    elif bot.user.mentioned_in(message):
        user_message = message.content
        #reply, chat_id, turn_id, candidate_id = await chat_with_character(AI_TOKEN, CHARACTER_ID, user_message, HISTORY_THREAD_ID)
        reply, chat_id, turn_id, candidate_id = await client.chat.send_message(character_id, chat.chat_id, user_message, history_thread_id)
        if reply:
            # Create a TTS button after the reply
            tts_button = TTSButton(chat_id, turn_id, candidate_id)
            view = View(timeout=None)  # Disable timeout so the button stays active
            view.add_item(tts_button)
            await message.channel.send(reply, view=view)
        else:
            await message.channel.send("``- could not get response -``")
            
    if message.content.startswith("!chat"):
        user_message = message.content[len("!chat "):]
        if user_message:
            #reply, chat_id, turn_id, candidate_id = await chat_with_character(AI_TOKEN, CHARACTER_ID, user_message, HISTORY_THREAD_ID)
            reply, chat_id, turn_id, candidate_id = await client.chat.send_message(character_id, chat.chat_id, user_message, history_thread_id)

            if reply:
                # Create a TTS button after the reply
                tts_button = TTSButton(chat_id, turn_id, candidate_id)
                view = View(timeout=None)  # Disable timeout so the button stays active
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

if args.clear:
    clear_screen()
# Run the bot
display_help()
bot.run(TOKEN)
