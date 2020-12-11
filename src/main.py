import os

import botogram

from src import db as database

bot = botogram.create(os.environ.get("BOT_TOKEN", ""))
db = database.Database(create_tables=True)


@bot.before_processing
def before_processing(chat, message):
    if message.sender == bot.itself:
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
