from quantiphy import Quantity, UnitConversion, UnknownConversion
from inform import Error, warn, comment, cull, conjoin, dedent, plural

__version__ = '0.1.0'
__released__ = '2019-07-12'


class Dollars(Quantity):
    units = '$'
    form = 'fixed'
    prec = 2
    show_commas = True
    strip_zeros = False

class Currency:
    def __init__(self, tokens, price=None, total=None):
        self.tokens = Quantity(tokens, self.UNITS)
        if total and price:
            raise Error('must not specify both total and price.', culprit=self.name())
        if not price:
            price = 0
        if total:
            price = total/abs(tokens)
        if price < 0:
            raise Error('price must not be negative.', culprit=self.name())
        self.price = Dollars(price)

    def in_tokens(self):
        return self.tokens

    def in_dollars(self, price=None):
        price = self.price if price is None else price
        return Dollars(self.tokens * price)

    def name(self):
        return self.__class__.__name__

    def __str__(self):
        return self.tokens.render()

    def __repr__(self):
        name = self.__class__.__name__
        if self.price:
            return f"{name}({self.tokens}, {self.price})"
        return f"{name}({self.tokens})"

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

class XLM(Currency):
    UNITS = 'XLM'
    NAME = 'Stellar Lumens'
    SYMBOL = '*'
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
        self.transactions = {}
        accounts[owner] = self
        self.totals = {}     # total value in dollars by token
        self.costs = {}      # total cost in dollars by token
        self.purchased = {}  # number of tokens actually purchased by token

    class Transaction:
        def __init__(self, tokens, date, comment, fees, source):
            self.tokens = tokens
            self.proceeds = tokens.in_dollars().scale(-1)
            self.date = date
            self.comment = comment
            self.fees = Dollars(fees)
            self.source = source
            self.tokens_reported = 0
            self.cost_basis = None

        def compute_cost_basis(self):
            source = self.source
            tokens = self.tokens
            date = self.date

            if source and type(source) != list:
                source = [source]

            if tokens.in_tokens() > 0:
                # this is a purchase
                if not source:
                    if self.proceeds == 0:
                        warn(
                            'purchase with no cost basis.',
                            culprit = self.ident()
                        )
                    self.cost_basis = self.proceeds.add(self.fees)
                    self.cost_basis_remaining = self.cost_basis
                    return

                # I'm not sure why this limitation exists
                # if self.proceeds != 0:
                #     raise Error(
                #         'cannot specify both an price and a source on a purchase.',
                #         culprit = self.ident()
                #     )

                basis = Dollars(0)
                for src in source:
                    try:
                        src, fraction = src
                    except TypeError:
                        fraction = 1
                    assert 0 <= fraction <= 1

                    if src.cost_basis is None:
                        raise Error(
                            f'source transaction ({src.ident()}) has no cost basis.',
                            culprit = self.ident()
                        )
                    if fraction:
                        if src.proceeds < 0:
                            raise Error(
                                f'a purchase ({src.ident()})',
                                'cannot be used as a source for a purchase.',
                                culprit = self.ident()
                            )
                        # if src.proceeds < 0:
                        #     raise Error(
                        #         f'using already reported asset ({src.ident()})',
                        #         'as source for purchase.',
                        #         culprit = self.ident()
                        #     )
                    cost_basis_used = src.cost_basis*fraction
                    basis = basis.add(cost_basis_used)
                    src.cost_basis_remaining = src.cost_basis_remaining.add(-cost_basis_used)
                self.cost_basis = basis.add(self.fees)
                self.cost_basis_remaining = self.cost_basis
                return

            # this is a sale
            tokens_to_consume = -tokens.in_tokens()
            basis = Dollars(0)
            if not source:
                source = []
            for src in source:
                try:
                    src, fraction = src
                except TypeError:
                    fraction = 1
                assert 0 <= fraction <= 1

                if fraction and src.proceeds > 0:
                    raise Error(
                        f'a sale ({src.ident()})',
                        'cannot be used as a source for a sale.',
                        culprit = self.ident()
                    )

                if tokens.name() != src.tokens.name():
                    raise Error(
                        'token type differs from source',
                        f'({src.tokens.name()}).',
                        culprit = self.ident()
                    )
                if tokens_to_consume <= 0:
                    warn(
                        f'unneeded source ({src.tokens.name()} {src.date}).',
                        culprit = self.ident()
                    )
                    break
                tokens_available = src.tokens_remaining()
                if tokens_to_consume <= tokens_available:
                    # take only tokens we need
                    tokens_consumed = tokens_to_consume
                    tokens_to_consume = 0
                else:
                    # take all remaining tokens
                    tokens_consumed = tokens_available
                    tokens_to_consume -= tokens_available
                src.tokens_reported += tokens_consumed
                if tokens_consumed:
                    cost_basis_used = src.cost_basis_remaining * (
                        tokens_consumed / tokens_available
                    )
                else:
                    cost_basis_used = 0
                basis = basis.add(cost_basis_used)
                src.cost_basis_remaining = src.cost_basis_remaining.add(-cost_basis_used)

            if tokens_to_consume > 0.001:
                # 0.001 is assumed negligible
                if source:
                    msg = (
                        'insufficient tokens available in',
                        f'{plural(source):source}',
                        f'(short by {tokens_to_consume}).'
                    )
                else:
                    msg = (f'sale without a source.',)
                warn(*msg, culprit = self.ident())
            elif tokens_to_consume < -0.001:
                raise AssertionError(f'overconsumed {tokens_to_consume}')
            else:
                self.cost_basis = basis.add(self.fees)
                self.cost_basis_remaining = self.cost_basis

            if self.proceeds:
                self.profit = self.proceeds
                if self.cost_basis:
                    self.profit = self.profit.add(-self.cost_basis)

        def fee(self):
            return Dollars(self.cost - self.tokens.in_dollars())

        def reported(self):
            return Dollars(self.tokens_reported * self.tokens.price)

        def tokens_remaining(self):
            return Quantity(
                float(self.tokens) - self.tokens_reported,
                self.tokens.tokens
            )

        def remaining(self):
            return Dollars(self.tokens_remaining * self.tokens.price)

        def ident(self):
            with Quantity.prefs(spacer=''):
                return ''.join(cull([self.tokens.name(), self.date])).lower()

        def __str__(self):
            return f'{self.date} {self.tokens}'

    def transaction(self, tokens, date=None, comment='', fees=0, source=None):
        t = self.Transaction(tokens, date, comment, fees, source)
        ident = t.ident()
        assert ident not in self.transactions, f'{ident} not unique'
        self.transactions[ident] = t
        kind = tokens.name()
        num_tokens = float(tokens)
        self.totals[kind] = Quantity(
            num_tokens + self.totals.get(kind, 0), units=tokens.UNITS
        )
        self.costs[kind] = Dollars(t.proceeds + self.costs.get(kind, 0))
        if t.proceeds > 0:
            self.purchased[kind] = Quantity(
                num_tokens + self.purchased.get(kind, 0), tokens.UNITS
            )
        return t

    def find_transaction(self, ident):
        try:
            return self.transactions[ident]
        except KeyError:
            matches = [k for k in self.transactions.keys() if k.startswith(ident)]
            if len(matches) == 1:
                return matches[0]
            elif matches:
                raise Error(
                    "transaction identifier is not unique, matches:",
                    *matches,
                    sep='\n    ',
                    culprit=ident,
                )
            raise Error('ident not found.', culprit=ident)

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
        return Dollars(total_dollars)

    def total_cost(self):
        "Total cost of tokens purchased in dollars."
        return Dollars(sum(self.costs.values()))

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
        return Dollars(max_dollars)

    def gen_csv(self, filename):
        import csv

        for t in self.transactions.values():
            try:
                t.compute_cost_basis()
            except Error as e:
                e.terminate()

        with open(filename, 'w', newline='') as csvfile:
            fieldnames = 'date coin amount price remaining total comment'.split()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            def add_row_to_totals(row):
                coin = row['coin']
                if coin not in totals:
                    totals[coin] = dict(amount=0, price=Dollars(0), total=Dollars(0))

                if row['amount']:
                    totals[coin]['amount'] += row['amount']
                if row['total']:
                    totals[coin]['total'] = totals[coin]['total'].add(Dollars(row['total']))
                if row['price']:
                    # first half of weighted average computation
                    totals[coin]['price'] = totals[coin]['price'].add(row['amount']*Dollars(row['price']))
            totals = {}

            writer.writeheader()
            for t in sorted(self.transactions.values(), key=lambda t: t.tokens.price):
                if t.tokens.name() != 'BTC':
                    continue
                remaining = t.tokens_remaining()
                total = t.tokens.in_dollars()
                row = dict(
                    date = f'{t.date[:2]} {t.date[2:4]} {t.date[4:6]} {t.date[6:]}',
                        # add spaces to dates so they cannot be confused with numbers
                        # without the dates without suffixes are treated as
                        # numbers, which fuxs up the sorting in Libre office
                        # can't use dashes, can't use slashes
                    coin = t.tokens.name(),
                    amount = round(float(t.tokens.in_tokens()), 8),
                    price = str(t.tokens.price) if t.tokens.price else '',
                    remaining = round(float(remaining), 8) if remaining >= 0 else '',
                    total = str(total) if total else '',
                    comment = dedent(t.comment, strip_nl='b'),
                )
                writer.writerow(row)
                add_row_to_totals(row)
            writer.writerow(dict())
            writer.writerow(dict(amount='total\ncoins', price='weighted\naverage', total='total\ninvested'))
            for coin in sorted(totals):
                row = totals[coin]
                # complete the weighted average computation
                row['price'] = Dollars(row['price']/row['amount'])
                writer.writerow({k: str(v) for k, v in row.items()})
