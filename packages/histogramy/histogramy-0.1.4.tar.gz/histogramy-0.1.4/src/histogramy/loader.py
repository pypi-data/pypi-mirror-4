#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#
# Author:   lambdalisue (lambdalisue@hashnote.net)
# URL:      http://hashnote.net/
# License:  MIT license
# Created:  2013-01-23
#
import re
import codecs
import numpy as np
from decimal import Decimal


def parse(data, column=0, delimiter=','):
    def _parse():
        for line in data:
            columns = line.split(delimiter)
            value = Decimal(columns[column])
            yield value
    return [x for x in _parse()]


def read(filename, encoding='utf-8', remove_pattern=r'#.*$'):
    def _read():
        if isinstance(filename, basestring):
            f = codecs.open(filename, 'r', encoding)
        else:
            f = filename    # stdin?
        for line in f:
            line = remove_pattern.sub('', line).strip()
            if line == '':
                continue
            yield line
    if isinstance(remove_pattern, basestring):
        remove_pattern = re.compile(remove_pattern)
    return [x for x in _read()]


def load(filename, opts):
    data = read(filename, opts.encoding)
    data = parse(data, opts.column, opts.delimiter)
    return np.array(data)
