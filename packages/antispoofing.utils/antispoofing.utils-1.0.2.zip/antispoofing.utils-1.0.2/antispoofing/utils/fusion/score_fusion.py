#!/usr/bin/env python
#Tiago de Freitas Pereira <tiagofrepereira@gmail.com>
#Oct 01 20:50:00 CEST 2012

"""
This script run the score fusion

"""

import bob
import numpy

from antispoofing.utils.helpers import *
from antispoofing.utils.ml import *

class ScoreFusion:
  """
  Class that run different Score level fusion with different normalization score algorithm
  """

  def __init__(self,scoreNormalizationAlg=None,realScoreReader=None,attackScoreReader=None):
    """
    Constructor

    @param scoresNormalization Name of the score Normalizatio algorithm (TODO: THIS IS CRAP. PLEASE THINK IN A BETTER SOLUTION)

    @param scoresReaderRealAccess ScoreReader with real access scores (training set)
    @param scoresReaderAttackAccess ScoreReader with attack scores (training set)
    """

    #Checking if the number of countermeasures has a match
    self.__checkCounterMeasureNumbers(realScoreReader,attackScoreReader)

    self.__realScoreReader   = realScoreReader
    self.__attackScoreReader = attackScoreReader

    self.__llrMachine = None
    self.__llrTrained = False

    self.__scoreNormalizationAlg = scoreNormalizationAlg

    if scoreNormalizationAlg != None:
      if realScoreReader == None and attackScoreReader == None:
        raise ScoreFusionException("Real and Attack training scores need to be provided for the normalization step")
      else:
        self.__scoreNormalization = ScoreNormalization(numpy.concatenate((realScoreReader.getConcatenetedScores(), attackScoreReader.getConcatenetedScores()), axis=0))



  def __checkCounterMeasureNumbers(self,scoreReaderA,scoreReaderB):
    """
    Checking if the number of countermeasures has a match
    """
    if scoreReaderA != None and scoreReaderB != None:
      if(scoreReaderA.getNumberCountermeasures() != scoreReaderB.getNumberCountermeasures()):
        raise ScoreFusionException("Number of countermeasures between real access and attacks does not match")
    

  def __normalizeData(self,data):
    """
    Apply the score normalization set by __scoreNormalizationAlg
    """
    if(self.__scoreNormalizationAlg=="minmax"):
      return self.__scoreNormalization.calculateMinMaxNorm(data)
    elif(self.__scoreNormalizationAlg=="znorm"):
      return self.__scoreNormalization.calculateZNorm(data)
    elif(self.__scoreNormalizationAlg==None):
      return data
    else:
      raise ScoreFusionException("Normalization algorithm " + self.__scoreNormalizationAlg + " invalid.")


  def __normalizeOutput(self,normalizationFactor,data):
    """
    Helper that normalize some data between -1 and 1
    """

    scoreNorm = ScoreNormalization(normalizationFactor)
    return scoreNorm.calculateMinMaxNorm(data)


  def getLLRScores(self,scoreReader, normalizeOutput=True, trainScores=None):
    """
    Get the fusion of scores using the LLR machine

    @param scoreReader Score reader with the scores to be fused. If the LLR Machine was not trained the method will train
    @param normalizeOutput Normalize the output between -1 and 1
    @param trainScores A tuple of numpy.arrays with positive and negatives scores which are going to be used to train the LLR machine. If the value of this variable is None, the scores from self.__realScoreReader and self.__realScoreAttack will be used.
   
    @return A numpy.array with the scores
    """

    self.__checkCounterMeasureNumbers(self.__realScoreReader,scoreReader)

    #Applying normalization
    normalizedData = self.__normalizeData(scoreReader.getConcatenetedScores())
    normalizedReal   = None
    normalizedAttack = None

    #Trainning the LLR if not trained
    if(not self.__llrTrained):
      self.__llrTrained = True
      llrTrainer = bob.trainer.LLRTrainer()
      self.__llrMachine = bob.machine.LinearMachine()

      if trainScores == None:
        normalizedReal   = self.__normalizeData(self.__realScoreReader.getConcatenetedScores())
        normalizedAttack = self.__normalizeData(self.__attackScoreReader.getConcatenetedScores())
        llrTrainer.train(self.__llrMachine, normalizedReal,normalizedAttack)
      else: #trainScores are supplied as pre-defined numpy arrays (and not through ScoreReader)
        # work around bad bindings for the LLRtrainer (that need to be fixed)
        train_pos=numpy.array(trainScores[0],copy=True,order='C',dtype='float')
        train_neg=numpy.array(trainScores[1],copy=True,order='C',dtype=numpy.float64)
        llrTrainer.train(self.__llrMachine, train_pos, train_neg)

    #Applying the LLR in the input data
    outputData = self.__llrMachine(normalizedData)

    #Normalizing the output
    if(normalizeOutput):
      #Getting the scores for the trainning data
      if(normalizedReal == None):
        normalizedReal   = self.__normalizeData(self.__realScoreReader.getConcatenetedScores())
        normalizedAttack = self.__normalizeData(self.__attackScoreReader.getConcatenetedScores())

      normalizedReal   = self.__llrMachine(normalizedReal)
      normalizedAttack = self.__llrMachine(normalizedAttack)

      #Normalizing the output
      normalizationFactor  = numpy.concatenate((normalizedReal,normalizedAttack),axis=0)
      outputData = self.__normalizeOutput(normalizationFactor,outputData)  

    outputData = numpy.reshape(outputData,(len(outputData)))
    return outputData



  def getSUMScores(self,scoreReader, normalizeOutput=True):
    """
    Get the fusion of scores using the SUM rule. The countermeasures scores has the same weight.

    @param scoreReader Score reader with the scores to be fused. If the LLR Machine was not trained the method will train
    @param normalizeOutput Normalize the output between 0 and 1
   
    @return A numpy.array with the scores
    """

    self.__checkCounterMeasureNumbers(self.__realScoreReader,scoreReader)


    #Applying the score normalization
    normalizedData = self.__normalizeData(scoreReader.getConcatenetedScores())
    normalizedReal   = None
    normalizedAttack = None


    #Applying the SUM rule in the input data
    outputData = numpy.sum(normalizedData,axis=1)

    #Normalizing the output
    if(normalizeOutput):
      #Getting the scores for the trainning data
      if(normalizedReal == None):
        normalizedReal   = self.__normalizeData(self.__realScoreReader.getConcatenetedScores())
        normalizedAttack = self.__normalizeData(self.__attackScoreReader.getConcatenetedScores())

      normalizedReal   = numpy.sum(normalizedReal,axis=1)
      normalizedAttack = numpy.sum(normalizedAttack,axis=1)

      #Normalizing the output
      normalizationFactor  = numpy.concatenate((normalizedReal,normalizedAttack),axis=0)
      outputData = self.__normalizeOutput(normalizationFactor,outputData)  

    outputData = numpy.reshape(outputData,(len(outputData)))
    return outputData


  def countCommonErrors(self, scoreReader, thresholds, labels):
    """
    Calculate the number of common errors that two or more different algorithms make.

    @param scoreReader Score reader with the scores of each of the algorithms.
    @param thresholds An iterable (list or tuple) with the thresholds used for binary classification of each of the algorithms (for example, threshold on EER or HTER on the development set)
    @param labels A numpy array containing the labels (tuple or list) containing the labels for the scores in the files
   
    @return Number of common errors of the counter measures

    Note: no normalization is done. It is assumed that the provided thresholds are on the same scale as the scores in the Score Reader
    """

    self.__checkCounterMeasureNumbers(self.__realScoreReader,scoreReader)

    if len(scoreReader.scoresDir) != len(thresholds):
      raise ScoreFusionException("Number of countermeasures does not match with the number of threholds")

    allData = scoreReader.getConcatenetedScores()

    numErrors = []
    decisions = numpy.ndarray(allData.shape, 'int')

    for i in range(0, len(thresholds)): # put 1 for all the countermeasures which decided positively for a sample, and 0 if they decided negatively for a sample
      allData[allData[:,i]>thresholds[i], i] = thresholds[i] + 1
      allData[allData[:,i]<=thresholds[i], i] = thresholds[i]
      allData[:,i] -= thresholds[i]
      decisions[:,i] = (allData[:,i] == labels)
      numErrors.append(numpy.sum(allData[:,i] != labels))
      
    decisionList = numpy.sum(decisions, axis=1)
    
    numCommonErrors = sum(decisionList == 0)

    #relativeCommonErrors = [float(numCommonErrors) / x for x in numErrors]   # the number of common errors relative to the number of errors for each counter measure

    return numCommonErrors, numErrors #, relativeCommonErrors


class ScoreFusionException(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)


