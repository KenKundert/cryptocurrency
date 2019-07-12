from quantiphy import Quantity, UnitConversion, UnknownConversion
from inform import warn, comment, cull

__version__ = '0.1.0'
__released__ = '2019-07-12'


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
        try:
            # SYMBOL is not unique
            #return UnitConversion(to, (cls.SYMBOL, cls.UNITS), data[cls.UNITS][to[-1]])
            return UnitConversion(to, cls.UNITS, data[cls.UNITS][to[-1]])
        except KeyError as e:
            comment(f'missing price in {e}.', culprit=cls.UNITS)

    @classmethod
    def names(cls):
        for s in cls.__subclasses__():
            yield s.__name__

    @classmethod
    def units(cls):
        for s in cls.__subclasses__():
            yield s.UNITS

    @classmethod
    def currencies(cls):
        for s in sorted(cls.__subclasses__(), key=lambda s: s.__name__):
            yield s

    @classmethod
    def currency(cls, name):
        for s in cls.__subclasses__():
            if name == s.__name__:
                return s

class USD(Currency):
    UNITS = 'USD'
    NAME = 'US Dollar'
    SYMBOL = '$'
    one = Quantity(1, UNITS)

class BTC(Currency):
    UNITS = 'BTC'
    NAME = 'Bitcoin'
    SYMBOL = 'Ƀ'
    one = Quantity(1, UNITS)

class ETH(Currency):
    UNITS = 'ETH'
    NAME = 'Ethereum'
    SYMBOL = 'Ξ'
    one = Quantity(1, UNITS)

class BCH(Currency):
    UNITS = 'BCH'
    NAME = 'Bitcoin Cash'
    SYMBOL = '฿'
    one = Quantity(1, UNITS)

class BTG(Currency):
    UNITS = 'BTG'
    NAME = 'Bitcoin Gold'
    SYMBOL = '฿'
    one = Quantity(1, UNITS)

class EOS(Currency):
    UNITS = 'EOS'
    NAME = 'EOS'
    SYMBOL = 'Ȅ'
    one = Quantity(1, UNITS)

class ZEC(Currency):
    UNITS = 'ZEC'
    NAME = 'Zcash'
    SYMBOL = 'ⓩ'
    one = Quantity(1, UNITS)

class IOT(Currency):
    UNITS = 'MIOTA'
    NAME = 'IOTA'
    SYMBOL = 'ι'
    one = Quantity(1, UNITS)

class ADA(Currency):
    UNITS = 'ADA'
    NAME = 'Cardano'
    SYMBOL = 'ℂ'
    one = Quantity(1, UNITS)

    # @classmethod
    # def converter(cls, to, data):
    # #    # cannot convert this to '$' directly using cryptocompare.
    # #    # instead, use ETH as intermediary
    #     conversion = data[cls.UNITS]['ETH'] * data['ETH'][to[-1]]
    #     return UnitConversion(to, (cls.SYMBOL, cls.UNITS), conversion)

class BLACK(Currency):
    UNITS = 'BLACK'
    NAME = 'EOS Black'
    one = Quantity(1, UNITS)

    @classmethod
    def converter(cls, to, data):
        # cannot convert this to '$' directly using cryptocompare.
        # instead, use EOS as intermediary
        conversion = data[cls.UNITS]['EOS'] * data['EOS'][to[-1]]
        units = getattr(cls, 'UNITS', None)
        symbol = getattr(cls, 'SYMBOL', None)
        return UnitConversion(to, cull([symbol, units]), conversion)

class HORUS(Currency):
    UNITS = 'HORUS'
    NAME = 'Horus Pay'
    one = Quantity(1, UNITS)

    @classmethod
    def converter(cls, to, data):
        # cannot convert this to '$' directly using cryptocompare.
        # instead, use EOS as intermediary
        conversion = data[cls.UNITS]['EOS'] * data['EOS'][to[-1]]
        units = getattr(cls, 'UNITS', None)
        symbol = getattr(cls, 'SYMBOL', None)
        return UnitConversion(to, cull([symbol, units]), conversion)

class IQ(Currency):
    UNITS = 'IQ'
    NAME = 'Everipedia'
    one = Quantity(1, UNITS)

class CET(Currency):
    UNITS = 'CET'
    NAME = 'CoinEx'
    one = Quantity(1, UNITS)

class KARMA(Currency):
    UNITS = 'KARMA'
    NAME = 'Karma'
    one = Quantity(1, UNITS)

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
        total_dollars = 0
        for token in self.totals.values():
            try:
                total_dollars += token.scale('$')
            except UnknownConversion:
                pass # this will get reported elsewhere
        return Quantity(total_dollars, '$')

    def total_cost(self):
        "Total cost of tokens purchased in dollars."
        return Quantity(sum(self.costs.values()), '$')

    def largest_share(self):
        "Value of currency in dollars with the largest holdings."
        max_dollars = 0
        for token in self.totals.values():
            try:
                dollars = token.scale('$')
                if dollars >= max_dollars:
                    max_dollars = dollars
            except UnknownConversion:
                pass # this will get reported elsewhere
        return Quantity(max_dollars, '$')

