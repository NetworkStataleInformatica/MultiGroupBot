import json
from datetime import datetime, timedelta

import botogram

RESTRICTION_TIMES = {
    60*60: '1h',
    24*60*60: '1d',
    7*24*60*60: '1w',
    30*24*60*60: '1m',
    0: 'per sempre 🚫'
}


def get_restriction_target(message, args):
    target = None
    if len(args) > 0:
        try:
            target = int(args[0])
        except ValueError:
            pass

    if message.reply_to_message:
        target = message.reply_to_message.sender.id

    if target is None:
        message.reply("<b>Errore</b>.\nDevi specificare chi bannare. "
                      "Puoi rispondere a un suo messaggio oppure scrivere "
                      "<code>/globalban ID</code> dove ID è il suo ID univoco di Telegram")
    return target


def network_restriction(bot, db, target, restriction_type, restriction_time):
    groups = db.exec("SELECT group_id FROM groups;", fetch=db.FETCH_ALL)
    for group in groups:
        group = group[0]
        try:
            if restriction_type == "ban":
                bot.chat(group).kick(target, calculate_rescrition_end_date(restriction_time))
                db.exec("UPDATE users SET banned=true WHERE user_id=%s", (target, ))
            elif restriction_type == "mute":
                bot.api.call("restrictChatMember", {
                    "chat_id": group,
                    "user_id": target,
                    "permissions": json.dumps({key: False for key in [
                        "can_send_messages",
                        "can_send_media_messages",
                        "can_send_polls",
                        "can_send_other_messages",
                        "can_add_web_page_previews",
                        "can_change_info",
                        "can_invite_users",
                        "can_pin_messages"
                    ]}),
                    "until_date": calculate_rescrition_end_date(restriction_time).timestamp()
                })
            elif restriction_type == "unban":
                bot.api.call("restrictChatMember", {
                    "chat_id": group,
                    "user_id": target,
                    "permissions": json.dumps({key: True for key in [
                        "can_send_messages",
                        "can_send_media_messages",
                        "can_send_polls",
                        "can_send_other_messages",
                        "can_add_web_page_previews",
                        "can_change_info",
                        "can_invite_users",
                        "can_pin_messages"
                    ]})
                })
                db.exec("UPDATE users SET banned=false WHERE user_id=%s", (target, ))
        except botogram.api.APIError:
            continue


def gen_restriction_times_inline_keyboard(restriction_type, selected):
    btns = botogram.Buttons()
    for r in RESTRICTION_TIMES:
        btns[0 if r != 0 else 1]\
            .callback(('✅ ' if r == selected else '') + RESTRICTION_TIMES[r],
                      "restrict_time", f"{restriction_type}@{r}")
    return btns


def calculate_rescrition_end_date(delta_seconds):
    return datetime.now() + timedelta(seconds=delta_seconds)
