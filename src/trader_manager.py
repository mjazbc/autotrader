
from auto_trader import Trader
from queue import Queue
import time
import threading


class TraderManager():
    def __init__(self, *args:Trader) -> None:
        self._bots = dict()
        self.queue = Queue()
        for bot in enumerate(args):
            bot[1].queue = self.queue
            self._bots[bot[0]] = bot[1]

    def run(self, *args:int):
        for bot_id in args:
            threading.Thread(target=self._bots[bot_id].run, args=(self.queue,), daemon=True).start()
            
    
    def run_all(self):
        for bot in self._bots.values():
             threading.Thread(target=bot.run, args=(self.queue,), daemon=True).start()
    
    def add_trader(self, trader:Trader, auto_start:bool=False) -> int:
        new_id = max(self._bots.keys()) + 1
        self._bots[new_id] = trader

        if auto_start:
            trader.run()
    
    def listen_all(self):
        while True:
            while self.queue.not_empty:
                print(self.queue.get())
            
            time.sleep(1)

    
if __name__ == "__main__":
    t = Trader(wallet= {'ETH' : 0, 'USDT' : 1000}, min_price_change = 0.02, id='slow')
    t2 = Trader(wallet= {'BTC' : 0, 'USDT' : 1000}, min_price_change = 0.005, id= 'fast')
    tm = TraderManager(t, t2)

    tm.run_all()
    tm.listen_all()

    input('Press any key to stop')