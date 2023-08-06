#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#
# Author:   lambdalisue (lambdalisue@hashnote.net)
# URL:      http://hashnote.net/
# License:  MIT license
# Created:  2013-01-23
#
from utils import create_formula


def fit(data, model, criterions, opts):
    print "# N = %d, Bins = %d, Base = %.2e" % (
            len(data), opts.bins, opts.base)
    print "n_components_try = %d, n_components_best = %d" % (
            len(criterions[0]),
            len(model.weights_),
        )
    
    for i in range(len(model.weights_)):
        formula = create_formula(data, model, i)
        print formula
    return data, model, criterions, opts


def histogram(data, model, criterions, opts):
    from numpy import histogram
    print "# N = %d, Bins = %d, Base = %.2e" % (
            len(data), opts.bins, opts.base)
    hist, bin_edges = histogram(data, bins=opts.bins)
    for index in range(len(hist)):
        print bin_edges[index], hist[index]
    return data, model, criterions, opts
