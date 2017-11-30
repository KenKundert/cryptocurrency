from quantiphy import Quantity, UnitConversion
from inform import warn

__version__ = '0.0.3'
__released__ = '2017-11-27'


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

class ZEC(Currency):
    UNITS = 'ZEC'
    SYMBOL = 'ⓩ'
    one = Quantity(1, UNITS)


class EOS(Currency):
    UNITS = 'EOS'
    SYMBOL = 'Ȅ'
    one = Quantity(1, UNITS)

    @classmethod
    def converter(cls, to, data):
        # cannot convert this to '$' directly using cryptocompare.
        # instead, use ETH as intermediary
        conversion = data[cls.UNITS]['ETH'] * data['ETH'][to[-1]]
        return UnitConversion(to, (cls.SYMBOL, cls.UNITS), conversion)

accounts = {}
class Account:
    def __init__(self, owner, default=True):
        self.owner = owner
        self.default = default
        self.transactions = []
        self.totals = {}
        accounts[owner] = self
        self.costs = {}

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
        self.totals[kind] = Quantity(
            float(tokens) + self.totals.get(kind, 0), units=tokens.UNITS
        )
        self.costs[kind] = Quantity(
            t.cost + self.costs.get(kind, 0), units='$'
        )

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
        return Quantity(sum(self.costs.values()), '$')
