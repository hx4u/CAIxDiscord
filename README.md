# CAIxDiscord
# Discord Character AI Bot

This is a Discord bot that interacts with Character.AI and uses TTS (Text-to-Speech) functionality to generate speech for messages. The bot uses the `PyCharacterAI` library to interact with the Character.AI API.

## Features

- Chat with a character on Character.AI.
- Generate TTS audio from Character.AI responses.
- Interact with the bot via Discord commands.

## Requirements

- Python 3.12 or above
- Install the required dependencies:

  ```bash
  pip install discord.py
  pip install PyCharacterAI

### Instructions Overview:
- **BOTS_DISCORD_TOKEN**: Get from the Discord Developer Portal.
- **HTTP_AUTHORIZATION**: Extract from your browser when logged into Character.AI. Look for "HTTP_AUTHORIZATION".
- **CHARACTER_INURL_ID**: Find it in the URL of the character's page on Character.AI.
- **HISTORIES_INURL_ID**: Extract from the network tab of the browser’s developer tools while chatting with the character. Enter the history thread and collect it fro the url bar (?hist=STATIC_CHAT_ID).
- **AIS_NAME_FOR_VOICE**: Fill this in with the name of the AI you are using. This is for searching for voice packs for the TTS feature.
  
### Executing the Program:
```
python3 caixdiscord.py
```
- To show the help page:
```
python3 caixdiscord.py --options
```
- Execute the program with a new voice pack:
```
python3 caixdiscord.py --name Blade
```
- Executes the program quickly (defaults to voice pack 0):
```
python3 caixdiscord.py --timeout 1
```
### Commands for in Discord:
- Initiate a command with "!".
- Use "/help" to display general command help.
- Use "/chat" to start a chat with your AI.
- Use "/image" to generate some images.
