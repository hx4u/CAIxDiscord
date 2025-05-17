# caixdiscord
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
- **DISCORD_TOKEN**: Get from the Discord Developer Portal.
- **CHARACTER_TOKEN**: Extract from your browser when logged into Character.AI. Look for "HTTP_AUTHORIZATION".
- **CHARACTER_ID**: Find it in the URL of the character's page on Character.AI.
- **STATIC_CHAT_ID**: Extract from the network tab of the browser’s developer tools while chatting with the character. Enter the history thread and collect it fro the url bar (?hist=STATIC_CHAT_ID).
