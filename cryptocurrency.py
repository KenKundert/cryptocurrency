from quantiphy import Quantity, UnitConversion
from inform import warn

__version__ = '0.0.14'
__released__ = '2018-02-25'


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

    @classmethod
    def converter(cls, to, data):
        return UnitConversion(to, (cls.SYMBOL, cls.UNITS), data[cls.UNITS][to[-1]])

    @classmethod
    def names(cls):
        for s in cls.__subclasses__():
            yield s.__name__

    @staticmethod
    def currency(name):
        for s in Currency.__subclasses__():
            if s.__name__ == name:
                return Quantity(tokens, s.UNITS)

class USD(Currency):
    UNITS = 'USD'
    SYMBOL = '$'
    one = Quantity(1, UNITS)

class BTC(Currency):
    UNITS = 'BTC'
    SYMBOL = 'Ƀ'
    one = Quantity(1, UNITS)

class ETH(Currency):
    UNITS = 'ETH'
    SYMBOL = 'Ξ'
    one = Quantity(1, UNITS)

class BCH(Currency):
    UNITS = 'BCH'
    SYMBOL = '฿'
    one = Quantity(1, UNITS)

class BTG(Currency):
    UNITS = 'BTG'
    SYMBOL = '฿'
    one = Quantity(1, UNITS)

class ZEC(Currency):
    UNITS = 'ZEC'
    SYMBOL = 'ⓩ'
    one = Quantity(1, UNITS)

class EOS(Currency):
    UNITS = 'EOS'
    SYMBOL = 'Ȅ'
    one = Quantity(1, UNITS)


class IOT(Currency):
    UNITS = 'IOT'
    SYMBOL = 'ι'
    one = Quantity(1, UNITS)

class ADA(Currency):
    UNITS = 'ADA'
    SYMBOL = 'ℂ'
    one = Quantity(1, UNITS)

    # @classmethod
    # def converter(cls, to, data):
    # #    # cannot convert this to '$' directly using cryptocompare.
    # #    # instead, use ETH as intermediary
    #     conversion = data[cls.UNITS]['ETH'] * data['ETH'][to[-1]]
    #     return UnitConversion(to, (cls.SYMBOL, cls.UNITS), conversion)

accounts = {}
class Account:
    def __init__(self, owner, default=True):
        self.owner = owner
        self.default = default
        self.transactions = []
        accounts[owner] = self
        self.totals = {}     # total value in dollars by token
        self.costs = {}      # total cost in dollars by token
        self.purchased = {}  # number of tokens actually purchased by token

    class Transaction:
        def __init__(self, tokens, date, comment):
            self.tokens = tokens
            self.date = date
            self.cost = tokens.in_dollars()
            self.comment = comment

        def fee(self):
            return Quantity(self.cost - self.tokens.in_dollars(), '$')

    def transaction(self, tokens, date=None, comment=''):
        t = self.Transaction(tokens, date, comment)
        self.transactions.append(t)
        kind = tokens.name()
        num_tokens = float(tokens)
        self.totals[kind] = Quantity(
            num_tokens + self.totals.get(kind, 0), units=tokens.UNITS
        )
        self.costs[kind] = Quantity(
            t.cost + self.costs.get(kind, 0), units='$'
        )
        if t.cost > 0:
            self.purchased[kind] = Quantity(
                num_tokens + self.purchased.get(kind, 0), tokens.UNITS
            )

    def confirm_balance(self, kind, tokens):
        actual = self.totals[kind.__name__]
        expected = Quantity(tokens, kind.UNITS)
        if not actual.is_close(expected):
            delta = Quantity(actual - tokens, kind.UNITS)
            warn(f'expected {expected}, found {actual}, difference {delta}')

    def total_value(self):
        "Total value of current holdings in dollars."
        return Quantity(
            sum(token.scale('$') for token in self.totals.values()), '$'
        )

    def total_cost(self):
        "Total cost of tokens purchased in dollars."
        return Quantity(sum(self.costs.values()), '$')
