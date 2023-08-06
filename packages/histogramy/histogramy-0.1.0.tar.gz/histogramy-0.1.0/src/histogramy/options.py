#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#
# Author:   lambdalisue (lambdalisue@hashnote.net)
# URL:      http://hashnote.net/
# License:  MIT license
# Created:  2013-01-23
#
import sys
import argparse
from decimal import Decimal
import prefix
import describer


ONE = Decimal(1)
LEGEND_LOCATIONS = (
    'upper right',
    'upper left',
    'lower left',
    'lower right',
    'right',
    'center left',
    'center right',
    'lower center',
    'upper center',
    'center',
)


def plot(data, model, criterions, opts):
    import plotter
    return plotter.plot(data, model, criterions, opts)


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--bins', default=10, type=int, metavar='BINS',
        help='It defines the number of equal-width bins.')
    parser.add_argument('-c', '--column', default=0, type=int, metavar='N',
        help='A number of column in data file used for analysis')
    parser.add_argument('-C', '--classifiers', default=10, type=int,
        metavar='N',
        help='The maximum number classifiers to simulate the fitting')
    parser.add_argument('--base', default=Decimal('1'), metavar='BASE',
        help='Base value to modulate the data')
    parser.add_argument('--auto-base', default=False, action='store_false',
        help='Automatically find the base value to modulate the data')
    parser.add_argument('--min-threshold', metavar='MIN', type=Decimal,
        help='Minimum threshold. Value smaller than this will be ignored')
    parser.add_argument('--max-threshold', metavar='MAX', type=Decimal,
        help='Maximum threshold. Value grater than this will be ignored')
    parser.add_argument('--covariance-type', default='diag', metavar='TYPE',
        help='Type of covariance. Default is "diag"')
    parser.add_argument('--min-covar', default=1e-3, type=float,
        metavar='MIN_COVAR',
        help='Minimum value of covariance')
    parser.add_argument('--delimiter', default=',', metavar='DELIMITER',
        help='Delimiter used to parse the data file')
    parser.add_argument('--encoding', default='utf-8', metavar='ENCODING',
        help='Encoding used to open the data file')
    parser.add_argument('--demo', default=False, action='store_true',
        help='Use demo data to analysis')
    parser.add_argument('filenames', default=[], nargs='*')

    # subparsers
    sp = parser.add_subparsers()

    # create the subparser for the 'histogram' command
    parser_histogram = sp.add_parser('histogram',
        help='Show histogram data')
    parser_histogram.set_defaults(func=describer.histogram)
    # create the subparser for the 'fit' command
    parser_fit = sp.add_parser('fit',
        help='Show fitting data')
    parser_fit.set_defaults(func=describer.fit)
    # create the subparser for the 'plot' command
    parser_plot = sp.add_parser('plot',
        help='Create graph by matplotlib')
    parser_plot.add_argument('-o', '--output', metavar='FILE',
        help='Export the graph as a PNG image to the FILE')
    parser_plot.add_argument('--graph-width', default=8, type=int,
        help='The width (inch) of the graph')
    parser_plot.add_argument('--graph-height', default=6, type=int,
        help='The height (inch) of the graph')
    parser_plot.add_argument('--graph-dpi', default=100, type=int,
        help='The DPI of the graph')
    parser_plot.add_argument('--graph-facecolor', default='white',
        help='The face color of the graph')
    parser_plot.add_argument('--graph-edgecolor', default='#3d3d3d',
        help='The edge color of the graph')
    parser_plot.add_argument('--graph-textcolor', default='#3d3d3d',
        help='The text color of the graph')
    # histogram
    parser_plot.add_argument('--histogram-type',
        default='stepfilled',
        choices=['bar', 'barstacked', 'step', 'stepfilled'],
        help='The type of histogram to draw')
    parser_plot.add_argument('--histogram-color',
        default='#6a8cc7', metavar='COLOR',
        help='The color of histogram to draw')
    parser_plot.add_argument('--histogram-edgecolor',
        default='#3261ab', metavar='COLOR',
        help='The edge color of histogram to draw')
    parser_plot.add_argument('--histogram-linewidth',
        default=1, type=int,
        help='The edge width of histogram to draw')
    parser_plot.add_argument('--histogram-alpha', type=float,
        default=1.0, metavar='ALPHA',
        help='The transparency of histogram to draw')
    parser_plot.add_argument('--histogram-xlabel',
        default='X', metavar='LABEL',
        help='The label of histogram X axis')
    parser_plot.add_argument('--histogram-ylabel',
        default='Count', metavar='LABEL',
        help='The label of histogram Y axis')
    parser_plot.add_argument('--histogram-xmin', type=float,
        metavar='MIN',
        help='The minimum value of histogram X axis to draw')
    parser_plot.add_argument('--histogram-xmax', type=float,
        metavar='MAX',
        help='The maximum value of histogram X axis to draw')
    parser_plot.add_argument('--histogram-ymin', type=float,
        metavar='MIN',
        help='The minimum value of histogram Y axis to draw')
    parser_plot.add_argument('--histogram-ymax', type=float,
        metavar='MAX',
        help='The maximum value of histogram Y axis to draw')
    parser_plot.add_argument('--histogram-legend',
        choices=LEGEND_LOCATIONS, nargs='?', const='upper left',
        help='The location of the histogram legend')
    # fitting
    parser_plot.add_argument('--no-fitting', dest='draw_fitting',
        default=True, action='store_false',
        help='Do not draw fitting curves')
    parser_plot.add_argument('--fitting-style',
        default='-', metavar='STYLE',
        help='The style of fitting curve to draw')
    parser_plot.add_argument('--fitting-color',
        default='#c7243a', metavar='COLOR',
        help='The color of fitting curve to draw')
    parser_plot.add_argument('--fitting-alpha', type=float,
        default=0.8, metavar='ALPHA',
        help='The transparency of fitting curve to draw')
    parser_plot.add_argument('--fitting-linewidth',
        default=1, type=int,
        help='The line width of fitting curve to draw')
    parser_plot.add_argument('--fitting-style-individual',
        default='--k', metavar='STYLE',
        help='The style of individual fitting curve to draw')
    parser_plot.add_argument('--fitting-color-individual',
        default='black', metavar='COLOR',
        help='The color of individual fitting curve to draw')
    parser_plot.add_argument('--fitting-alpha-individual', type=float,
        default=0.7, metavar='ALPHA',
        help='The transparency of individual fitting curve to draw')
    parser_plot.add_argument('--fitting-linewidth-individual',
        default=2, type=int,
        help='The line width of individual fitting curve to draw')
    parser_plot.add_argument('--fitting-ylabel',
        default='Probability', metavar='LABEL',
        help='The label of fitting curve Y axis')
    parser_plot.add_argument('--fitting-label',
        default='Fitting curve', metavar='LABEL',
        help='The legend label of fitting curve')
    parser_plot.add_argument('--fitting-ymin', type=float,
        metavar='MIN',
        help='The minimum value of fitting curve Y axis to draw')
    parser_plot.add_argument('--fitting-ymax', type=float,
        metavar='MAX',
        help='The maximum value of fitting curve Y axis to draw')
    parser_plot.add_argument('--fitting-legend',
        choices=LEGEND_LOCATIONS, nargs='?', const='upper right',
        help='The location of the fitting curve legend')
    # criterions
    parser_plot.add_argument('--criterions', dest='draw_criterions',
        default=False, action='store_true',
        help='Plot AIC and BIC values of each # of components in subfigure')
    parser_plot.add_argument('--criterions-xlabel',
        default='# of components', metavar='LABEL',
        help='The label of criterions graph X axis')
    parser_plot.add_argument('--criterions-style-aic',
        default='-k', metavar='STYLE',
        help='The style of AIC to draw')
    parser_plot.add_argument('--criterions-alpha-aic', type=float,
        default=1.0, metavar='ALPHA',
        help='The transparency of AIC to draw')
    parser_plot.add_argument('--criterions-style-bic',
        default='--k', metavar='STYLE',
        help='The style of BIC to draw')
    parser_plot.add_argument('--criterions-alpha-bic', type=float,
        default=1.0, metavar='ALPHA',
        help='The transparency of BIC to draw')
    parser_plot.set_defaults(func=plot)

    opts = parser.parse_args(args)

    # delimiter can be specified as SPACE, TAB, \s, \t
    delimiter = opts.delimiter.lower()
    if delimiter in ('space', '\\s'):
        opts.delimiter = ' '
    elif delimiter in ('tab', '\\t'):
        opts.delimiter = '\t'
    # convert SI Prefix to Decimal
    if isinstance(opts.base, basestring):
        # SI Prefix -> Decimal
        ps = list(prefix.NEGATIVES) + list(prefix.POSITIVES)
        ps = dict(ps)
        opts.base = ps.get(opts.base, ONE)

    return opts
