import time
from tradingview_ta import TA_Handler, Interval
import config as cfg
import requests
import json
import logging

class Trader:

    def __init__(self, symbol1, symbol2, min_price_change):
        
        # initialize wallet amounts
        self.trading_pair = (symbol1, symbol2)
        self.amounts = {symbol1 : 0, symbol2 : 1000}
        self.symbol = symbol1 + symbol2
        self.price_change = min_price_change
        
        # initialize price api
        self.api = 'https://min-api.cryptocompare.com/data/pricemulti?fsyms={0}&tsyms={1}&api_key={2}'.format(symbol1, symbol2, cfg.CRYPTOCOMPARE_TOKEN)
        
        # initialize technical analysis api
        self.handler = TA_Handler()
        self.handler.set_symbol_as(self.symbol)
        self.handler.set_exchange_as_crypto_or_stock("BINANCE")
        self.handler.set_screener_as_crypto()
        self.handler.set_interval_as(Interval.INTERVAL_15_MINUTES)

    def check_recommendation(self):
        return self.handler.get_analysis().summary['RECOMMENDATION']

    def get_price(self):
        response = requests.request("GET", self.api)
        json_resp = json.loads(response.text)
        return json_resp[self.trading_pair[0]][self.trading_pair[1]]

    def buy(self, percent, price):
        quantity = self.amounts[self.trading_pair[1]] * percent
        self.amounts[self.trading_pair[0]] += quantity / price
        self.amounts[self.trading_pair[1]] -= quantity
        return 'BOUGHT '+str(quantity / price) +' '+ self.trading_pair[0]+ ' for ' + str(price)

    def sell(self, percent, price):
        quantity = self.amounts[self.trading_pair[0]] * percent
        self.amounts[self.trading_pair[1]] += quantity * price
        self.amounts[self.trading_pair[0]] -= quantity
        return'SOLD '+str(quantity) +' '+self.trading_pair[0]+' for ' + str(price)

    def handle_status_change(self, curr, price):
        result = None
        if curr == 'STRONG_BUY' and self.amounts[self.trading_pair[1]] > 0:
            result = self.buy(1, price)
        if curr == 'BUY' and self.amounts[self.trading_pair[1]] > 0:
            result = self.buy(0.4, price)
        if curr == 'SELL' and self.amounts[self.trading_pair[0]] > 0:
            result = self.sell(0.4, price)
        if curr == 'STRONG_SELL' and self.amounts[self.trading_pair[0]] > 0:
            result = self.sell(1, price)

        return result      

    def run(self):
        logging.info('Started trading '+self.symbol)
        prev_rec = 'NONE'
        prev_price = 0

        while True: 
            try:
                rec = self.check_recommendation()
                price = self.get_price()

                price_change = abs(1 - (prev_price / price))

                if rec != prev_rec and price_change > self.price_change:
                    result = self.handle_status_change(rec, price)
                    
                    if not result:
                        continue

                    logging.info(result)

                    walletstr =  '[WALLET] {:.4f} {} | {:.4f} {} | TOTAL {:.4f} {}'.format(self.amounts[self.trading_pair[0]], 
                    self.trading_pair[0], self.amounts[self.trading_pair[1]], self.trading_pair[1], 
                    self.amounts[self.trading_pair[1]] + self.amounts[self.trading_pair[0]] * price, self.trading_pair[1])

                    logging.info(walletstr)

                    yield result + '\n\n' + walletstr

                prev_rec = rec
                prev_price = price

                time.sleep(30) 
            except Exception as e:
                logging.exception('Error occurred')