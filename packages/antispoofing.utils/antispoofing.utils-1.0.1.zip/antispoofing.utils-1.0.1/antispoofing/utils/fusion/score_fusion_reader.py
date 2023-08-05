#!/usr/bin/env python
#Tiago de Freitas Pereira <tiagofrepereira@gmail.com>
#Oct 01 14:12:00 CEST 2012

"""
This script is an utility for prepate scores for fusion

"""

import bob
import numpy

from antispoofing.utils.helpers import *

class ScoreFusionReader:
  """
  Class that read scores for fuse countermeasures.
  """

  def __init__(self,scoreObjects,scoresDir):
    """
    Receive a list file objects (xbob.db.files) and path for the scores directories
    """
    
    if(len(scoreObjects) <=0):
      raise ScoreFusionReaderException("There is no scores in the list.")
   
    if(len(scoresDir) <=0):
      raise ScoreFusionReaderException("The score directories must be provided.")

    self.scoreObjects = scoreObjects
    self.scoresDir    = scoresDir

    #Checking if the number of scores of each set of scores are the same
    scoreReader   = ScoreReader(scoreObjects,scoresDir[0])
    self.numberOfScores = len(scoreReader.getScores(onlyValidScores=False))

    for i in range(1,len(scoresDir)): 
      scoreReader   = ScoreReader(scoreObjects,scoresDir[i])

      if(self.numberOfScores != len(scoreReader.getScores(onlyValidScores=False))):
        raise ScoreFusionReaderException("The number of scores in each directory does not mach.")
      

  def __str__(self):
    return "<ScoreReader> - There are {0} scores extracted from {1} videos of {2} different countermeasures".format(self.numberOfScores,len(self.scoreObjects),len(self.scoresDir))


  def getNumberCountermeasures(self):
    """
    Return the number of Countermeasures
    """
    return len(self.scoresDir)


  def getConcatenetedScores(self,onlyValidScores=True):
    """
    Get the scores from different sources an concatenate them returning in a numpy.ndarray format

    onlyValidScores Will consider only the not nan scores
    """

    scoreReader        = ScoreReader(self.scoreObjects,self.scoresDir[0])
    scores             = scoreReader.getScores(onlyValidScores=False)
    concatenatedScores = numpy.reshape(scores,(len(scores),1))

    for i in range(1,len(self.scoresDir)):
      scoresReader       = ScoreReader(self.scoreObjects,self.scoresDir[i])
      scores             = scoresReader.getScores(onlyValidScores=False)
      scores             = numpy.reshape(scores,(len(scores),1))
      concatenatedScores = numpy.concatenate((concatenatedScores,scores),axis=1)

    #Will remove the Nan data
    if(onlyValidScores):
      nanLines = numpy.array([numpy.sum(numpy.isnan(concatenatedScores[j,:])) for j in range(concatenatedScores.shape[0])])
      nanLines = numpy.where(nanLines>0)[0]

      #removing the lines with nan
      concatenatedScores = numpy.delete(concatenatedScores,nanLines,axis=0)
    
    concatenatedScores = numpy.array(concatenatedScores,copy=True,order='C',dtype='float')

    return concatenatedScores

  def getScoresByIndex(self,index):
    """
    Get an specific set of scores by index
    """

    if((index < 0) or (index > self.getNumberCountermeasures() )):
      raise ScoreFusionReaderException("Index out of bounds. There are only {0} countermeasures of score".format(self.getNumberCountermeasures()))

    scoreReader = ScoreReader(self.scoreObjects,self.scoresDir[index])
    scores      = scoreReader.getScores()
    scores      = numpy.reshape(scores,(len(scores)))

    return scores


class ScoreFusionReaderException(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)


