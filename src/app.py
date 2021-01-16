import logging
from auto_trader import Trader
import config as cfg
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

subscribers = set()

def subscribe(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Subscribed to autotrader notifications.')
    subscribers.add(update.effective_chat.id)

def stop(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Subscribed to autotrader notifications.')
    subscribers.remove(update.effective_chat.id)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("./debug.log"),
            # logging.StreamHandler()
        ]
    )

    updater = Updater(cfg.TELEGRAM_BOT_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", subscribe))
    dispatcher.add_handler(CommandHandler("stop", stop))

    # Start the Bot
    updater.start_polling()

    # # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # # SIGABRT. This should be used most of the time, since start_polling() is
    # # non-blocking and will stop the bot gracefully.
    # updater.idle()
    
    t = Trader('ETH', 'USDT', 0.02)

    for trade in t.run():
        for chatid in subscribers:
            updater.bot.send_message(chat_id = chatid, text = trade)