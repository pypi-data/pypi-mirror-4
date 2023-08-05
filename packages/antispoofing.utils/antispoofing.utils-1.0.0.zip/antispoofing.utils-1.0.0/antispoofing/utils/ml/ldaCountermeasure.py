#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiagofrepereira@gmail.com>
# Wed Sep 12 11:43:19 CET 2012

import bob
import numpy

from . import *

"""
Implement the train flow to a LDA based countermeasure
"""

"""
Train the countermeasure
"""
def train(train_real, train_attack, normalize=False,pca_reduction=False,energy=0.99,copy=True):

  pcaMachine = None

  if(copy):
    train_real   = numpy.copy(train_real)
    train_attack = numpy.copy(train_attack)

  if normalize:  # zero mean unit variance data normalziation
    mean, std = calc_mean_std(train_real, train_attack,nonStdZero=True)
    mean = numpy.double(mean)
    std = numpy.double(std)

  # PCA dimensionality reduction of the data
  if pca_reduction:
    dataPCA = numpy.concatenate((train_real,train_attack),axis=0)
    pcaMachine = pca.make_pca(dataPCA, energy, False) # performing PCA

    #Storing the normaliation factors in PCA machine
    if normalize:
      pcaMachine.input_subtract = mean
      pcaMachine.input_divide = std

    train_real = pcareduce(pcaMachine, train_real); train_attack = pcareduce(pcaMachine, train_attack)

  train = [train_real,train_attack]

  ldaMachine = make_lda(train) # training the LDA
  ldaMachine.shape = (ldaMachine.shape[0], 1) #only use first component!

  #Storing the normaliation factors in Linear machine
  if(not pca_reduction and normalize):
    ldaMachine.input_subtract = mean
    ldaMachine.input_divide   = std

  return [ldaMachine,pcaMachine]



"""
Compute scores
"""
def computeScores(train_real, train_attack,devel_real, devel_attack,test_real, test_attack, ldaMachine,pcaMachine, copy=True):

  if(copy):
    train_real   = numpy.copy(train_real)
    train_attack = numpy.copy(train_attack)

    devel_real   = numpy.copy(devel_real)
    devel_attack = numpy.copy(devel_attack)
  
    test_real   = numpy.copy(test_real)
    test_attack = numpy.copy(test_attack)

  if(pcaMachine != None):
    train_real = pcareduce(pcaMachine, train_real); train_attack = pcareduce(pcaMachine, train_attack)
    devel_real = pcareduce(pcaMachine, devel_real); devel_attack = pcareduce(pcaMachine, devel_attack)
    test_real  = pcareduce(pcaMachine, test_real); test_attack   = pcareduce(pcaMachine, test_attack)


  train_real_scores   = get_scores(ldaMachine, train_real)
  train_attack_scores = get_scores(ldaMachine, train_attack)

  devel_real_scores   = get_scores(ldaMachine, devel_real)
  devel_attack_scores = get_scores(ldaMachine, devel_attack)

  test_real_scores    = get_scores(ldaMachine, test_real)
  test_attack_scores  = get_scores(ldaMachine, test_attack)

  # it is expected that the scores of the real accesses are always higher then the scores of the attacks. Therefore, a check is first made, if the   average of the scores of real accesses is smaller then the average of the scores of the attacks, all the scores are inverted by multiplying with -1.
  if numpy.mean(devel_real_scores) < numpy.mean(devel_attack_scores):
    train_real_scores = train_real_scores * -1; train_attack_scores = train_attack_scores * -1
    devel_real_scores = devel_real_scores * -1; devel_attack_scores = devel_attack_scores * -1
    test_real_scores = test_real_scores * -1; test_attack_scores = test_attack_scores * -1


  return [train_real_scores,train_attack_scores,devel_real_scores,devel_attack_scores,test_real_scores,test_attack_scores]

