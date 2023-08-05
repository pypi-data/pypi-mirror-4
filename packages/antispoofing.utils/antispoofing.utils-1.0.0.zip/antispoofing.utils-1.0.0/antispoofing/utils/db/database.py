#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiagofrepereira@gmail.com>
# Andre Anjos <andre.anjos@idiap.ch>
# Tue 01 Oct 2012 16:48:44 CEST 

import abc

class File(object):
  """Abstract class that define basic properties of File objects"""

  __metaclass__ = abc.ABCMeta

  @abc.abstractmethod
  def videofile(self, directory=None):
    """Returns the path to the database video file for this object

    Keyword Parameters:

    directory 
      An optional directory name that will be prefixed to the returned result.

    Returns a string containing the video file path.
    """
    return

  @abc.abstractmethod
  def facefile(self, directory=None):
    """Returns the path to the companion face bounding-box file

    Keyword Parameters:

    directory 
      An optional directory name that will be prefixed to the returned result.

    Returns a string containing the face file path.
    """
    return

  @abc.abstractmethod
  def bbx(self, directory=None):
    """Reads the file containing the face locations for the frames in the
    current video

    Keyword Parameters

    directory 
      A directory name that will be prepended to the final filepaths where the
      face bounding boxes are located, if not on the current directory.

    Returns a :py:class:`numpy.ndarray` containing information about the
    located faces in the videos. Each row of the :py:class:`numpy.ndarray`
    corresponds for one frame. The five columns of the
    :py:class:`numpy.ndarray` are (all integers):

      * Frame number (int)
      * Bounding box top-left X coordinate (int)
      * Bounding box top-left Y coordinate (int)
      * Bounding box width (int)
      * Bounding box height (int)

      Note that **not** all the frames may contain detected faces.
    """
    return

  @abc.abstractmethod
  def load(self, directory=None, extension='.hdf5'):
    """Loads the data at the specified location and using the given extension.

    Keyword Parameters:

    data 
      The data blob to be saved (normally a :py:class:`numpy.ndarray`).

    directory 
      [optional] If not empty or None, this directory is prefixed to the final
      file destination

    extension 
      [optional] The extension of the filename - this will control the type of
      output and the codec for saving the input blob.  
      
    """
    return

  @abc.abstractmethod
  def save(self, data, directory=None, extension='.hdf5'):
    """Saves the input data at the specified location and using the given
    extension.

    Keyword Parameters:

    data 
      The data blob to be saved (normally a :py:class:`numpy.ndarray`).

    directory 
      [optional] If not empty or None, this directory is prefixed to the final
      file destination

    extension 
      [optional] The extension of the filename - this will control the type of
      output and the codec for saving the input blob.
      
    """
    return

  @abc.abstractmethod
  def make_path(self, directory=None, extension=None):
    """Wraps the current path so that a complete path is formed

    Keyword Parameters:

    directory 
      An optional directory name that will be prefixed to the returned result.

    extension
      An optional extension that will be suffixed to the returned filename. The
      extension normally includes the leading ``.`` character as in ``.jpg`` or
      ``.hdf5``.

    Returns a string containing the newly generated file path.
    """
    return 

class Database(object):
  """Abstract class that define the basic API for querying antispoofing
  databases. Queries result in :py:class:`File` objects.
  """

  __metaclass__ = abc.ABCMeta

  @abc.abstractmethod
  def __init__(self, parsed_arguments):
    """Initializes an instanced of the Database with argparse parsed
    arguments."""
    return

  #################
  # File querying #
  #################

  @abc.abstractmethod
  def get_train_data(self):
    """
    Will return the real access and the attack File objects (antispoofing.utils.db.files.File) for training the antispoofing classifier
    """
    return

  @abc.abstractmethod
  def get_devel_data(self):
    """
    Will return the real access and the attack File objects (antispoofing.utils.db.files.File) for development (supposed to tune the antispoofing classifier)
    """
    return

  @abc.abstractmethod
  def get_test_data(self):
    """
    Will return the real access and the attack File objects (antispoofing.utils.db.files.File) for test (supposed to report the results)
    """
    return

  @abc.abstractmethod
  def get_all_data(self):
    """
    Will return the real access and the attack File objects (antispoofing.utils.db.files.File) for ALL group sets
    """
    return

  ######################
  # Management methods #
  ######################
  
  @abc.abstractmethod
  def create_subparser(self, subparser, entry_point_name):
    """
    Creates a subparser for the central manager taking into consideration the
    options for every module that can provide those

    Keyword parameters

    subparser
      The argparse subparser I'll attach to

    entry_point_name
      My name, given on the setup of this package (or whatever I'm declared as
      an ``entry_point``).
    """
    return 

  @abc.abstractmethod
  def short_description(self):
    """Returns a short (1 line) description about this database"""
    return

  @abc.abstractmethod
  def long_description(self):
    """Returns a longer description about this database"""
    return

  @abc.abstractmethod
  def implements_any_of(self, propname):
    """Tells if this database subtype implements a given property
    
    Keyword Parameters

    propname
      A string or an iterable of strings that define at least one access
      protocol this dataset must implement (e.g. ``video`` or ``photo``).

    Returns ``True`` if the dataset implements **any** of the access protocols
    or ``False`` otherwise.
    """
    return

  #################################################
  # Factory for iterating through known instances #
  #################################################

  @staticmethod
  def create_parser(parser, implements_any_of=None):
    """Defines a sub parser for each database, with optional properties.

    Keyword Parameters:

    parser
      The argparse.ArgumentParser to which I'll attach the subparsers to

    implements_any_of
      A string or an interable over strings that determine **at least** one
      property that the given database has to fullfill so that it gets included
      in the parser. This method will call the instance's `implements()` to
      find if the instance implements or not the given access protocol.
    """

    subparsers = parser.add_subparsers(help="Available databases",
        title='Databases', description='choose one of the following databases to run this script with:')

    #For each resource
    import pkg_resources
    for entrypoint in pkg_resources.iter_entry_points('antispoofing.utils.db'):
      plugin = entrypoint.load()
      db = plugin()
      if db.implements_any_of(implements_any_of):
        db.create_subparser(subparsers, entrypoint.name)
