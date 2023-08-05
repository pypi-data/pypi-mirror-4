#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiagofrepereira@gmail.com>
# Thu Sep 13 11:06:19 CET 2012

import bob
import numpy

from . import *

"""
Implement the train flow to a SVM based countermeasure
"""

"""
Train the countermeasure
"""
def train(train_real, train_attack, normalize=False,pca_reduction=False,energy=0.99,copy=True,lowbound=-1, highbound=1):

  pcaMachine = None
  mins       = None #Normalization factor
  maxs       = None #Normalization factor

  if(copy):
    train_real   = numpy.copy(train_real)
    train_attack = numpy.copy(train_attack)

  if normalize:  # zero mean unit variance data normalziation
    train_data = numpy.concatenate((train_real, train_attack), axis=0) 
    mins, maxs = norm.calc_min_max(train_data)
    # normalization in the range [-1, 1] (recommended by LIBSVM)
    train_real = norm.norm_range(train_real, mins, maxs, lowbound, highbound); train_attack = norm.norm_range(train_attack, mins, maxs, lowbound, highbound)

  # PCA dimensionality reduction of the data
  if pca_reduction:
    train = [train_real,train_attack]
    pcaMachine = pca.make_pca(train, energy, False) # performing PCA
    train_real = pcareduce(pcaMachine, train_real); train_attack = pcareduce(pcaMachine, train_attack)

  #Running the SVM trainer
  svm_trainer = bob.trainer.SVMTrainer()
  svm_trainer.probability = True
  #svm_trainer.kernel_type = bob.machine.svm_kernel_type.LINEAR
  svmMachine = svm_trainer.train([train_real, train_attack])

  return [svmMachine,pcaMachine,mins,maxs]


"""
Compute the scores for one set of data
"""
def svm_predict(svm_machine, data):
  labels = numpy.array([svm_machine.predict_class_and_scores(x)[1][0] for x in data])
  return labels


"""
Compute scores
"""
def computeScores(train_real, train_attack,devel_real, devel_attack,test_real, test_attack, svmMachine,pcaMachine, normalize=False, copy=True,lowbound=-1, highbound=1,mins=[],maxs=[]):

  if(copy):
    train_real   = numpy.copy(train_real)
    train_attack = numpy.copy(train_attack)

    devel_real   = numpy.copy(devel_real)
    devel_attack = numpy.copy(devel_attack)
  
    test_real   = numpy.copy(test_real)
    test_attack = numpy.copy(test_attack)

  #Normalizing the data
  if(normalize):
    train_real = norm.norm_range(train_real, mins, maxs, lowbound, highbound)
    train_attack = norm.norm_range(train_attack, mins, maxs, lowbound, highbound)

    devel_real = norm.norm_range(devel_real, mins, maxs, lowbound, highbound)
    devel_attack = norm.norm_range(devel_attack, mins, maxs, lowbound, highbound)

    test_real = norm.norm_range(test_real, mins, maxs, lowbound, highbound)
    test_attack = norm.norm_range(test_attack, mins, maxs, lowbound, highbound)


  #Running PCA
  if(pcaMachine != None):
    train_real = pcareduce(pcaMachine, train_real); train_attack = pcareduce(pcaMachine, train_attack)
    devel_real = pcareduce(pcaMachine, devel_real); devel_attack = pcareduce(pcaMachine, devel_attack)
    test_real  = pcareduce(pcaMachine, test_real); test_attack   = pcareduce(pcaMachine, test_attack)


  #Computing the scores
  train_real_scores   = svm_predict(svmMachine, train_real)
  train_attack_scores = svm_predict(svmMachine, train_attack)

  devel_real_scores   = svm_predict(svmMachine, devel_real)
  devel_attack_scores = svm_predict(svmMachine, devel_attack)

  test_real_scores    = svm_predict(svmMachine, test_real)
  test_attack_scores  = svm_predict(svmMachine, test_attack)


  # it is expected that the scores of the real accesses are always higher then the scores of the attacks. Therefore, a check is first made, if the   average of the scores of real accesses is smaller then the average of the scores of the attacks, all the scores are inverted by multiplying with -1.
  if numpy.mean(devel_real_scores) < numpy.mean(devel_attack_scores):
    train_real_scores = train_real_scores * -1; train_attack_scores = train_attack_scores * -1
    devel_real_scores = devel_real_scores * -1; devel_attack_scores = devel_attack_scores * -1
    test_real_scores = test_real_scores * -1; test_attack_scores = test_attack_scores * -1

  return [train_real_scores,train_attack_scores,devel_real_scores,devel_attack_scores,test_real_scores,test_attack_scores]


"""
Write the normalization file for SVM classification
"""
def writeNormalizationData(fileName,lowbound,highbound,mins,maxs):
  hdf5File = bob.io.HDF5File(fileName, openmode_string='w')
  hdf5File.append('lowbound',lowbound)
  hdf5File.append('highbound',highbound)
  hdf5File.append('mins',mins)
  hdf5File.append('maxs',maxs)
  del hdf5File


"""
Load the normalization file for SVM classification
"""
def readNormalizationData(fileName):
  
  #Opening HDF5 Files
  hdf5 = bob.io.HDF5File(fileName, openmode_string='r')
  lowbound  = hdf5.read('lowbound')
  highbound = hdf5.read('highbound')
  mins      = hdf5.read('mins')
  maxs      = hdf5.read('maxs')

  return [lowbound,highbound,mins,maxs]




