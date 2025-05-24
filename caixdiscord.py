import asyncio
import json
import discord
import random
import argparse
from discord.ext import commands
from discord.ui import Button, View
from PyCharacterAI import get_client

# Load configuration from config.json
def load_config():
    with open('config.json', 'r') as f:
        config = json.load(f)
    return config

# Function to get the AI's response
async def chat_with_character(token, character_id, user_message, history_thread_id):
    client = await get_client(token=token)

    try:
        # Fetch account information
        me = await client.account.fetch_me()
        print(f"Logged in as @{me.username}")

        # Use the provided history thread ID if it's available
        if history_thread_id:
            chat, greeting = await client.chat.create_chat(character_id, history_thread_id=history_thread_id)
            print(f"{greeting.author_name}: {greeting.get_primary_candidate().text}")
        else:
            # No history thread ID, create a new thread
            chat, greeting = await client.chat.create_chat(character_id)
            print(f"New chat created with {greeting.author_name}: {greeting.get_primary_candidate().text}")

        # Send the user message
        response = await client.chat.send_message(character_id, chat.chat_id, user_message)
        reply = response.get_primary_candidate().text
        print(f"{response.author_name}: {reply}")

        return reply, chat.chat_id, response.turn_id, response.get_primary_candidate().candidate_id

    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None, None, None
    finally:
        # Ensure the session is properly closed
        await client.close_session()

# Function to find and select the voice ID
async def find_voice_id(cai_client, voicename):
    try:
        voices = await cai_client.utils.search_voices(voicename)

        if not voices:
            print("No voices found.")
            return None

        # Select the first voice by default
        selected_voice_id = voices[0].voice_id
        print(f"Selected voice ID: {selected_voice_id}")
        return selected_voice_id

    except Exception as e:
        print(f"Error: {e}")
        return None

# Function to search voice packs
async def search_voice_packs(cai_client, voicename):
    try:
        voices = await cai_client.utils.search_voices(voicename)

        if voices:
            print(f"Found {len(voices)} voice packs for {voicename}.")
            for idx, voice in enumerate(voices[:99]):  # Display up to 99 voice packs
                # Format numbers 0-9 with leading zeros
                print(f"#{str(idx + 1).zfill(2)}: {voice.voice_id}, {voice.name}")

            # Prompt user to select a voice pack
            selection = input(f"Please select a voice pack (1-{len(voices)}): ").strip()

            if selection.isdigit():
                selection_index = int(selection) - 1
                if 0 <= selection_index < len(voices):
                    selected_voice_id = voices[selection_index].voice_id
                    print(f"Selected voice pack: {voices[selection_index].name} ({selected_voice_id})")
                    return selected_voice_id
                else:
                    print(f"Invalid selection. Using default voice pack.")
                    return voices[0].voice_id
            else:
                print(f"Invalid input. Using default voice pack.")
                return voices[0].voice_id
        else:
            print("No voice packs found.")
            return None
    except Exception as e:
        print(f"Error searching for voice packs: {e}")
        return None

# Discord Bot Setup
config = load_config()

# Extract values from the config
TOKEN = config.get("BOTS_DISCORD_TOKEN")
AI_TOKEN = config.get("HTTP_AUTHORIZATION")
CHARACTER_ID = config.get("CHARACTER_INURL_ID")
HISTORY_THREAD_ID = config.get("HISTORIES_INURL_ID")  # Load history thread ID from config
VOICENAME = config.get("AIS_NAME_FOR_VOICE")

# Command-line argument parsing
parser = argparse.ArgumentParser(description="Discord Bot with Unexpected Reply Feature.")
parser.add_argument("--unexpected-reply", type=int, default=0, help="Chance of unexpected reply (0 to 100).")
parser.add_argument("--name", type=str, help="Override the voice name from the config.")
args = parser.parse_args()

# Use --name flag if provided, otherwise use the name from config.json
voice_name = args.name if args.name else VOICENAME

# Create bot instance
intents = discord.Intents.default()
intents.message_content = True  # Make sure to enable this intent for reading message content
bot = commands.Bot(command_prefix="!", intents=intents)

# Select voice on bot startup
selected_voice_id = None
async def setup_voice():
    global selected_voice_id
    cai_client = await get_client(token=AI_TOKEN)
    
    # Ask user if they want to search for voice packs
    user_input = input("Would you like to search for voice packs? (Y/n): ").strip().lower()

    if user_input == "y":
        selected_voice_id = await search_voice_packs(cai_client, voice_name)

    if not selected_voice_id:
        selected_voice_id = await find_voice_id(cai_client, voice_name)
    await cai_client.close_session()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} ({bot.user.id})")
    await setup_voice()

# TTS Button
class TTSButton(Button):
    def __init__(self, chat_id: str, turn_id: str, candidate_id: str):
        super().__init__(label="🔊 Generate TTS", style=discord.ButtonStyle.green)
        self.chat_id = chat_id
        self.turn_id = turn_id
        self.candidate_id = candidate_id
        self.disabled = False  # Button is initially enabled

    async def callback(self, interaction: discord.Interaction):
        # Generate TTS audio
        tts_audio = await generate_tts(self.chat_id, self.turn_id, self.candidate_id)
        
        # If TTS audio is generated, send it and disable the button
        if tts_audio:
            await interaction.response.send_message("Here is the TTS audio:", file=discord.File(tts_audio, filename="response.mp3"))

            # Disable the button after TTS has been generated and sent
            self.disabled = True
            # Update the view to reflect the disabled state of the button
            view = View(timeout=None)  # Disable timeout so the button remains disabled
            view.add_item(self)  # Re-add the button to the view
            await interaction.message.edit(view=view)
        else:
            await interaction.response.send_message("Sorry, something went wrong with TTS generation.")

async def generate_tts(chat_id: str, turn_id: str, candidate_id: str):
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
        print(f"Error generating TTS: {e}")
        return None

async def generate_tts(chat_id: str, turn_id: str, candidate_id: str):
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
        print(f"Error generating TTS: {e}")
        return None

# Function to generate an image from a prompt
async def generate_image_from_prompt(prompt):
    try:
        cai_client = await get_client(token=AI_TOKEN)

        # Generate image from the prompt
        images = await cai_client.utils.generate_image(prompt)

        if images:
            image_url = images[0]  # Take the first image URL
            print(f"Generated image URL: {image_url}")
            return image_url
        else:
            print("No images generated.")
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
    if message.author == bot.user:
        return

    # Random unexpected reply
    if should_send_unexpected_reply(args.unexpected_reply):
        unexpected_reply = "I'm just here to say something unexpected!"
        await message.channel.send(unexpected_reply)

    if message.content.startswith("!chat"):
        user_message = message.content[len("!chat "):]
        if user_message:
            reply, chat_id, turn_id, candidate_id = await chat_with_character(AI_TOKEN, CHARACTER_ID, user_message, HISTORY_THREAD_ID)
            if reply:
                # Create a TTS button after the reply
                tts_button = TTSButton(chat_id, turn_id, candidate_id)
                view = View(timeout=None)  # Disable timeout so the button stays active
                view.add_item(tts_button)
                await message.channel.send(reply, view=view)
            else:
                await message.channel.send("Sorry, I couldn't get a response.")
        else:
            await message.channel.send("Please provide a message after `!chat`.")
    
    elif message.content.startswith("!image"):
        prompt = message.content[len("!image "):]
        if prompt:
            image_url = await generate_image_from_prompt(prompt)
            if image_url:
                await message.channel.send(f"Here is your image: {image_url}")
            else:
                await message.channel.send("Sorry, I couldn't generate an image.")
        else:
            await message.channel.send("Please provide a prompt after `!image`.")

# Run the bot
bot.run(TOKEN)
