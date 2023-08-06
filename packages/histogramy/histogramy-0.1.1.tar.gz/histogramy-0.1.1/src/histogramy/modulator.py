#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#
# Author:   lambdalisue (lambdalisue@hashnote.net)
# URL:      http://hashnote.net/
# License:  MIT license
# Created:  2013-01-23
#
from decimal import Decimal
from numpy import vectorize

import prefix

ONE = Decimal('1')

def flatten(l):
    if isinstance(l, (list, tuple)):
        return reduce(lambda a,b: a + flatten(b), l, [])
    else:
        return [l]


def modulate_base(value, base=ONE):
    if not isinstance(base, Decimal):
        base = Decimal(base)
    return Decimal(value) / base
modulate_base = vectorize(modulate_base)

def to_float(value):
    return float(value)
to_float = vectorize(to_float)
