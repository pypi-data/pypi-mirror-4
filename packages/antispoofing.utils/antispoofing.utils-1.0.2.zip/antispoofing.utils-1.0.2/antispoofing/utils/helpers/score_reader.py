#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiagofrepereira@gmail.com>
# Thu 27 Sep 2011 13:01:44 CEST 

"""
Class that work with the scores

"""

import bob
import numpy

class ScoreReader:

  def __init__(self,files,inputDir):
    """
    " Receive a list of xbob.db.replay.File to return the scores
    """

    self.files = files
    self.inputDir = inputDir
  

  def __str__(self):
    return "%d video files " % len(self.files)


  def __reshape(self,scores):
    """
    A little hack. Sorry

    The motion package has the format x,1 and the lbptop has the format 1,x
    """
    if(scores.shape[1]==1):
      scores = numpy.reshape(scores,(scores.shape[1],scores.shape[0]))

    return scores


  def getScores(self,onlyValidScores=True):
    """
    Return a numpy.array with the scores of all xbob.db.replay.File

    @param onlyValidScores Will return only the valid scores
    """

    #Finding the number of elements
    totalScores = 0
    for f in self.files:
      fileName = str(f.make_path(self.inputDir,extension='.hdf5'))
      scores = bob.io.load(fileName)
      scores = self.__reshape(scores)
      totalScores =totalScores + scores.shape[1]

    #allScores = numpy.zeros(shape=(1,totalScores))
    allScores = numpy.zeros(shape=(totalScores))
    offset = 0
    for f in self.files:
      fileName = str(f.make_path(self.inputDir,extension='.hdf5'))

      scores = bob.io.load(fileName)
      scores = self.__reshape(scores)

      #allScores=numpy.concatenate((allScores,scores),axis=1)
      #allScores[0,offset:offset+scores.shape[1]] = scores
      allScores[offset:offset+scores.shape[1]] = numpy.reshape(scores,(scores.shape[1]))
      offset = offset + scores.shape[1]


    if(onlyValidScores):
      allScores = allScores[(numpy.where(numpy.isnan(allScores)==False))[0]]

    return allScores

