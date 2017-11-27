from quantiphy import Quantity
from inform import warn

__version__ = '0.0.1'
__released__ = '2017-11-26'


class Currency:
    def __init__(self, tokens, price=0):
        self.tokens = Quantity(tokens, self.UNITS)
        self.price = Quantity(price, '$')

    def in_tokens(self):
        return self.tokens

    def in_dollars(self, price=None):
        price = self.price if price is None else price
        return Quantity(self.tokens * price, '$')

    def name(self):
        return self.__class__.__name__

    def __str__(self):
        return self.tokens.render()

    def __float__(self):
        return float(self.tokens)


class BTC(Currency):
    UNITS = 'Ƀ'
    total = 0

class ETH(Currency):
    UNITS = 'Ξ'
    total = 0

class BCH(Currency):
    UNITS = 'BCH'
    total = 0

class ZEC(Currency):
    UNITS = 'ZEC'

accounts = {}
class Account:
    def __init__(self, owner):
        self.owner = owner
        self.transactions = []
        self.totals = {}
        accounts[owner] = self
        self.cost = 0

    class Transaction:
        def __init__(self, tokens, date, comment):
            self.tokens = tokens
            self.date = date
            self.cost = tokens.in_dollars()
            self.comment = comment

        def fee(self):
            return Quantity(self.cost - self.tokens.in_dollars(), '$')

    def transaction(self, tokens, date, comment=''):
        t = self.Transaction(tokens, date, comment)
        self.transactions.append(t)
        kind = tokens.name()
        self.totals[kind] = Quantity(
            float(tokens) + self.totals.get(kind, 0), units=tokens.UNITS
        )
        self.cost += t.cost

    def confirm_balance(self, kind, tokens):
        actual = self.totals[kind.__name__]
        expected = Quantity(tokens, kind.UNITS)
        if not actual.is_close(expected):
            delta = Quantity(actual - tokens, kind.UNITS)
            warn(f'expected {expected}, found {actual}, difference {delta}')

    def total_value(self):
        return Quantity(
            sum(token.scale('$') for token in self.totals.values()), '$'
        )

    def total_cost(self):
        return Quantity(self.cost, '$')


