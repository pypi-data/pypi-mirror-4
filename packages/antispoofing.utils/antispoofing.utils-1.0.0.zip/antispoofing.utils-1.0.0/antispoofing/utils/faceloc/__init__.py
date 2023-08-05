#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Tue 19 Jul 2011 12:53:56 CEST 

"""Support methods and classes for reading face locations from text files."""

import bob
import numpy
from .BoundingBox import * 

def expand_detections(detections, nframes, max_age=-1, faceSizeFilter=0):
  """Calculates a list of "nframes" with the best possible detections taking
  into consideration the ages of the last valid detectio on the detections
  list.

  Keyword Parameters:

  detections
    A dictionary containing keys that indicate the frame number of the
    detection and a value which is a BoundingBox object.

  nframes
    An integer indicating how many frames has the video that will be
    analyzed.

  max_age
    An integer indicating for a how many frames a detected face is valid if
    no detection occurs after such frame. A value of -1 == forever
  
  faceSizeFilter
    The minimum required size of face height (in pixels)
  """

  retval = []
  curr = None
  age = 0
  for k in range(nframes):
    if detections and detections.has_key(k) and detections[k].is_valid(faceSizeFilter=faceSizeFilter):
      curr = detections[k]
      age = 0
    elif max_age < 0 or age < max_age:
      age += 1
    else: # no detections and age is larger than maximum allowed
      curr = None

    retval.append(curr)

  return retval

def read_face(filename):
  """Reads a single file containing the face locations.

  Parameters:

  filename
    the name of the text file containing the face locations

  Returns: A dictionary containing the frames in which detection occurred and
  with keys corresponding to BoundingBox objects:

    * Bounding box top-left X coordinate
    * Bounding box top-left Y coordinate
    * Bounding box width
    * Bounding box height

  """

  f = open(filename, 'rt') #opens the file for reading

  # we read all lines that are not empty
  lines = [k.strip() for k in f.readlines() if k.strip()]

  # iteratively transform the data in every line and store it on the
  # to-be-returned dictionary
  retval = {}
  for i, line in enumerate(lines):
    s = line.split()
    if len(s) < 4:
      raise RuntimeError, \
          "Cannot make sense of data in line %d of file '%s': '%s'" % \
          (i, filename, " ".join(line))
    retval[int(s[0])] = BoundingBox(s[1], s[2], s[3], s[4])

  return retval

def preprocess_detections(filename, nFrames, facesize_filter=0, max_age=-1):
  """Reads a single face with the face locations getting the best possible
  detections taking into consideration the ages of the last valid detection

  Keyword Parameters:

  filename 
    The file name with the face annotations
  
  nFrames 
    An integer indicating how many frames has the video that will be analyzed.

  facesize_filter
    The minimum required size of face height (in pixels)

  max_age 
    An integer indicating for a how many frames a detected face is valid if no
    detection occurs after such frame. A value of -1 == forever

  Returns dictionary containing the frames in which detection occurred and with
  keys corresponding to BoundingBox objects.
  """

  locations = read_face(filename)
  locations = expand_detections(locations,nFrames,faceSizeFilter=facesize_filter,max_age=max_age)

  return locations
