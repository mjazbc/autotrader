import logging
from auto_trader import Trader
import config as cfg
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import json

subscribers = set()

def subscribe(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Subscribed to autotrader notifications.')
    subscribers.add(update.effective_chat.id)
    with open('./subscribers.json', 'w') as f:
        json.dump(list(subscribers), f)

def stop(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Unsubscribed from autotrader notifications.')
    subscribers.remove(update.effective_chat.id)
    with open('./subscribers.json', 'w') as f:
        json.dump(list(subscribers), f)

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

    updater = Updater(cfg.TELEGRAM_BOT_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", subscribe))
    dispatcher.add_handler(CommandHandler("stop", stop))

    # Start the Bot
    updater.start_polling()
    
    t = Trader(wallet= {'ETH' : 0, 'USDT' : 1000}, min_price_change=0.02)

    for trade in t.run():
        for chatid in subscribers:
            updater.bot.send_message(chat_id = chatid, text = trade)