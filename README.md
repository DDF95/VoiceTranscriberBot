# Voice Transcription Telegram Bot

Telegram bot that automatically transcribes voice messages and video messages into text using Google Speech Recognition.

## Features

- Transcribes voice messages and video notes (.ogg, .mp4 with audio).
- Sends back transcriptions as formatted Telegram messages.
- Users can delete transcriptions by replying with a delete command.

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
- SpeechRecognition
- pydub

Note: `ffmpeg` is required for audio conversion. Install it via your package manager (e.g. `brew install ffmpeg` on macOS).

---

### 3. Create Configuration File

Create a file called `config.ini` in the root folder:

```ini
[bot]
bot_token = YOUR_TELEGRAM_BOT_TOKEN

[bot_admins]
admin1 = 123456789
```

Replace `YOUR_TELEGRAM_BOT_TOKEN` with your actual bot token and `123456789` with your Telegram user ID.

---

### 4. Run the Bot

```bash
python3 main.py
```

> You may want to change the transcription language in `transcribe.py` (currently set to Italian, `it-IT`).

---

## How It Works

1. User sends a voice message or video note.
2. The bot downloads and converts the audio to .wav.
3. It uses Google Speech Recognition to transcribe the audio.
4. The transcription is sent back as a reply.
5. Users can delete the transcription with one of the supported delete commands.

---

## Project Structure

```
├── main.py               # Entry point of the bot
├── config.py             # Loads config from config.ini
├── transcribe.py         # Handles audio conversion and transcription
├── utilities.py          # Contains restart and delete message utilities
├── config.ini            # (You create this)
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
