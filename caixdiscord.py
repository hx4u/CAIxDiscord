import os
import io
import sys
import time
import json
import signal
import asyncio
import discord
import platform
import argparse
from discord.ext import commands
from discord.ui import Button, View
from PyCharacterAI import get_client
from PyCharacterAI.exceptions import SessionClosedError

  
def clear_screen():
    # Pause to allow user to see previous output
    time.sleep(0.5)
    # Check OS and clear screen accordingly
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')


clear_screen()  
  
  
  
  

# Load configuration from config.json
def load_config():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"Error occurred: {e}")
        return None

# Display the help message
def display_help():
    help_text = (
        "Usage: python bot.py [options]\n\n"
        "Options:\n"
        "  --options          Show this help message and exit.\n"
        "  --name             Set the character's name.\n"
        "  --timeout          Set the timeout for selecting a voice (default 5 seconds).\n"
    )
    print(help_text)

# Parse command-line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Discord bot with TTS integration.")
    parser.add_argument('--options', action='store_true', help="Show this help message and exit.")
    parser.add_argument('--name', type=str, help="Set the character's name.")
    parser.add_argument('--timeout', type=int, default=5, help="Set the timeout for selecting a voice (default 5 seconds).")
    return parser.parse_args()

# Main entry point
if __name__ == "__main__":
    # Parse the arguments
    args = parse_args()

    # If --help is called, display help and exit
    if args.options:
        display_help()
        sys.exit(0)  # Exit after displaying help

    # Load the config (or use arguments if provided)
    config = load_config() # if config is None else config

    DISCORD_TOKEN = config["DISCORD_TOKEN"]
    CHARACTER_TOKEN = config["CHARACTER_TOKEN"]
    CHARACTER_ID = config["CHARACTER_ID"]
    STATIC_CHAT_ID = config["STATIC_CHAT_ID"]
    CHARACTER_NAME = args.name or config["CHARACTER_NAME"]
    timeout = args.timeout

    # Bot and other code continues below...
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    client = None
    chat = None
    me = None
    selected_voice_id = None  # Global variable for the selected voice ID
  
  
  

  
  
    
    
red = '\033[91m'  # Red color for the message
grey = '\033[90m'  # Grey color for the time
blue = '\033[34m'  # Blue color for the message
purple = '\033[38;5;129m'  # Purple color for the message
reset = '\033[0m'  # Reset color to default
light_blue = '\033[94m'  # Light blue color for the time
light_green = '\033[92m'  # Light green color for the message
light_pink = '\033[95m'  # Light pink (magenta) color for the message
dark_red = '\033[38;5;52m'  # Dark red color for the message
bright_red = '\033[91m'  # Bright red color for the message

timeout = 9

class TimeoutException(Exception):
    pass
  
# Function to handle the timeout signal
def timeout_handler(signum, frame):
    raise TimeoutException("Time is up!")
    
# Set the timeout handler
signal.signal(signal.SIGALRM, timeout_handler)


def get_input_with_timeout(prompt, timeout):
    # Set the alarm for timeout
    signal.alarm(timeout)
    
    try:
        user_input = input(prompt)
        signal.alarm(0)  # Cancel the alarm if input is received
        return user_input
    except TimeoutException:
        return None  # Timeout occurred


async def find_voice_id(CHARACTER_NAME, token):
    global selected_voice_id  # Use the global variable to store the selected voice ID

    client = await get_client(token=token)

    try:
        # Search for voices for the character
        voices = await client.utils.search_voices(CHARACTER_NAME)

        if not voices:
            current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            print(f"{grey}{current_time}{light_blue} INFO{reset}     No voices found for character: {CHARACTER_NAME}")
            return None

        # If the token is 0, select the first available voice
        if token == "0":
            selected_voice_id = voices[0].voice_id
            current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            print(f"{grey}{current_time}{blue} EXEC{reset} <-> Selected voice ID: {selected_voice_id} for character: {CHARACTER_NAME}")
            return selected_voice_id

        # Print out the voices and their IDs
        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        print(f"{grey}{current_time}{light_blue} INFO{reset}     Found voices for {CHARACTER_NAME}:")
                
                
               
                
        user_input = get_input_with_timeout(f"{grey}{current_time}{light_green} USER{reset} >-- Select a voice ID from list? (Defaults to first voice found)." + " (Y/n): ", timeout)
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
                
                
                user_input = input(f"{grey}{current_time}{light_green} USER{reset} <-> Select a voice (#): ").lower()
                
                
                
                if user_input.isdigit():
                    voice_select = int(user_input)
                    selected_voice_id = voices[voice_select].voice_id
                    return selected_voice_id
                else:
                    print(f"{grey}{current_time}{light_blue} INFO{reset}     Must be a number... Using voice 0.")
                    selected_voice_id = voices[0].voice_id
                    return selected_voice_id
        if user_input == 'n':
# Select the first voice by default if no specific one is selected
            current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            print(f"{grey}{current_time}{blue} EXEC{reset} --> OK... Using voice 0.")
            selected_voice_id = voices[0].voice_id
            return selected_voice_id
# Return the voice ID of the first voice (or select a specific one)            
            return selected_voice_id
        if user_input == None:
            current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            print(f"\n{grey}{current_time}{red} ERRO{reset} <-> No response... defaulting to voice 0.")
            selected_voice_id = voices[0].voice_id
            return selected_voice_id
        else:
            current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            print(f"{grey}{current_time}{blue} EXEC{reset} --> Incorrect response... defaulting to voice 0.")          
            selected_voice_id = voices[0].voice_id
            return selected_voice_id
    except Exception as e:
        print(f"Error occurred: {e}")
        return None

# Replace with your actual token
token = CHARACTER_TOKEN  # Default token (can be "0" if you want to use the first voice)

# Run the async function to get the selected voice ID
# asyncio.run(find_voice_id(CHARACTER_NAME, token))


class TTSButton(Button):
    def __init__(self, chat_id, turn_id, candidate_id, CHARACTER_NAME, voice_id):
        super().__init__(emoji="🔊", style=discord.ButtonStyle.primary)
        self.chat_id = chat_id
        self.turn_id = turn_id
        self.candidate_id = candidate_id
        self.CHARACTER_NAME = CHARACTER_NAME
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
                content="``voice:``",
                file=discord.File(filepath),
                ephemeral=True  # Optional: You can set ephemeral=False to make it visible to everyone
            )

            # Clean up the audio file after sending
            os.remove(filepath)

        except Exception as e:
            # Handle errors and inform the user
            current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            await interaction.followup.send(f"{grey}{current_time}{red} ERRO{reset} <-> ``error generating voice:`` {e}")


@bot.event
async def on_ready():
    global client, chat, me
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    print(f"{grey}{current_time}{blue} EXEC{reset} --> Logged in as {light_blue} {bot.user}")
    client = await get_client(token=CHARACTER_TOKEN)
    chat = await client.chat.fetch_chat(STATIC_CHAT_ID)
    me = await client.account.fetch_me()
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    print(f"{grey}{current_time}{blue} EXEC{reset} --> Authenticated as {light_green}@{me.username}")
    
    # Call find_voice_id after bot logs in
    voice_id = await find_voice_id(CHARACTER_NAME, CHARACTER_TOKEN)
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    if voice_id:
        print(f"{grey}{current_time}{blue} EXEC{reset} --> Voice ID for {CHARACTER_NAME}: {voice_id}")
    else:
        print(f"{grey}{current_time}{red} ERRO{reset} <-> Could not find voice ID.")


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


@bot.command(name="chat")
async def chat_command(ctx, *, message: str):
    await send_character_message(ctx.message, message)


# Command to generate image from prompt
@bot.command(name="image")
async def image_command(ctx, *, prompt: str):
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    try:
        urls = await client.utils.generate_image(prompt)
        if not urls:
            await ctx.send(f"{grey}{current_time}{red} ERRO{reset} <-> No images generated.")
            return
        # Send all images as embeds
        for url in urls:
            embed = discord.Embed(title=f"{grey}{current_time}{red} INFO{reset} --> Image result for: {prompt}")
            embed.set_image(url=url)
            await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"{grey}{current_time}{red} ERRO{reset} <-> Failed to generate image: {e}")




@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message):
        content = message.clean_content.replace(f"@{bot.user.name}", "").strip()
        if content:
            await send_character_message(message, content)
    await bot.process_commands(message)


async def send_character_message(message, user_message):
    try:
        answer = await client.chat.send_message(CHARACTER_ID, chat.chat_id, user_message)
        reply_text = answer.get_primary_candidate().text

        # Pass the selected voice_id to the TTSButton
        view = View()
        view.add_item(TTSButton(
            chat.chat_id,
            answer.turn_id,
            answer.get_primary_candidate().candidate_id,
            answer.author_name,
            selected_voice_id  # Pass the voice ID here
        ))

        await message.channel.send(content=reply_text, view=view)

    except SessionClosedError:
        await message.channel.send(f"{grey}{current_time}{light_blue} INFO{reset}     Session closed. Try again later.")
    except Exception as e:
        await message.channel.send(f"{grey}{current_time}{red} ERRO{reset} <-> {e}")






bot.run(DISCORD_TOKEN)
