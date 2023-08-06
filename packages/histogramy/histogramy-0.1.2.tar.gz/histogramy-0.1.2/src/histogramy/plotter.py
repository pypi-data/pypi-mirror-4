#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#
# Author:   lambdalisue (lambdalisue@hashnote.net)
# URL:      http://hashnote.net/
# License:  MIT license
# Created:  2013-01-23
#
from numpy import min, max, exp
from numpy import newaxis, linspace, arange
from matplotlib import pyplot, mpl
from utils import create_formula


def get(value, default_value):
    if value is None:
        return default_value
    return value


def plot(data, model, criterions, opts):
    mpl.rcParams['text.color'] = opts.graph_textcolor
    mpl.rcParams['axes.facecolor'] = opts.graph_facecolor
    mpl.rcParams['axes.edgecolor'] = opts.graph_edgecolor
    mpl.rcParams['axes.labelcolor'] = opts.graph_textcolor
    mpl.rcParams['xtick.color'] = opts.graph_edgecolor
    mpl.rcParams['ytick.color'] = opts.graph_edgecolor
    mpl.rcParams['grid.color'] = opts.graph_edgecolor
    mpl.rcParams['legend.fancybox'] = True

    fig = pyplot.figure(
            figsize=(opts.graph_width, opts.graph_height),
            dpi=opts.graph_dpi)
    
    # plot histogram
    if opts.draw_criterions:
        ax = fig.add_subplot(211)
    else:
        ax = fig.add_subplot(111)
    plot_histogram(ax, data, opts)
    if opts.histogram_legend:
        ax.legend(loc=opts.histogram_legend, prop={'size':
            opts.histogram_legend_size})
    # plot fitting curve
    if opts.draw_fitting:
        ax = ax.twinx()
        plot_fitting(ax, data, model, opts)
        if opts.fitting_legend:
            ax.legend(loc=opts.fitting_legend, prop={'size':
                opts.fitting_legend_size})
    # plot criterions
    if opts.draw_criterions:
        ax = fig.add_subplot(212)
        plot_criterions(ax, criterions, opts)
        ax.legend()
    return pyplot


def plot_histogram(axis, data, opts):
    # configure axis
    axis.set_xlabel(opts.histogram_xlabel)
    axis.set_ylabel(opts.histogram_ylabel)

    # plot
    n, bins, patches = axis.hist(data,
        bins=opts.bins,
        histtype=opts.histogram_type,
        color=opts.histogram_color,
        edgecolor=opts.histogram_edgecolor,
        alpha=opts.histogram_alpha,
        linewidth=opts.histogram_linewidth,
        label='Histogram (N = %d, bin = %d)' % (len(data), opts.bins))

    # limit x viewport
    xmin, xmax = axis.get_xlim()
    xmin = get(opts.histogram_xmin, xmin)
    xmax = get(opts.histogram_xmax, xmax)
    axis.set_xlim(xmin, xmax)
    # limit y viewport
    ymin, ymax = min(n), (max(n) * 1.2)
    ymin = get(opts.histogram_ymin, ymin)
    ymax = get(opts.histogram_ymax, ymax)
    axis.set_ylim(ymin, ymax)


def plot_fitting(axis, data, model, opts):
    # configure axis
    axis.set_ylabel(opts.fitting_ylabel)

    # create plot data
    x = linspace(min(data, axis=0), max(data, axis=0), 1000)
    logprob, responsibilities = model.fit(data).eval(x)
    pdf = exp(logprob)
    pdf_individual = responsibilities * pdf[:, newaxis]
    # plot fitting curve
    axis.plot(x, pdf, opts.fitting_style, 
            color=opts.fitting_color,
            linewidth=opts.fitting_linewidth,
            alpha=opts.fitting_alpha,
            label=opts.fitting_label)
    # plot individual fitting curve
    for i in range(0, len(model.weights_)):
        formula = create_formula(data, model, i)
        pdf = pdf_individual[:,i]
        axis.plot(x, pdf, opts.fitting_style_individual,
                color=opts.fitting_color_individual,
                linewidth=opts.fitting_linewidth_individual,
                alpha=opts.fitting_alpha_individual,
                label=formula)

    # remove yticks
    axis.get_yaxis().set_visible(False)

    # limit x viewport
    xmin, xmax = axis.get_xlim()
    xmin = get(opts.histogram_xmin, xmin)
    xmax = get(opts.histogram_xmax, xmax)
    axis.set_xlim(xmin, xmax)
    # limit y viewport
    ymin, ymax = axis.get_ylim()
    ymin = get(opts.fitting_ymin, ymin)
    ymax = get(opts.fitting_ymax, ymax)
    axis.set_ylim(ymin, ymax)


def plot_criterions(axis, criterions, opts):
    AIC, BIC = criterions

    # configure axis
    axis.set_xlabel(opts.criterions_xlabel)

    # plot criterions
    x = arange(1, len(AIC) + 1)
    axis.plot(x, AIC, opts.criterions_style_aic, 
            label='AIC', alpha=opts.criterions_alpha_aic)
    axis.plot(x, BIC, opts.criterions_style_bic,
            label='BIC', alpha=opts.criterions_alpha_bic)
