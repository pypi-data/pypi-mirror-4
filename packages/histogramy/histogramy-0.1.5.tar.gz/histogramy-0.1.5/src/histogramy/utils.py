#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#
# Author:   lambdalisue (lambdalisue@hashnote.net)
# URL:      http://hashnote.net/
# License:  MIT license
# Created:  2013-01-23
#
from numpy import sqrt
MICRO = u"\u00b5"
SIGMA = u"\u03c3"
PLMIN = u"\u00b1"


def create_formula(X, model, index=0):
    w = model.weights_[index]
    m = model.means_[index][0]
    c = model.covars_[index][0]  # covariance = variance in 1-dimension
    d = sqrt(c)                  # SD = sqrt(variance)
    e = d / sqrt(len(X))         # SE = SD / sqrt(N)
    f = "%.2f%%: %s=%.2e%s%.2e, %s=%.2e"
    f = f % (w * 100, MICRO, m, PLMIN, e, SIGMA, d)
    return f
