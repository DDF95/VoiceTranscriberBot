import os
import uuid
import wave
import json
import asyncio
import threading

from pydub import AudioSegment
from telegram import Update
from telegram.ext import ContextTypes
import vosk

import config

# Initialize Vosk model in a thread-safe way
MODEL_PATH = os.path.join(config.main_directory, "vosk-model-it-0.22")
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Vosk model not found at {MODEL_PATH}")

# Use a lock to ensure thread-safe model access
model_lock = threading.Lock()
MODEL = vosk.Model(MODEL_PATH)

def split_text(text, max_length=4096):
    """Split text into chunks while preserving HTML tags."""
    chunks = []
    while text:
        if len(text) <= max_length:
            chunks.append(text)
            break
        
        # Find safe split point (space within limit)
        split_index = text.rfind(' ', 0, max_length)
        if split_index == -1:
            split_index = max_length
        
        # Check if we're splitting inside an HTML tag
        if split_index > 10 and (text[split_index-1] == '<' or text[split_index] == '>'):
            # Find nearest safe space if splitting in tag
            safe_index = text.rfind(' ', 0, split_index - 10)
            split_index = safe_index if safe_index != -1 else max_length
        
        chunks.append(text[:split_index])
        text = text[split_index:].lstrip()
    return chunks


async def transcribe_audio(path):
    """Transcribe audio file to text using Vosk offline speech recognition."""
    # Generate unique filename to prevent conflicts
    temp_wav = f"{config.main_directory}/temp_{uuid.uuid4().hex}.wav"
    
    try:
        # Convert to WAV format (16kHz mono PCM required by Vosk)
        audio = AudioSegment.from_file(path)
        
        # Optimize audio for Vosk
        audio = audio.set_frame_rate(16000).set_channels(1)
        
        # Reduce file size if possible
        if len(audio) > 60000:  # Longer than 60 seconds
            # Use lower bitrate for longer files
            audio.export(temp_wav, format='wav', bitrate="16k", parameters=["-ac", "1"])
        else:
            audio.export(temp_wav, format='wav', codec='pcm_s16le')
        
        # Transcribe using Vosk in a separate thread to prevent blocking
        def vosk_transcribe():
            with model_lock:  # Ensure thread-safe access to the model
                recognizer = vosk.KaldiRecognizer(MODEL, 16000)
                recognizer.SetWords(False)  # We don't need word-level timestamps
                
                transcription_parts = []
                with wave.open(temp_wav, 'rb') as wf:
                    while True:
                        data = wf.readframes(8000)  # Larger chunks for efficiency
                        if len(data) == 0:
                            break
                        if recognizer.AcceptWaveform(data):
                            result = json.loads(recognizer.Result())
                            if 'text' in result:
                                transcription_parts.append(result['text'])
                    
                    # Get final result
                    final_result = json.loads(recognizer.FinalResult())
                    if 'text' in final_result:
                        transcription_parts.append(final_result['text'])
                
                return ' '.join(transcription_parts).strip()
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, vosk_transcribe)

    except Exception as e:
        print(f"Vosk transcription error: {e}")
        return None
    finally:
        # Clean up temporary file
        if os.path.exists(temp_wav):
            try:
                os.remove(temp_wav)
            except:
                pass


async def send_processing_message(context, chat_id, message_id):
    """Send initial processing message with italic formatting."""
    return await context.bot.send_message(
        chat_id=chat_id,
        text="<i>Trascrizione in corso, attendi qualche istante...</i>",
        reply_to_message_id=message_id,
        parse_mode="HTML"
    )


def wrap_in_blockquote(text):
    """Wrap text in an expandable blockquote."""
    return f"<blockquote expandable>{text}</blockquote>"


async def handle_transcription_result(context, chat_id, message_id, status_msg, transcription):
    """Handle the transcription result including splitting and formatting."""
    if not transcription:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_msg.message_id,
            text="Non sono riuscitə a trascrivere il messaggio."
        )
        return

    # Create formatted header and footer
    header = "<b>Trascrizione:</b>\n"
    footer = "\n\n<i>Rispondi a questo messaggio con <tg-spoiler>/cancella</tg-spoiler> per eliminare la trascrizione</i>"

    # Wrap transcription in blockquote
    quoted_transcription = wrap_in_blockquote(transcription)
    full_content = header + quoted_transcription
    
    # Check if we can fit header + blockquoted transcription + footer in one message
    if len(full_content + footer) <= 4096:
        final_text = full_content + footer
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_msg.message_id,
            text=final_text,
            parse_mode="HTML"
        )
    else:
        # Send header with blockquote start
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_msg.message_id,
            text=header + "<blockquote expandable>",
            parse_mode="HTML"
        )
        
        # Split and send transcription content
        chunks = split_text(transcription, 4070)  # Reserve space for closing tags
        for i, chunk in enumerate(chunks):
            # Add closing tag only for the last chunk
            content = chunk
            if i == len(chunks) - 1:
                content += "</blockquote>"
            
            await context.bot.send_message(
                chat_id=chat_id,
                text=content,
                reply_to_message_id=message_id,
                parse_mode="HTML"
            )
        
        # Send footer
        await context.bot.send_message(
            chat_id=chat_id,
            text=footer,
            reply_to_message_id=message_id,
            parse_mode="HTML"
        )


async def on_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    message_id = update.message.message_id
    status_msg = None
    audio_path = None
    
    try:
        # Send initial processing message
        status_msg = await send_processing_message(context, chat_id, message_id)
        
        # Get media file
        media = update.message.voice or update.message.video_note
        if not media:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=status_msg.message_id,
                text="Formato non supportato."
            )
            return
            
        file = await media.get_file()
        audio_path = await file.download_to_drive()
        
        # Transcribe audio
        transcription = await transcribe_audio(audio_path)
            
        # Handle and send transcription
        await handle_transcription_result(context, chat_id, message_id, status_msg, transcription)

    except Exception as e:
        print(f"Error in on_voice_message: {e}")
        if status_msg:
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=status_msg.message_id,
                    text="Errore durante la trascrizione."
                )
            except:
                pass
    finally:
        # Clean up the audio file
        if audio_path and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except:
                pass
