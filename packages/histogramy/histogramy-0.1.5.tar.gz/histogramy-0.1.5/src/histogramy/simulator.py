#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#
# Author:   lambdalisue (lambdalisue@hashnote.net)
# URL:      http://hashnote.net/
# License:  MIT license
# Created:  2013-01-23
#
from numpy import zeros, argmin
from sklearn.mixture import GMM


def fit(data, n_components, covariance_type='diag', min_covar=1e-3):
    # create n_components of GMM
    models = zeros(n_components, dtype=object)
    for i in range(n_components):
        kwargs = dict(
            covariance_type=covariance_type,
            min_covar=min_covar)
        models[i] = GMM(i+1, **kwargs).fit(data)

    # calculate AIC, BIC
    AIC = [m.aic(data) for m in models]
    BIC = [m.bic(data) for m in models]
    # find best match by AIC
    best = models[argmin(AIC)]
    return best, (AIC, BIC)
