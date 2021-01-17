import time
from tradingview_ta import TA_Handler, Interval
import config as cfg
import requests
import json
import logging
import emoji
import pickle
import uuid

class Trader:
    def __init__(self, wallet: dict, min_price_change:float, id:str = None) -> None: 
        # initialize wallet amounts
        self.tokens = list(wallet.keys())
        self.values = list(wallet.values())
        self.symbol = ''.join(self.tokens)
        self.price_change = min_price_change
        self.current_price = 0
        self.id = id
        
        if not id:
            self.id = uuid.uuid4().hex
        
        # initialize price api
        self.api = 'https://min-api.cryptocompare.com/data/pricemulti?fsyms={0}&tsyms={1}&api_key={2}'.format(
            self.tokens[0], self.tokens[1], cfg.CRYPTOCOMPARE_TOKEN)
        
        # initialize technical analysis api
        self.handler = TA_Handler()
        self.handler.set_symbol_as(self.symbol)
        self.handler.set_exchange_as_crypto_or_stock("BINANCE")
        self.handler.set_screener_as_crypto()
        self.handler.set_interval_as(Interval.INTERVAL_15_MINUTES)

    def check_recommendation(self) -> str:
        return self.handler.get_analysis().summary['RECOMMENDATION']

    def get_price(self) -> float:
        response = requests.request("GET", self.api)
        json_resp = json.loads(response.text)
        return json_resp[self.tokens[0]][self.tokens[1]]

    def buy(self, percent) -> float:
        quantity = self.values[1] * percent
        self.values[0] += quantity / self.current_price
        self.values[1] -= quantity

        return quantity / self.current_price

    def sell(self, percent) -> float:
        quantity = self.values[0] * percent
        self.values[1] += quantity * self.current_price
        self.values[0] -= quantity

        return quantity
        # return'SOLD '+str(quantity) +' '+self.trading_pair[0]+' for ' + str(price)

    def handle_status_change(self, curr) -> float:
        if curr == 'STRONG_BUY' and self.values[1] > 0:
            return (self.buy(1), 'BUY')
        elif curr == 'BUY' and self.values[1] > 0:
            return (self.buy(0.4), 'BUY')
        elif curr == 'SELL' and self.values[0] > 0:
            return (self.sell(0.4), 'SELL')
        elif curr == 'STRONG_SELL' and self.values[0] > 0:
            return (self.sell(1), 'SELL')
        else:
            return (0, None)

    def wallet_pretty(self) -> str:
        w = emoji.emojize(':credit_card:\n{:.4f} {}\n{:.4f} {}\n\nTotal:\n{:.4f} {}'.format(self.values[0], self.tokens[0], 
            self.values[1], self.tokens[1], self.values[1] + self.values[0] * self.current_price, self.tokens[1]))
        return w
    
    def trade_pretty(self, quantity, side) -> str:
        if side == 'SELL':
            return emoji.emojize(':left_arrow: Sold {:.4f} {} for {:.4f}'.format(quantity, self.tokens[0], self.current_price))
        else:
            return emoji.emojize(':right_arrow: Bought {:.4f} {} for {:.4f}'.format(quantity, self.tokens[0], self.current_price))

    def persist(self) -> None:
        pass
        with open('./saved.pickle', 'wb') as f:
            pickle.dump(self, f)

    # def run(self):
    #     logging.info('Started trading '+self.symbol)
    #     threading.Thread(target=self._run_thread, daemon=True).start()

    def run(self, queue = None):  
        prev_rec = 'NONE'
        prev_price = self.current_price
        print('running')
        while True: 
            try:
                rec = self.check_recommendation()
                self.current_price = self.get_price()

                price_change = abs(1 - (prev_price / self.current_price))

                if rec != prev_rec and price_change > self.price_change:
                    traded = self.handle_status_change(rec)
                    
                    # self.persist()
                    if traded[0] <= 0:
                        continue
                    
                    prev_price = self.current_price
                    prev_rec = rec
                    
                    tradedstr = self.trade_pretty(*traded)
                    walletstr = self.wallet_pretty()

                    if queue:
                        queue.put((self.id, traded))

                    logging.info(tradedstr)
                    logging.info(walletstr)

                    # self.persist()
            except:
                logging.exception('Error occurred')
            finally:
                time.sleep(30) 


if __name__ == "__main__":
    log_format = '[%(asctime)s] [%(levelname)s] - %(message)s'
    logging.basicConfig(level='DEBUG', format=log_format)    
    t = Trader(wallet= {'ETH' : 0, 'USDT' : 1000}, min_price_change=0.02)
    t.run()
    input()