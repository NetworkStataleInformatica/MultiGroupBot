import logging

from telegram.ext import Updater, CommandHandler

updater = Updater('893851442:AAEtZPUJQbHKPlrRAORI6AtEmd7Nf6G_4eU', use_context=True)

# Enable logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
dispatcher = updater.dispatcher

# Now, you can define a function that should process a specific type of update:
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Salve, sono Dennis Farina!")

# The goal is to have this function called every time the Bot receives a Telegram message 
# that contains the /start command. To accomplish that, you can use a CommandHandler 
# (one of the provided Handler subclasses) and register it in the dispatcher:
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

# And that's all you need. To start the bot, run:
updater.start_polling()
updater.idle()