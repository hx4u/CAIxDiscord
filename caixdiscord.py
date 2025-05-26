def display_help():
    help_text = (
        "    .aMMMb  .aMMMb  dMP                    _____                                              \n"
        "   dMP VMP dMP dMP amr  ooooooo  ooooo  __|__   |__  __  ______  ______  _____  _____   _     \n"   
        "  dMP     dMMMMMP dMP    `8888    d8'  |     |     ||__||   ___||   ___||  _  ||   __| | |    \n"   
        " dMP.aMP dMP dMP dMP       Y888..8P    |      |    ||  | `-.`-. |   |__ | |_| ||  | __ | |    \n"  
        " VMMMP* dMP dMP dMP         `8888'     |______|  __||__||______||______||_____||__||_____|    \n"
        "                           .8PY888.       |_____|                                             \n"
        "   Character X            d8'  `888b                                                          \n"
        "           Ai Discord   o888o  o88888o    A Character AI to Discord api with TTS integration. \n"
        "                                                                                              \n"
        "                                          Credits: LiteKira (kil_l_y) @hx4u - Version 1.0     \n"
        )
    print(help_text)
import discord
import json
import asyncio
import argparse
from discord.ui import Button, View
from utils.cai import CAIWrapper
from utils.voice import select_voice
from utils.tts import generate_tts
import random
with open("config.json") as f:
    config = json.load(f)
parser = argparse.ArgumentParser()
parser.add_argument("--clear", action="store_true")
parser.add_argument("--name", type=str, help="Override voice name from config")
parser.add_argument("--unexpected-reply", type=int, choices=range(0, 101))
args = parser.parse_args()
if args.clear:
    import os
    os.system("cls" if os.name == "nt" else "clear")
TOKEN = config["BOTS_DISCORD_TOKEN"]
VOICE_NAME = args.name if args.name else config["AIS_NAME_FOR_VOICE"]
REPLY_CHANCE = args.unexpected_reply if args.unexpected_reply else 0
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(bot)
cai = None  # Will initialize later
@bot.event
async def on_ready():
    global cai
    print(f"Logged in as {bot.user}")
    cai = await CAIWrapper.create(config["HTTP_AUTHORIZATION"], config["CHARACTER_INURL_ID"], config["HISTORIES_INURL_ID"])
    await select_voice(cai, VOICE_NAME)
    await tree.sync()
@tree.command(name="help", description="Show commands")
async def help_command(interaction: discord.Interaction):
    await interaction.response.send_message("Commands: /chat [message], /image [prompt]")
@tree.command(name="chat", description="Chat with AI")
async def chat_command(interaction: discord.Interaction, message: str):
    await interaction.response.defer()
    answer = await cai.send_message(message)
    await send_message_with_tts(interaction.channel, answer)
@tree.command(name="image", description="Generate an image")
async def image_command(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer()
    urls = await cai.generate_image(prompt)
    await interaction.followup.send(content="\n".join(urls) if urls else "No image generated.")
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if bot.user.mentioned_in(message) or message.reference and message.reference.resolved.author == bot.user:
        answer = await cai.send_message(message.content)
        await send_message_with_tts(message.channel, answer)
    elif REPLY_CHANCE > 0 and random.randint(1, 100) <= REPLY_CHANCE:
        answer = await cai.send_message(message.content)
        await send_message_with_tts(message.channel, answer)
async def send_message_with_tts(channel, answer):
    reply_text = answer.get_primary_candidate().text
    button = Button(label="🔊", style=discord.ButtonStyle.gray)
    view = View()
    view.answer = answer
    view.reply_text = reply_text  # Optional, for display
    async def button_callback(interaction):
        button.disabled = True
        await interaction.response.edit_message(view=view)
        voice_data = await generate_tts(cai, view.answer)
        await interaction.followup.send(file=discord.File(voice_data, filename="TTS.mp3"))
    button.callback = button_callback
    view.add_item(button)
    await channel.send(content=reply_text, view=view)
display_help()
bot.run(TOKEN)
