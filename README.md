# Voice Transcription Telegram Bot

Telegram bot that automatically transcribes voice messages and video messages into text using **offline speech recognition** with Vosk.

## Features

- Transcribes voice messages and video notes (.ogg, .mp4 with audio) using offline processing
- Supports Italian language transcription
- Sends back transcriptions as formatted Telegram messages with expandable blockquotes
- Users can delete transcriptions by replying with a delete command

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/voice-transcriber-bot.git
cd voice-transcriber-bot
```

### 2. Install Dependencies

Make sure you have Python 3.10+ installed. Then:

```bash
pip3 install -r requirements.txt
```

Dependencies include:
- python-telegram-bot
- vosk
- pydub

Note: `ffmpeg` is required for audio conversion. Install it via your package manager (e.g. `brew install ffmpeg` on macOS).

### 3. Download Vosk Language Model

Download the Italian language model (or your preferred language):
```bash
wget https://alphacephei.com/vosk/models/vosk-model-it-0.22.zip
unzip vosk-model-it-0.22.zip
```

Note: The model should be placed in your **project directory**. For other languages, see [Vosk Models](https://alphacephei.com/vosk/models).

### 4. Create Configuration File

Create a file called `config.ini` in the root folder:

```ini
[bot]
bot_token = YOUR_TELEGRAM_BOT_TOKEN

[bot_admins]
admin1 = 123456789
```

Replace `YOUR_TELEGRAM_BOT_TOKEN` with your actual bot token and `123456789` with your Telegram user ID.

### 5. Run the Bot

```bash
python3 main.py
```

> The bot will load the Vosk model on startup. This may take a few seconds.

---

## How It Works

1. User sends a voice message or video note.
2. Vosk performs offline speech recognition.
3. The transcription is sent back as a reply.
4. Users can delete the transcription with one of the supported delete commands.

---

## Project Structure

```
├── main.py               # Entry point of the bot
├── config.py             # Loads config from config.ini
├── transcribe.py         # Handles audio conversion and transcription
├── utilities.py          # Contains restart and delete message utilities
├── vosk-model-it-0.22/   # Vosk language model (downloaded separately)
├── config.ini            # Bot configuration
├── requirements.txt      # Required Python packages
```

---

## Commands

| Bot Commands                           | Description                                      |
|--------------------------------------|--------------------------------------------------|
| `/start`                             | Start the bot and display a welcome message      |
| `/help`                              | Show help instructions                           |
| `/cancella`, `/elimina`, `/delete`, `/del` | Delete the transcription (use in reply)         |
| `/restart`                           | Restart the bot (admin only)                     |
