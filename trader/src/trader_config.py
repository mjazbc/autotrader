import emoji


class TraderConfig:
    def __init__(self, name:str, wallet: dict, **kwargs) -> None:
        self.name = name
        self.wallet = Wallet(wallet)
        self.symbol = ''.join(self.wallet.tokens)
        self.min_change_price = kwargs.get('min_change_price',0)


class Wallet:
    def __init__(self, wallet: dict) -> None:
        self.tokens = list(wallet.keys())
        self.values = list(wallet.values())

    def pretty_print(self, current_price:float) -> str:
        w = emoji.emojize(':credit_card:\n{:.4f} {}\n{:.4f} {}\n\nTotal:\n{:.4f} {}'.format(self.values[0], self.tokens[0], 
            self.values[1], self.tokens[1], self.values[1] + self.values[0] * current_price, self.tokens[1]))
        return w