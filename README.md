# CAIxDiscord
# Discord Character AI Bot

This is a Discord bot that interacts with Character AI and uses TTS (Text-to-Speech) functionality to generate speech for messages. The bot uses the `PyCharacterAI` library to interact with the Character.AI API.

## Features

- Chat with a character on Character.AI.
- Generate TTS audio from Character.AI responses.
- Interact with the bot via Discord commands.

## Requirements

- Python 3.12 or above
- Install the required dependencies:

## Installation

Navigate to the directory location where you want to keep caixdiscord either through cmd.exe (Windows) or in your linux terminal.
Next, enter in these commands:
```bash
git clone https://github.com/hx4u/caixdiscord.git
```
```bash
cd caixdiscord
```
```bash
pip install -r requirements.txt
```
You'll then need to EDIT your config.json file (any text editor will work) and fill in the correct information.
You must create a discord application in the discord developer portal. Add the intents you want (send messages, read messages, add reactions, send TTS, etc).

### Instructions Overview:
```
- **BOTS_DISCORD_TOKEN**: Get from the Discord Developer Portal. (It's in the BOT section).
- **HTTP_AUTHORIZATION**: Extract from your browser when logged into Character.AI. Look for "HTTP_AUTHORIZATION".
- **CHARACTER_INURL_ID**: Find it in the URL of the character's page on Character.AI.
- **HISTORIES_INURL_ID**: Extract from the network tab of the browser’s developer tools while chatting with the character. Enter the history thread and collect it fro the url bar (?hist=HISTORIES_INURL_ID).
- **AIS_NAME_FOR_VOICE**: Fill this in with the name of the AI you are using. This is for searching for voice packs for the TTS feature.
```
### Executing the Program:
```
python caixdiscord.py
```
- To show the help page:
```
python caixdiscord.py --options
```
- Execute the program with a new voice pack:
```
python caixdiscord.py --name Blade
```

### Commands for in Discord:
- Initiate a command with "!".
- Use "/help" to display general command help.
- Use "/chat" to start a chat with your AI.
- Use "/image" to generate some images.
