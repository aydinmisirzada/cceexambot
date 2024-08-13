from multiprocessing import Process
import os
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode

from fetcher import start_fetcher
from init_db import add_subscription, add_user_if_not_exists, delete_subcription, get_user_subscription
from scraper import LANG_LEVELS_WHITELIST, get_total_number_of_seats_for_level, get_seats_from_db, get_or_fetch_seats

from utils import get_help_messages, print_for_telegram

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')


async def _checkstatus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = await update.effective_chat.send_message(
        text="_Loading\.\.\. this may take a minute_",
        parse_mode=ParseMode.MARKDOWN_V2
    )

    levels = LANG_LEVELS_WHITELIST
    chat_id = update.effective_chat.id
    message_id = msg.id

    if context.args:
        levels = [x.upper()
                  for x in context.args if x.upper() in LANG_LEVELS_WHITELIST]

        if len(levels) == 0:
            await context.bot.edit_message_text(
                text="You've provided incorrect data",
                message_id=message_id,
                chat_id=chat_id,
                parse_mode=ParseMode.MARKDOWN_V2
            )

            return

    result = get_or_fetch_seats(levels)
    text = print_for_telegram(result)

    await context.bot.edit_message_text(
        text=text,
        message_id=message_id,
        chat_id=chat_id,
        parse_mode=ParseMode.MARKDOWN_V2
    )


async def _help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_chat.send_message(text=get_help_messages())

# Main function to handle the /track command


async def _track(update: Update, context: ContextTypes.DEFAULT_TYPE):
    interval = os.getenv('FETCH_INTERVAL')

    if not interval:
        print('No FETCH_INTERVAL provided')

    # If the user provided specific levels, use them; otherwise, track all levels
    if context.args:
        levels = [level for level in context.args if level in LANG_LEVELS_WHITELIST]
        if not levels:
            levels = list(LANG_LEVELS_WHITELIST)
    else:
        levels = list(LANG_LEVELS_WHITELIST)

    subscriber_id = update.effective_user.id
    chat_id = update.effective_chat.id

    # Add the user to the bot_users table if they don't exist, or update their last usage
    add_user_if_not_exists(subscriber_id, chat_id)

    # Add or update the subscription in the subscriptions table
    add_subscription(subscriber_id, levels)

    job_removed = remove_job_if_exists(str(chat_id), context)
    context.job_queue.run_repeating(
        check_db_and_notify,
        int(interval),
        chat_id=chat_id,
        name=str(subscriber_id)
    )

    text = "You have successfully subscribed to the updates! We'll notify you as soon as there's an available seat for the tracked language levels"

    if job_removed:
        text += "\n\nThe old subscription was removed."

    await update.effective_chat.send_message(
        text=text,
    )


async def _untrack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    subscriber_id = update.effective_user.id
    chat_id = update.effective_chat.id

    delete_subcription(subscriber_id)

    job_removed = remove_job_if_exists(str(chat_id), context)

    if job_removed:
        await update.effective_chat.send_message(
            text="You have successfully unsubscribed from the updates!",
        )
    else:
        await update.effective_chat.send_message(
            text="You are not currently subscribed to the updates!",
        )


async def check_db_and_notify(context: ContextTypes.DEFAULT_TYPE) -> None:
    print('Checking db...')
    job = context.job
    subscriber_id = int(job.name)

    data = get_seats_from_db(LANG_LEVELS_WHITELIST)
    total_number_per_level = get_total_number_of_seats_for_level(data)

    # Fetch users and their subscriptions
    user_subscription = get_user_subscription(subscriber_id)

    subscribed_levels = user_subscription[2].split(',')

    text = ''

    for l in subscribed_levels:
        if total_number_per_level[l] is not None:
            text += f"{l}: {total_number_per_level[l]} seats\n"
        else:
            print('No seats found for', l)

    if text:
        text += '\n[Register now!](https://ujop.cuni.cz/UJOP-371.html?ujopcmsid=4)'
        await context.bot.send_message(job.chat_id, text=text, parse_mode=ParseMode.MARKDOWN_V2)

        delete_subcription(subscriber_id)
        remove_job_if_exists(job.name, context=context)


def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


if __name__ == '__main__':
    print("Initializing the bot...")

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler(["start", "help"], _help))
    application.add_handler(CommandHandler('checkstatus', _checkstatus))
    application.add_handler(CommandHandler('track', _track))
    application.add_handler(CommandHandler('untrack', _untrack))

    # Start the data fetcher in a separate thread
    fetcher_process = Process(target=start_fetcher)

    fetcher_process.start()

    print('Starting the bot...')
    application.run_polling()

    fetcher_process.join()
