import time
from tradingview_ta import TA_Handler, Interval
import config as cfg
import requests
import json
import logging

class Trader:
    def __init__(self, wallet: dict, min_price_change:float) -> None:
        
        # initialize wallet amounts
        self.wallet = wallet
        self.tokens = list(wallet.keys())
        self.values = list(wallet.values())
        self.symbol = ''.join(self.tokens)
        self.price_change = min_price_change
        
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

    def buy(self, percent, price) -> float:
        quantity = self.values[1] * percent
        self.values[0] += quantity / price
        self.values[1] -= quantity

        return quantity / price
        # return 'BOUGHT '+str(quantity / price) +' '+ self.trading_pair[0]+ ' for ' + str(price)

    def sell(self, percent, price) -> float:
        quantity = self.values[0] * percent
        self.values[1] += quantity * price
        self.values[0] -= quantity

        return quantity
        # return'SOLD '+str(quantity) +' '+self.trading_pair[0]+' for ' + str(price)

    def handle_status_change(self, curr, price) -> float:
        if curr == 'STRONG_BUY' and self.values[1] > 0:
            return (self.buy(1, price), 'BUY')
        elif curr == 'BUY' and self.values[1] > 0:
            return (self.buy(0.4, price), 'BUY')
        elif curr == 'SELL' and self.values[0] > 0:
            return (self.sell(0.4, price), 'SELL')
        elif curr == 'STRONG_SELL' and self.values[0] > 0:
            return (self.sell(1, price), 'SELL')
        else:
            return (0, None)

    def wallet_pretty(self, price) -> str:
        w = '[WALLET] {:.4f} {} | {:.4f} {} | TOTAL {:.4f} {}'.format(self.values[0], self.tokens[0], 
            self.values[1], self.tokens[1], self.values[1] + self.values[0] * price, self.tokens[1])
        return w
    
    def trade_pretty(self, quantity, side, price) -> str:
        if side == 'SELL':
            return 'SOLD {:.4f} {} for {:.4f}'.format(quantity, self.tokens[0], price)
        else:
            return 'BOUGHT {:.4f} {} for {:.4f}'.format(quantity, self.tokens[1], price)


    def run(self) -> None:
        logging.info('Started trading '+self.symbol)
        prev_rec = 'NONE'
        prev_price = 0

        while True: 
            try:
                rec = self.check_recommendation()
                price = self.get_price()

                price_change = abs(1 - (prev_price / price))

                if rec != prev_rec and price_change > self.price_change:
                    traded = self.handle_status_change(rec, price)
                    
                    if traded[0] <= 0:
                        continue
                    
                    prev_price = price  
                    
                    tradedstr = self.trade_pretty(*traded, price)
                    walletstr = self.wallet_pretty(price)

                    logging.info(tradedstr)
                    logging.info(walletstr)

                    yield tradedstr + '\n\n' + walletstr

                prev_rec = rec
                
            except:
                logging.exception('Error occurred')
            finally:
                time.sleep(30) 