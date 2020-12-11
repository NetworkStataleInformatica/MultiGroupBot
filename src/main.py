import os
import re
from datetime import datetime as dt, timedelta as td

import botogram

from src import db as database
from src import utils

bot = botogram.create(os.environ.get("BOT_TOKEN", ""))
db = database.Database(create_tables=True)

SENDER_BLACKLIST = [
    bot.itself.id,
    777000,  # Telegram
    1087968824,  # Group Anonymous bot
]
VALID_CDL = [
    "generale",
    "informatica",
    "informatica_musicale",
    "informatica_com_digitale",
    "sicurezza_sistemi_reti_informatiche",
    "sicurezza_sistemi_reti_informatiche_online",
]


@bot.before_processing
def before_processing(chat, message):
    if message.sender.id in SENDER_BLACKLIST:
        return True
    if message.text is not None and message.text.startswith("/register"):
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


# Adds a new group to the database
@bot.command("register")
def register_command(chat, message, args):
    if db.get_permissions_level(message.sender) < 2:
        return True

    if len(args) < 3:
        return message.reply(
            "<b>Comando utilizzato dagli amministratori per registrare un gruppo al database del bot.</b>"
            "\n<b>Utilizzo</b>: <code>/register cdl anno_accademico numero_semestre</code>"
            "\n- <b><u>cdl</u></b>: deve essere uno esattamente di " +
            ", ".join(f"<code>{c.upper()}</code>" for c in VALID_CDL) +
            "\n- <b><u>anno_accademico</u></b>: anno in cui è svolto il corso (il primo anno è 1). "
            "Se non è un gruppo legato a un corso mettere 0."
            "\n- <b><u>numero_semestre</u></b>: semestre in cui si svolge il corso (può essere 1 o 2). "
            "Se non è un gruppo legato a un corso mettere 0."
            "\n\n<b>Esempio</b>: <code>/register INFORMATICA_MUSICALE 3 2</code>",
            syntax="html",
        )
    cdl = args[0].lower()
    if cdl not in VALID_CDL:
        return message.reply("CDL non valido. Fai /register per vedere l'help del comando")

    try:
        academic_year = int(args[1])
    except TypeError:
        return message.reply("Semestre non valido. Fai /register per vedere l'help del comando")
    if academic_year < 0 or academic_year > 5:
        return message.reply("Anno accademico non valido. Fai /register per vedere l'help del comando")

    try:
        semester = int(args[2])
    except TypeError:
        return message.reply("Semestre non valido. Fai /register per vedere l'help del comando")
    if not (0 <= semester <= 2):
        return message.reply("Semestre non valido. Fai /register per vedere l'help del comando")

    db.exec("DELETE FROM groups WHERE group_id=%s", (chat.id, ))
    db.exec(
        "INSERT INTO groups(group_id, title, invite_link, degree_name, academic_year, semester) "
        "VALUES(%s, %s, %s, %s, %s, %s)",
        (chat.id, chat.title, chat.invite_link, cdl, academic_year, semester)
    )
    message.reply("<b>Gruppo aggiunto al database</b>")

