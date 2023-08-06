#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#
# Author:   lambdalisue (lambdalisue@hashnote.net)
# URL:      http://hashnote.net/
# License:  MIT license
# Created:  2013-01-23
#
from decimal import Decimal

ONE = Decimal('1')
NEGATIVES = (
    ('y',    Decimal('1e-24')),
    ('z',    Decimal('1e-21')),
    ('a',    Decimal('1e-18')),
    ('f',    Decimal('1e-15')),
    ('p',    Decimal('1e-12')),
    ('n',    Decimal('1e-09')),
    ('u',    Decimal('1e-06')),
    ('m',    Decimal('1e-03')),
    ('c',    Decimal('1e-02')),
    ('d',    Decimal('1e-01')),
)
POSITIVES = (
    ('Y',    Decimal('1e+24')),
    ('Z',    Decimal('1e+21')),
    ('E',    Decimal('1e+18')),
    ('P',    Decimal('1e+15')),
    ('T',    Decimal('1e+12')),
    ('G',    Decimal('1e+09')),
    ('M',    Decimal('1e+06')),
    ('k',    Decimal('1e+03')),
    ('h',    Decimal('1e+02')),
    ('da',   Decimal('1e+01')),
)

def get_prefix(value):

    if not isinstance(value, Decimal):
        value = Decimal(value)
    abs_value = abs(value)
    if abs_value > ONE:
        for (prefix, threshold) in POSITIVES:
            if threshold <= abs_value:
                return value / threshold, prefix
    elif abs_value < ONE:
        previous_prefix = ''
        previous_threshold = Decimal(0)
        for (prefix, threshold) in NEGATIVES:
            if threshold > abs_value:
                return value / previous_threshold, previous_prefix
            previous_prefix = prefix
            previous_threshold = threshold
    return value, ''


if __name__ == '__main__':
    assert get_prefix(Decimal('1000')) == (ONE, 'k')
    assert get_prefix(Decimal('0.001')) == (ONE, 'm')
    assert get_prefix(Decimal('-4e+25')) == (Decimal('-40'), 'Y')
    assert get_prefix(Decimal('-2e-23')) == (Decimal('-20'), 'y')
