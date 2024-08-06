import os
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode

from scraper import LANG_LEVELS_WHITELIST, get_seats_by_language_level
from utils import get_help_messages, print_for_telegram

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')

async def _checkstatus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = await update.effective_chat.send_message(text="_Loading\.\.\._", parse_mode=ParseMode.MARKDOWN_V2)

    levels = LANG_LEVELS_WHITELIST

    if (context.args):
        levels = filter(lambda x: x in LANG_LEVELS_WHITELIST, context.args)

    result = get_seats_by_language_level(levels)
    text = print_for_telegram(result)

    chat_id = update.effective_chat.id
    message_id = msg.id
    await context.bot.edit_message_text(
        text=text,
        message_id=message_id,
        chat_id=chat_id,
        parse_mode=ParseMode.MARKDOWN_V2
    )
    pass

async def _help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_chat.send_message(text=get_help_messages())

async def _commingsoon(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_chat.send_message(text="This feature is coming soon")

if __name__ == '__main__':
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler('help', _help))
    application.add_handler(CommandHandler('start', _help))
    application.add_handler(CommandHandler('checkstatus', _checkstatus))
    application.add_handler(CommandHandler('track', _commingsoon))
    application.add_handler(CommandHandler('untrack', _commingsoon))

    # Start the Bot
    print(f"Starting the bot...")
    application.run_polling()