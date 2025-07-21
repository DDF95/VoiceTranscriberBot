import config
from telegram import Update
from telegram.ext import (ApplicationBuilder, CommandHandler, ContextTypes,
                          MessageHandler, filters)
from transcribe import on_voice_message
from utilities import delete_msg, restart_bot


application = ApplicationBuilder().token(config.BOT_TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Ciao! Inviami un messaggio vocale o un videomessaggio e lo trascriverò per te!"
        "\nRispondi ad una trascrizione con /cancella per eliminarla."
        "\n\nCreato da @diddieffe"
        "\nCodice sorgente: https://github.com/DDF95/VoiceTranscriberBot"
    )


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Invia un messaggio vocale o un videomessaggio e lo trascriverò per te!"
        "\nRispondi ad una trascrizione con /cancella per eliminarla."
        "\n\nCreato da @diddieffe"
        "\nCodice sorgente: https://github.com/DDF95/VoiceTranscriberBot"
    )


if __name__ == '__main__':
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler, 0)

    on_voice_message_handler = MessageHandler(filters.VOICE | filters.VIDEO_NOTE, on_voice_message)
    application.add_handler(on_voice_message_handler, 1)

    help_handler = CommandHandler('help', help)
    application.add_handler(help_handler, 2)

    delete_handler = CommandHandler(('delete', 'del', 'cancella', 'elimina'), delete_msg)
    application.add_handler(delete_handler, 3)

    restart_bot_handler = CommandHandler("restart", restart_bot)
    application.add_handler(restart_bot_handler, 4)

    application.run_polling(drop_pending_updates=True)
