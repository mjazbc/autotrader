import time
from trader_config import TraderConfig
import db
from tradingview_ta import TA_Handler, Interval
import requests
import json
import logging
import emoji
import pickle
import os

class Trader:
    def __init__(self, config) -> None: 
        self._config = config

        self._current_price = 0.0000001
        
        # initialize price api
        self._api = 'https://min-api.cryptocompare.com/data/pricemulti?fsyms={0}&tsyms={1}&api_key={2}'.format(
            self._config.wallet.tokens[0], self._config.wallet.tokens[1], os.environ['CRYPTOCOMPARE_TOKEN'])
        
        # initialize technical analysis api
        self._handler = TA_Handler()
        self._handler.set_symbol_as(self._config.symbol)
        self._handler.set_exchange_as_crypto_or_stock("BINANCE")
        self._handler.set_screener_as_crypto()
        self._handler.set_interval_as(Interval.INTERVAL_15_MINUTES)

    def check_recommendation(self) -> str:
        return self._handler.get_analysis().summary['RECOMMENDATION']

    def get_price(self) -> float:
        response = requests.request("GET", self._api)
        json_resp = json.loads(response.text)
        return json_resp[self._config.wallet.tokens[0]][self._config.wallet.tokens[1]]

    def buy(self, percent) -> float:
        quantity = self._config.wallet.values[1] * percent
        self._config.wallet.values[0] += quantity / self._current_price
        self._config.wallet.values[1] -= quantity

        return quantity / self._current_price

    def sell(self, percent) -> float:
        quantity = self._config.wallet.values[0] * percent
        self._config.wallet.values[1] += quantity * self._current_price
        self._config.wallet.values[0] -= quantity

        return quantity
        # return'SOLD '+str(quantity) +' '+self.trading_pair[0]+' for ' + str(price)

    def handle_status_change(self, curr) -> float:
        if curr == 'STRONG_BUY' and self._config.wallet.values[1] > 0:
            return (self.buy(1), 'BUY')
        elif curr == 'BUY' and self._config.wallet.values[1] > 0:
            return (self.buy(0.4), 'BUY')
        elif curr == 'SELL' and self._config.wallet.values[0] > 0:
            return (self.sell(0.4), 'SELL')
        elif curr == 'STRONG_SELL' and self._config.wallet.values[0] > 0:
            return (self.sell(1), 'SELL')
        else:
            return (0, None)
    
    #TODO: move this out of core trader class
    def trade_pretty(self, quantity, side) -> str:
        if side == 'SELL':
            return emoji.emojize(':left_arrow: Sold {:.4f} {} for {:.4f}'.format(quantity, self._config.wallet.tokens[0], self.current_price))
        else:
            return emoji.emojize(':right_arrow: Bought {:.4f} {} for {:.4f}'.format(quantity, self._config.wallet.tokens[0], self.current_price))

    def persist(self) -> None:
        pass
        with open('./saved.pickle', 'wb') as f:
            pickle.dump(self, f)

    def run(self, queue = None):  
        prev_price = self._current_price # small number to avoid division by zero on startup
        print('running')
        while True: 
            try:
                rec = self.check_recommendation()
                self._current_price = self.get_price()

                price_change = abs(1 - (prev_price / self._current_price))

                if price_change >= self._config.min_change_price or 'STRONG' in rec:
                    traded = self.handle_status_change(rec)
                    
                    # self.persist()
                    if traded[0] <= 0:
                        continue
                    
                    prev_price = self._current_price
                    # prev_rec = rec
                    
                    tradedstr = self.trade_pretty(*traded)
                    walletstr = self._config.wallet.pretty_print(self._current_price)

                    if queue:
                        queue.put((self._config.name, traded))

                    logging.info(tradedstr)
                    logging.info(walletstr)

            except:
                logging.exception('Error occurred')
            finally:
                time.sleep(30) 


if __name__ == "__main__":
    pass
    try:
        with open('./saved.pickle', 'rb') as f:
            t = pickle.load(f)
    except:
        t = Trader(wallet= {'ETH' : 0, 'USDT' : 1000}, min_price_change=0.02, name='dev')

    log_format = '[%(asctime)s] [%(levelname)s] - %(message)s'
    logging.basicConfig(level='DEBUG', format=log_format)    
    t.run()
    input()