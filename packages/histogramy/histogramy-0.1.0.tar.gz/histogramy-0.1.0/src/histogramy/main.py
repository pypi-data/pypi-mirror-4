#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#
# Author:   lambdalisue (lambdalisue@hashnote.net)
# URL:      http://hashnote.net/
# License:  MIT license
# Created:  2013-01-23
#
import sys
from numpy import concatenate

from demo import demo
from loader import load
from simulator import fit
from modulator import modulate_base
from options import parse_args


def analyze(opts):
    # use sys.stdin insted if no filename is specified
    if len(opts.filenames) == 0:
        opts.filenames.append(sys.stdin)

    if opts.demo:
        data = [demo(), demo(), demo()]
    else:
        # load data file
        data = [load(f, opts) for f in opts.filenames]
    # transform to 1-dimensional array
    data = concatenate(data, axis=0)

    # modulate the data with base
    data = modulate_base(data, opts.base)

    # convert Decimal to float

    # remove data with threshold
    if opts.min_threshold:
        data = data[data>opts.min_threshold]
    if opts.max_threshold:
        data = data[data<opts.max_threshold]

    # fitting
    kwargs = dict(
        n_components=opts.classifiers,
        covariance_type=opts.covariance_type,
        min_covar=opts.min_covar)
    model, criterions = fit(data, **kwargs)

    # call function
    return opts.func(data, model, criterions, opts)


def main(args=None):
    # parse args
    opts = parse_args(args)
    # analyze
    result = analyze(opts)

    if opts.func.__name__ == 'plot':
        # result = pyplot
        if opts.output:
            result.savefig(opts.output)
        else:
            try:
                result.show()
            except KeyboardInterrupt:
                exit(0)


if __name__ == '__main__':
    main()
