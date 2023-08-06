#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#
# Author:   lambdalisue (lambdalisue@hashnote.net)
# URL:      http://hashnote.net/
# License:  MIT license
# Created:  2013-01-23
#
import random
import numpy as np
from decimal import Decimal
from sklearn.mixture import GMM


def demo():
    np.random.seed(1)
    gmm = GMM(3, n_iter=1)
    gmm.means_ = np.array([[-1], [0], [3]])
    gmm.covars_ = np.array([[1.5], [1], [0.5]]) ** 2
    gmm.weights_ = np.array([0.3, 0.5, 0.2])
    return gmm.sample(1000)
