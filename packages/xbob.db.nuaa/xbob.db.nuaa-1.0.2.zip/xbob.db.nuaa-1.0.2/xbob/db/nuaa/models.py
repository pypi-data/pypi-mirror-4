#!/usr/bin/env python
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Thu Sep 20 12:15:37 CEST 2012

import os
import bob

class File(object):
  """ Generic file container """

  def __init__(self, filename, version, cls, group):

    self.filename = filename
    self.version = version # 'raw', 'detected_face' or 'normalized_face' 
    self.cls = cls # 'attack' or 'real'
    self.group = group # 'train' or 'test'
    
  def __repr__(self):
    return "File('%s')" % self.filename

  def make_path(self, directory=None, extension=None):
    """Wraps this files' filename so that a complete path is formed

    Keyword parameters:

    directory
      An optional directory name that will be prefixed to the returned result.

    extension
      An optional extension that will be suffixed to the returned filename. The
      extension normally includes the leading ``.`` character as in ``.jpg`` or
      ``.hdf5``.

    Returns a string containing the newly generated file path.
    """

    if not directory: directory = ''
    if not extension: extension = ''
    return os.path.join(directory, self.filename + extension)
    
  def is_real():
    """True if the file belongs to a real access, False otherwise """

    return bool(self.cls == 'real')

  def get_clientno(self):
    """The ID of the client. Can be a string with values from '0001'-'0016'."""

    short_filename = self.filename.rpartition('/')[2] # just the filename (without the full path)
    stems = short_filename.split('_')
    return stems[0]

  def get_glasses(self):
    """'00' if the client has glasses, '01' in the other case"""

    short_filename = self.filename.rpartition('/')[2] # just the filename (without the full path)
    stems = short_filename.split('_')
    return stems[1]

  def get_condition(self):
    """The code of the combination of shooting lighting conditions and spoofing image poses. The possible codes are strings with values from '00'-'08'"""

    short_filename = self.filename.rpartition('/')[2] # just the filename (without the full path)
    stems = short_filename.split('_')
    return stems[2]

  def get_session(self):
    """The number of shooting session. The possible values are from '01'-'03'"""

    short_filename = self.filename.rpartition('/')[2] # just the filename (without the full path)
    stems = short_filename.split('_')
    return stems[3]

  def save(self, data, directory=None, extension='.hdf5'):
    """Saves the input data at the specified location and using the given
    extension.

    Keyword parameters:

    data
      The data blob to be saved (normally a :py:class:`numpy.ndarray`).

    directory
      If not empty or None, this directory is prefixed to the final file
      destination

    extension
      The extension of the filename - this will control the type of output and
      the codec for saving the input blob.
    """

    path = self.make_path(directory, extension)
    bob.db.utils.makedirs_safe(os.path.dirname(path))
    bob.io.save(data, path)



