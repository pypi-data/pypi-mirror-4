# encoding=UTF-8
from decimal import Decimal, ROUND_UP

from pymonon.currencies import CURRENCIES_CODES

__version__ = '0.0.1-dev'


class CurrencyError(Exception):
    pass


class Currency(object):
    def __init__(self, code, name=None, symbol=u'$', decimals=2):
        self.code = code.upper()
        self.name = name
        self.symbol = symbol
        self.decimals = decimals

    def __eq__(self, other):
        return self.code == other.code

    @staticmethod
    def get_default():
        return DEFAULT_CURRENCY

    @staticmethod
    def normalize_currency(currency):
        if currency is None:
            currency = Currency.get_default()
        elif isinstance(currency, Currency):
            currency = currency
        elif isinstance(currency, basestring) and currency.upper() in CURRENCIES:
            currency = CURRENCIES[currency.upper()]
        else:
            raise CurrencyError('Currency does not exist.')
        return currency

    def __unicode__(self):
        return unicode(self.symbol)

    def __repr__(self):
        return self.code


class Money(object):
    def __init__(self, amount, currency=None):
        self.currency = Currency.normalize_currency(currency)
        self.amount = self.quantize_amount(amount, self.currency)

    @staticmethod
    def quantize_amount(amount, currency):
        places = Decimal(10) ** (- currency.decimals)
        return Decimal(amount).quantize(places, rounding=ROUND_UP)

    def __cmp__(self, other):
        if not other:
            other = Money(0, self.currency)
        if not isinstance(other, Money):
            raise TypeError("You can only compare Money instances.")
        assert self.currency == other.currency, "Currency mismatch."

        return self.amount - other.amount

    def __add__(self, other):
        if not isinstance(other, Money):
            raise TypeError("You can only add Money instances.")
        assert self.currency == other.currency, "Currency mismatch."

        amount = self.amount + other.amount
        return Money(amount, currency=self.currency)

    def __sub__(self, other):
        if not isinstance(other, Money):
            raise TypeError("You can only substract Money instances.")
        assert self.currency == other.currency, "Currency mismatch."

        amount = self.amount - other.amount
        return Money(amount, currency=self.currency)

    def __mul__(self, other):
        if isinstance(other, Money):
            raise TypeError("You cannot multiply Money values.")
        amount = self.amount * Decimal(other)
        return Money(amount, currency=self.currency)

    def __div__(self, other):
        if isinstance(other, Money):
            raise TypeError("You cannot divide Money values.")
        amount = self.amount / Decimal(other)
        return Money(amount, currency=self.currency)

    def __unicode__(self):
        return u'%s%s' % (self.currency.symbol, self.amount)

    def __repr__(self):
        return '%s %s' % (self.currency.code, self.amount)


def set_default_currency(currency):
    global DEFAULT_CURRENCY
    add_currency(currency)
    DEFAULT_CURRENCY = currency


def add_currency(currency):
    global CURRENCIES
    CURRENCIES.update({
        currency.code: currency
    })

CURRENCIES = {}
for name, code, symbol, decimals in CURRENCIES_CODES:
    add_currency(Currency(code=code, name=name, symbol=symbol, decimals=decimals))

DEFAULT_CURRENCY = CURRENCIES['USD']
