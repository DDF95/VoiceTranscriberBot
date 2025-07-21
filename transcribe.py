import os
import uuid

import speech_recognition
from pydub import AudioSegment
from telegram import Update
from telegram.ext import ContextTypes

import config


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
        if text[split_index-1] == '<' or text[split_index] == '>':
            # Find nearest safe space if splitting in tag
            safe_index = text.rfind(' ', 0, split_index - 10)
            split_index = safe_index if safe_index != -1 else max_length
        
        chunks.append(text[:split_index])
        text = text[split_index:].lstrip()
    return chunks


def transcribe_audio(path):
    """Transcribe audio file to text using Google Speech Recognition."""
    # Generate unique filename to prevent conflicts
    temp_wav = f"{config.main_directory}/temp_{uuid.uuid4().hex}.wav"
    
    try:
        # Convert to WAV format
        AudioSegment.from_file(path).export(temp_wav, format='wav')

        # Recognize speech
        r = speech_recognition.Recognizer()
        with speech_recognition.AudioFile(temp_wav) as source:
            audio = r.record(source)
        
        return r.recognize_google(audio, language="it-IT")
    except speech_recognition.UnknownValueError:
        return None
    except speech_recognition.RequestError as e:
        print(f"Google Speech Recognition error: {e}")
        return None
    finally:
        # Clean up temporary file
        if os.path.exists(temp_wav):
            os.remove(temp_wav)


async def send_processing_message(context, chat_id, message_id):
    """Send initial processing message with italic formatting."""
    return await context.bot.send_message(
        chat_id=chat_id,
        text="<i>Trascrizione in corso, attendi qualche secondo...</i>",
        reply_to_message_id=message_id,
        parse_mode="HTML"
    )


def wrap_in_blockquote(text):
    """Wrap text in an expandable blockquote."""
    return f"<blockquote expandable>{text}</blockquote>"


async def handle_transcription_result(context, chat_id, message_id, status_msg, transcription):
    """Handle the transcription result including splitting and formatting."""
    # Create formatted header and footer
    header = "<b>Trascrizione:</b>\n"
    footer = "\n<i>Rispondi a questo messaggio con /cancella per eliminare la trascrizione</i>"
    
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
            content = chunk + "</blockquote>" if i == len(chunks) - 1 else chunk
            
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
        transcription = transcribe_audio(audio_path)
        os.remove(audio_path)
        
        if not transcription:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=status_msg.message_id,
                text="Non sono riuscitə a trascrivere il messaggio."
            )
            return
            
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