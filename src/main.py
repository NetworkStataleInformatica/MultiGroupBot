import os

import botogram

from src import db as database

bot = botogram.create(os.environ.get("BOT_TOKEN", ""))
db = database.Database(create_tables=True)


@bot.before_processing
def before_processing(message):
    if message.sender == bot.itself:
        return

    db.update_user(message.sender)


@bot.command("start")
def start_command(chat):
    chat.send("hello world")
