from quantiphy import Quantity
from inform import warn

__version__ = '0.0.0'
__released__ = '2017-11-16'


class Currency:
    def __init__(self, tokens, price):
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
        def __init__(self, tokens, date, cost, comment):
            self.tokens = tokens
            self.date = date
            self.cost = Quantity(cost, '$')
            if cost and tokens.in_dollars() > cost + 0.005:
                value = tokens.in_dollars()
                cost = Quantity(cost, '$')
                warn(
                    f'value ({value}) exceeds cost ({cost}).',
                    culprit=(tokens.name(), date)
                )
            self.comment = comment

        def fee(self):
            return Quantity(self.cost - self.tokens.in_dollars(), '$')

    def transaction(self, tokens, date, cost=0, comment=''):
        t = self.Transaction(tokens, date, cost, comment)
        self.transactions.append(t)
        kind = tokens.name()
        self.totals[kind] = Quantity(
            float(tokens) + self.totals.get(kind, 0), units=tokens.UNITS
        )
        self.cost += t.cost

    def total_value(self):
        return Quantity(
            sum(token.scale('$') for token in self.totals.values()), '$'
        )

    def total_cost(self):
        return Quantity(self.cost, '$')


