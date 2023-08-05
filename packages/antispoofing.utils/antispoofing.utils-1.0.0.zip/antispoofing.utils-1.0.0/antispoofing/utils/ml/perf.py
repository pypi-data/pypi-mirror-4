#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Wed 17 Aug 11:42:09 2011 

"""A few utilities to plot and dump results.
"""

import os
import bob
import numpy
import re

def pyplot_axis_fontsize(ax, size):
  """Sets the font size on axis labels"""

  for label in ax.xaxis.get_ticklabels():
    label.set_fontsize(size)
  for label in ax.yaxis.get_ticklabels():
    label.set_fontsize(size)

def score_distribution_plot(test, devel, train, bins, thres,scoresRange=(-5,5),title=""):
  """Plots the score distributions in 3 different subplots"""

  import matplotlib.pyplot as mpl
  histoargs = {'bins': bins, 'alpha': 0.8, 'histtype': 'step', 'range': scoresRange} 
  lineargs = {'alpha': 0.5}
  axis_fontsize = 8

  # 3 plots (same page) with the tree sets
  mpl.subplot(3,1,1)
  
  mpl.hist(test[0], label='Real Accesses', color='g', **histoargs)
  mpl.hist(test[1], label='Attacks', color='b', **histoargs)
  xmax, xmin, ymax, ymin = mpl.axis()
  mpl.vlines(thres, ymin, ymax, color='red', label='EER', 
      linestyles='solid', **lineargs)
  mpl.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
       ncol=4, mode="expand", borderaxespad=0.)
  mpl.grid(True, alpha=0.5)
  mpl.ylabel("Test set")
  axis = mpl.gca()
  axis.yaxis.set_label_position('right')
  pyplot_axis_fontsize(axis, axis_fontsize)
  mpl.subplot(3,1,2)
  mpl.hist(devel[0], color='g', **histoargs)
  mpl.hist(devel[1], color='b', **histoargs)
  xmax, xmin, ymax, ymin = mpl.axis()
  mpl.vlines(thres, ymin, ymax, color='red', linestyles='solid',
      label='EER', **lineargs)
  mpl.grid(True, alpha=0.5)
  mpl.ylabel("Development set")
  axis = mpl.gca()
  axis.yaxis.set_label_position('right')
  pyplot_axis_fontsize(axis, axis_fontsize)
  mpl.subplot(3,1,3)
  mpl.hist(train[0], color='g', **histoargs)
  mpl.hist(train[1], color='b', **histoargs)
  xmax, xmin, ymax, ymin = mpl.axis()
  mpl.vlines(thres, ymin, ymax, color='red', linestyles='solid', 
      label='EER', **lineargs)
  mpl.grid(True, alpha=0.5)
  mpl.ylabel("Training set")
  mpl.xlabel("Score distribution " + title) 
  axis = mpl.gca()
  axis.yaxis.set_label_position('right')

  pyplot_axis_fontsize(axis, axis_fontsize)


def perf_hter(test_scores, devel_scores, threshold_func):
  """Computes a performance table and returns the HTER for the test and
  development set, as well as a formatted text with the results and the value
  of the threshold obtained for the given threshold function

  Keyword parameters:

    test_scores
      the scores of the samples in the test set
    devel_scores
      the scores of the samples in the development set
    threshold function
      the type of threshold
  """ 
   
  from bob.measure import farfrr

  devel_attack_scores = devel_scores[1]
  devel_real_scores = devel_scores[0]
  test_attack_scores = test_scores[1]
  test_real_scores = test_scores[0]

  devel_real = devel_real_scores.shape[0]
  devel_attack = devel_attack_scores.shape[0]
  test_real = test_real_scores.shape[0]
  test_attack = test_attack_scores.shape[0]

  thres = threshold_func(devel_attack_scores, devel_real_scores)
  devel_far, devel_frr = farfrr(devel_attack_scores, devel_real_scores, thres)
  test_far, test_frr = farfrr(test_attack_scores, test_real_scores, thres)
  devel_hter = 50 * (devel_far + devel_frr)
  test_hter = 50 * (test_far + test_frr)
  devel_text = " d: FAR %.2f%% / FRR %.2f%% / HTER %.2f%% " % (100*devel_far, 100*devel_frr, devel_hter)
  test_text = " t: FAR %.2f%% / FRR %.2f%% / HTER %.2f%% " % (100*test_far, 100*test_frr, test_hter)
  return (test_hter, devel_hter), (test_text, devel_text), thres
