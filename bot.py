import os
import discord
from discord.ext import commands
from discord.ui import Button, View
import asyncio
from PyCharacterAI import get_client
from PyCharacterAI.exceptions import SessionClosedError

# Configuration
DISCORD_TOKEN = "DISCORD_TOKEN"
CHARACTER_TOKEN = "CHARACTER_TOKEN"
CHARACTER_ID = "CHARACTER_ID"
STATIC_CHAT_ID = "STATIC_CHAT_ID"  # Must be pre-created manually on Character.AI

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

client = None
chat = None
me = None
selected_voice_id = None  # Global variable for the selected voice ID


async def find_voice_id(character_name, token):
    global selected_voice_id  # Use the global variable to store the selected voice ID

    client = await get_client(token=token)

    try:
        # Search for voices for the character
        voices = await client.utils.search_voices(character_name)

        if not voices:
            print(f"No voices found for character: {character_name}")
            return None

        # If the token is 0, select the first available voice
        if token == "0":
            selected_voice_id = voices[0].voice_id
            print(f"Selected voice ID: {selected_voice_id} for character: {character_name}")
            return selected_voice_id

        # Print out the voices and their IDs
        print(f"Found voices for {character_name}:")
                
                
                
                
        user_input = input("Search for and select a voice ID?" + " (Y/n): ").lower() 
        if user_input == 'y':
            count = 0
            for voice in voices:
                print(f"{count}: {voice.name}, Voice ID: {voice.voice_id}")
                count += 1
            user_input = input("Select a voice (#): ").lower()
            if user_input.isdigit():
                voice_select = int(user_input)
                selected_voice_id = voices[voice_select].voice_id
                return selected_voice_id
            else:
                print("Must be a number... Using voice 0.")
                selected_voice_id = voices[0].voice_id
                return selected_voice_id
        if user_input == 'n':
# Select the first voice by default if no specific one is selected
            print("OK... Using voice 0.")
            selected_voice_id = voices[0].voice_id
# Return the voice ID of the first voice (or select a specific one)            
            return selected_voice_id
    except Exception as e:
        print(f"Error occurred: {e}")
        return None

# Replace with your actual token
token = CHARACTER_TOKEN  # Default token (can be "0" if you want to use the first voice)
character_name = "L Lawliet"

# Run the async function to get the selected voice ID
# asyncio.run(find_voice_id(character_name, token))

# Run the async function to get the selected voice ID
# asyncio.run(find_voice_id(character_name, token))


class TTSButton(Button):
    def __init__(self, chat_id, turn_id, candidate_id, character_name, voice_id):
        super().__init__(emoji="🔊", style=discord.ButtonStyle.primary)
        self.chat_id = chat_id
        self.turn_id = turn_id
        self.candidate_id = candidate_id
        self.character_name = character_name
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
            await interaction.followup.send(f"``error generating voice:`` {e}")


@bot.event
async def on_ready():
    global client, chat, me
    print(f"Logged in as {bot.user}")
    client = await get_client(token=CHARACTER_TOKEN)
    chat = await client.chat.fetch_chat(STATIC_CHAT_ID)
    me = await client.account.fetch_me()
    print(f"Authenticated as @{me.username}")
    
    # Call find_voice_id after bot logs in
    voice_id = await find_voice_id(character_name, CHARACTER_TOKEN)
    if voice_id:
        print(f"Voice ID for {character_name}: {voice_id}")
    else:
        print("Could not find voice ID.")


@bot.command(name="commands")
async def help_command(ctx):
    help_text = (
        "**Available Commands:**\n"
        "`!chat [message]` — Chat with the character.\n"
        "`!image [message]` — Generate some images.\n"
        "`@BotName [message]` — Mention the bot to chat.\n"
        "``!commands` — Show this help message.\n"
        "Click 🔊 under any bot message to generate speech."
    )
    await ctx.send(help_text)


@bot.command(name="chat")
async def chat_command(ctx, *, message: str):
    await send_character_message(ctx.message, message)


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
        await message.channel.send("Session closed. Try again later.")
    except Exception as e:
        await message.channel.send(f"Error: {e}")


bot.run(DISCORD_TOKEN)
