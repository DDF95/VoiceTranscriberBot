import os
import sys

from telegram import Update
from telegram.ext import ContextTypes

import config


def is_bot_admin(user_id):
    if user_id in config.BOT_ADMINS:
        return True
    else:
        return False


async def restart_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_bot_admin(update.effective_user.id):
        return
    
    await update.message.reply_text("Restarting...")
    args = sys.argv[:]
    args.insert(0, sys.executable)
    os.chdir(os.getcwd())
    os.execv(sys.executable, args)


async def delete_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.reply_to_message.message_id)