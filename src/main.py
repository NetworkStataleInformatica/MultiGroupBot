import os
import re

import botogram

from src import db as database
from src import utils

bot = botogram.create(os.environ.get("BOT_TOKEN", ""))
db = database.Database()

SENDER_BLACKLIST = [
    bot.itself.id,
    777000,  # Telegram
    1087968824,  # Group Anonymous bot
]


@bot.before_processing
def before_processing(chat, message):
    if message.sender.id in SENDER_BLACKLIST:
        return True

    db.update_user(message.sender, chat)


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
    if db.get_permissions_level(message.sender) < 1:
        return True

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


@bot.command("networkmute")
@bot.command("networkban")
@bot.command("networkunban")
@bot.command("networkunmute")
def networkban(message, args):
    if db.get_permissions_level(message.sender) < 1:
        return True

    action = message.text[len("/network"):]
    if action == "unmute":
        action = "unban"

    target = utils.get_restriction_target(message, args)
    utils.network_restriction(bot, db, target, action, 0)
    if action == "unban":
        return message.reply(f"🌈 <b>Utente #{target} sbannato</b>")

    btns = utils.gen_restriction_times_inline_keyboard(action, 0)
    message.reply(
        f"🔨 <b>Utente #{target} {'silurato' if action == 'ban' else 'mutato'}.</b>"
        "\n⏳ <b>Durata</b>: per sempre",
        syntax="html", attach=btns,
    )


@bot.callback("restrict_time")
def ban_callback(message, query, data):
    if db.get_permissions_level(query.sender) < 1:
        query.notify("403 Forbidden", alert=True)
        return True

    prog = re.compile(r"#\d+")
    result = prog.search(message.text)
    target = int(result.group()[1:])
    action = data.split('@')[0]
    restriction_time = int(data.split('@')[1])

    utils.network_restriction(bot, db, target, action, restriction_time)
    btns = utils.gen_restriction_times_inline_keyboard(action, restriction_time)
    try:
        message.edit(
            f"🔨 <b>Utente #{target} {'silurato' if action == 'ban' else 'mutato'}.</b>"
            f"\n⏳ <b>Durata</b>: {utils.RESTRICTION_TIMES[restriction_time]}",
            syntax="html", attach=btns,
        )
    except botogram.api.APIError:
        query.notify("Hai premuto la stessa durata già precedentemente selezionata."
                     "\nOgni volta che lo fai un gattino (digitale) muore 😿", alert=True)


@bot.command("id")
def id_command(chat, message):
    chat.send(
        f"👥 <b>Chat ID</b>: <code>{chat.id}</code>"
        f"\n👤 <b>User ID</b>: <code>{message.sender.id}</code>"
        f"\n🆔 <b>Message ID</b>: <code>{message.id}</code>",
        syntax="html",
    )
