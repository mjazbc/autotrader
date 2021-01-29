import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import json
import requests
import os

trader_api_url = 'http://trader:5000'
subscribers = set()
t = object()

def start(update: Update, context: CallbackContext) -> None:
    url = trader_api_url + '/user/' + update.effective_chat.id
    response = requests.request("POST", url)
    update.message.reply_text('Hello! Use /trade command to start your bot.')

def stop(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Unsubscribed from autotrader notifications.')
    subscribers.remove(update.effective_chat.id)
    
    #TODO remove user and all bots

def wallet(update: Update, context: CallbackContext) -> None:
     update.message.reply_text(t.wallet_pretty())

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("./debug.log"),

        ]
    )

    try:
        with open('./subscribers.json', 'r') as f:
            subscribers = set(json.load(f))
    except:
        subscribers = set()

    updater = Updater(os.environ['TELEGRAM_BOT_TOKEN'], use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("stop", stop))
    dispatcher.add_handler(CommandHandler("wallet", wallet))

    # Start the Bot
    updater.start_polling()
    
    # for trade in t.run():
    #     for chatid in subscribers:
    #         updater.bot.send_message(chat_id = chatid, text = trade)

    input('Press any key to exit')
   