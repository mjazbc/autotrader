
from auto_trader import Trader
from queue import Queue
import time
import threading
import db


class TraderManager():
    def __init__(self) -> None:
        active_bots = db.load_active_traders()
        self._bots = {bot : Trader(db.load_trader_config(bot)) for bot in active_bots}
        self.queue = Queue()

    def run(self, *args:str):
        for name in args:
            threading.Thread(target=self._bots[name].run, args=(self.queue,), daemon=True).start()
              
    def run_all(self):
        for bot in self._bots.values():
             threading.Thread(target=bot.run, args=(self.queue,), daemon=True).start()
    
    def add_trader(self, trader:Trader, auto_start:bool=False) -> None:
        self._bots[trader.name] = trader

        if auto_start:
            self.run(trader.name)
    
    def listen_all(self):
        while True:
            while self.queue.not_empty:
                print(self.queue.get())
            
            time.sleep(1)

    
if __name__ == "__main__":
    tm = TraderManager()

    tm.run_all()
    tm.listen_all()

    input('Press any key to stop')