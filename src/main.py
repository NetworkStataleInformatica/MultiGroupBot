import os

import botogram

from src import db as database

bot = botogram.create(os.environ.get("BOT_TOKEN", ""))
db = database.Database(create_tables=True)

SENDER_BLACKLIST = [
    bot.itself.id,
    777000,  # Telegram
    1087968824,  # Group Anonymous bot
]


@bot.before_processing
def before_processing(chat, message):
    if message.sender.id in SENDER_BLACKLIST:
        return

    db.update_user(message.sender)
    if chat.type in ["group", "supergroup"]:
        db.update_group(chat, message.sender)


# Replaces the default botogram /help command
@bot.command("help")
def dummy_command():
    return True


@bot.command("chatid")
def chatid_command(chat, message):
    chat.send(
        f"Beep bop.\n<b>Chat ID</b>: <code>{chat.id}</code>\n<b>User ID</b>: <code>{message.sender.id}</code>",
        syntax="html"
    )


@bot.command("start")
def start_command(chat):
    chat.send("hello world")


@bot.process_message
def process_message(message):
    # -- Reputation system --
    if not message.text or not message.reply_to_message:
        return True

    if not (message.text.startswith("+") or message.text.startswith("^")):
        return True

    original_sender = message.reply_to_message.sender
    if original_sender == message.sender or original_sender.id in SENDER_BLACKLIST:
        return True

    # Make sure the original sender is in the database
    db.update_user(original_sender)
    db.increase_rep(original_sender)

    message.reply_to_message.reply(
        f"➕ <b>Reputazione di {original_sender.name} aumentata</b> [{db.get_rep(original_sender)}]"
    )
