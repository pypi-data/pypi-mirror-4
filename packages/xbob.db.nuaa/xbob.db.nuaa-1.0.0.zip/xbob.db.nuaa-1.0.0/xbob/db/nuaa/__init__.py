#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Ivana Chingovska <ivana.chingovska@idiap.ch>
# Wed Feb 15 12:57:28 CET 2012

"""
The NUAA database is a spoofing attack database which consists of real accesses
and only printed photo attacks. There are three versions of the database:
version composed of raw images, version composed of the cropped faces detected
in the images and version composed of 64x64 normalized faces detected in the
images. There are only train and test set defined.

References:

  1. X. Tan, Y. Li, J. Liu, L. Jiang: "Face Liveness Detection from a Single
  Image with Sparse Low Rank Bilinear Discriminative Model", Proceedings of
  11th European Conference on Computer Vision (ECCV'10), Crete, Greece,
  September 2010; p.9-11
"""

import os
from .models import *

class Database(object):

  def __init__(self):  
    from .driver import Interface
    from pkg_resources import resource_filename
    self.info = Interface()
    self.location = resource_filename(__name__, '')
    self.groups = ('train', 'test')
    self.classes = ('attack', 'real')
    self.versions = ('raw','detected_face','normalized_face')

  def files(self, directory=None, extension=None, groups=None, cls=None, versions=None):
    """Returns a set of filenames for the specific query by the user.

    .. deprecated:: 1.1.0

      This function is *deprecated*, use :py:meth:`.Database.objects` instead.

    Keyword Parameters:

    directory
      A directory name that will be prepended to the final filepath returned

    extension
      A filename extension that will be appended to the final filepath returned

    groups
      One of the protocolar subgroups of data as specified in the tuple groups,
      or a tuple with several of them.  If you set this parameter to an empty
      string or the value None, we use reset it to the default which is to get
      all.

    cls
      Either "attack", "real" or any combination of those (in a tuple). Defines
      the class of data to be retrieved.  If you set this parameter to an empty
      string or the value None, we use reset it to the default, ("real",
      "attack").

    versions
      Either "raw", "detected_face", "normalized_face" or any combination of
      those (in a tuple). Defines the version of the database that is going to
      be used. If you set this parameter to the value None, the images from all
      the versions are returned ("raw", "detected_face", "normalized_face").

    Returns: A dictionary containing the resolved filenames considering all the
    filtering criteria. The keys of the dictionary are just pro-forma (for
    uniformity with the other databases).  
    
    """

    import warnings
    warnings.warn("The method Database.files() is deprecated, use Database.objects() for more powerful object retrieval", DeprecationWarning)

    def check_validity(l, obj, valid, default):
      """Checks validity of user input data against a set of valid values"""
      if not l: return default
      elif isinstance(l, str): return check_validity((l,), obj, valid, default)
      for k in l:
        if k not in valid:
          raise RuntimeError, 'Invalid %s "%s". Valid values are %s, or lists/tuples of those' % (obj, k, valid)
      return l

    def make_path(stem, directory, extension):
      if not extension: extension = ''
      if directory: return os.path.join(directory, stem + extension)
      return stem + extension


    # check if groups set are valid
    VALID_GROUPS = self.groups
    groups = check_validity(groups, "group", VALID_GROUPS, VALID_GROUPS)

    # check if versions are valid
    VALID_VERSIONS = self.versions
    versions = check_validity(versions, "version", VALID_VERSIONS, VALID_VERSIONS)

    # by default, do NOT grab enrollment data from the database
    VALID_CLASSES = self.classes
    cls = check_validity(cls, "class", VALID_CLASSES, ('real', 'attack'))
  
    retval = {}
    key = 0
    
    # because of couple of non-uniformities in the naming system in the database, we need to introduce these dictionaries to convert between names
    version_dict = {'raw':'raw', 'detected_face':'Detectedface', 'normalized_face':'NormalizedFace'}
    version_dict_1 = {'raw':'Raw', 'detected_face':'Face', 'normalized_face':'Normalized'}
    cls_dict = {'attack':'Imposter', 'real':'Client'}

    for v in versions:   
      if (v == 'raw' or v == 'detected_face') and extension=='.bmp': extension = '.jpg' # the extension is .jpg for raw data and detected faces images
      if v == 'normalized_face' and extension=='.jpg': extension = '.bmp' # the extension is .bmp for normalized faces images
      for c in cls:
        for g in groups:
          bdir = version_dict[v]
          # the filename with the list of files belonging to the user specified criteria
          readfilename = os.path.join(self.location, bdir, cls_dict[c].lower()+'_'+g+'_'+version_dict_1[v].lower()+'.txt')
          readfilelines = open(readfilename, 'r').readlines()
          filesdir = os.path.join(bdir, cls_dict[c]+version_dict_1[v]) # the directory where the files are stored
          for i in readfilelines:
            name = i.partition('.')[0].replace("\\", "/") # remove the initial extension, do string procesing
            retval[key] = make_path(os.path.join(filesdir, name), directory, extension)
            key = key + 1
    return retval

  def objects(self, groups=None, cls=None, versions=None, client_no=None, glasses=None, conditions=None, session=None):
    """Returns a list of unique :py:class:`.File` objects for the specific query by the user.

    Keyword Parameters:

    groups
      One of the protocolar subgroups of data as specified in the tuple groups,
      or a tuple with several of them.  If you set this parameter to an empty
      string or the value None, we use reset it to the default which is to get
      all.

    cls
      Either "attack", "real" or any combination of those (in a tuple). Defines
      the class of data to be retrieved.  If you set this parameter to an empty
      string or the value None, we use reset it to the default, ("real",
      "attack").

    versions
      Either "raw", "detected_face", "normalized_face" or any combination of
      those (in a tuple). Defines the version of the database that is going to
      be used. If you set this parameter to the value None, the images from all
      the versions are returned ("raw", "detected_face", "normalized_face").

    client_no 
      The number of the client. A string (or tuple of strings) with values from
      '0001'-'0016'

    glasses
      A string (or tuple of strings) with value '00' for clients with glasses
      and '01' for cleints without glasses

    conditions
      A string (or tuple of strings) with values '00'-'08' for various
      combinations of lighting conditions and spoofing images poses

    session
      A string (or tuple of strings) with values '01'-'03' for three different
      client enrollment sessions

    Returns: A list of :py:class:`.File` objects.
    
    """

    def check_validity(l, obj, valid, default):
      """Checks validity of user input data against a set of valid values"""
      if not l: return default
      elif isinstance(l, str): return check_validity((l,), obj, valid, default)
      for k in l:
        if k not in valid:
          raise RuntimeError, 'Invalid %s "%s". Valid values are %s, or lists/tuples of those' % (obj, k, valid)
      return l

    # check if groups set are valid
    VALID_GROUPS = self.groups
    groups = check_validity(groups, "group", VALID_GROUPS, VALID_GROUPS)

    # check if versions are valid
    VALID_VERSIONS = self.versions
    versions = check_validity(versions, "version", VALID_VERSIONS, VALID_VERSIONS)

    # by default, do NOT grab enrollment data from the database
    VALID_CLASSES = self.classes
    cls = check_validity(cls, "class", VALID_CLASSES, ('real', 'attack'))
  
    retval = []
    
    # because of couple of non-uniformities in the naming system in the database, we need to introduce these dictionaries to convert between names
    version_dict = {'raw':'raw', 'detected_face':'Detectedface', 'normalized_face':'NormalizedFace'}
    version_dict_1 = {'raw':'Raw', 'detected_face':'Face', 'normalized_face':'Normalized'}
    cls_dict = {'attack':'Imposter', 'real':'Client'}

    for v in versions:   
      for c in cls:
        for g in groups:
          bdir = version_dict[v]
          # the filename with the list of files belonging to the user specified criteria
          readfilename = os.path.join(self.location, bdir, cls_dict[c].lower()+'_'+g+'_'+version_dict_1[v].lower()+'.txt')
          readfilelines = open(readfilename, 'r').readlines()
          
          filesdir = os.path.join(bdir, cls_dict[c]+version_dict_1[v]) # the directory where the files are stored
          for i in readfilelines:
            name = i.partition('.')[0].replace("\\", "/") # remove the initial extension, do string procesing
            fileobj = File(os.path.join(filesdir, name), v, c, g)
            if client_no != None and isinstance(client_no, str): client_no = (client_no,) # transform it into a  tuple
            if glasses != None and isinstance(glasses, str): glasses = (glasses,) # transform it into a  tuple
            if conditions != None and isinstance(conditions, str): conditions = (conditions,) # transform it into a  tuple
            if session != None and isinstance(session, str): session = (session,) # transform it into a  tuple

            if client_no != None and fileobj.get_clientno() not in client_no:
              continue
            if glasses != None and fileobj.get_glasses() not in glasses:
              continue
            if conditions != None and fileobj.get_condition() not in conditions:
              continue
            if session != None and fileobj.get_session() not in session:
              continue

            retval.append(fileobj)
    return retval

  def filter_files(self, filenames, client_no=None, glasses=None, conditions=None, session=None):
    """ Filters the filenames in a dictionary and returns a filtered dictionary
    which contains only the images with the specified criteria.
 
    .. deprecated:: 1.1.0

      This function is *deprecated*, use :py:meth:`.Database.objects` instead.

    Keyword Parameters:

    filenames
      A dictionary with filenames (most probably obtained using the files()
      method).

    client_no 
      The number of the client. A string (or tuple of strings) with values from
      '0001'-'0016'

    glasses
      A string (or tuple of strings) with value '00' for clients with glasses
      and '01' for cleints without glasses

    conditions
      A string (or tuple of strings) with values '00'-'08' for various
      combinations of lighting conditions and spoofing images poses

    session
      A string (or tuple of strings) with values '01'-'03' for three different
      client enrollment sessions
    """

    import warnings
    warnings.warn("The method Database.files() is deprecated, use Database.objects() for more powerful object retrieval", DeprecationWarning)

    if isinstance(client_no, str): client_no = (client_no,) # transform it into a  tuple
    retval = {}
    newkey = 0
    for key, filename in filenames.items():
      short_filename = filename.rpartition('/')[2] # just the filename (without the full path)
      stems = short_filename.split('_')
      if client_no != None:
        if stems[0] not in client_no:
          continue
      if glasses != None:
        if stems[1] not in glasses:
          continue
      if conditions != None:
        if stems[2] not in conditions:
          continue
      if session != None:
        if stems[3] not in session:
          continue
      newkey = newkey + 1
      retval[newkey] = filename
        
    return retval  

  def cross_valid_gen(self, numpos, numneg, numfolds=10, outfilename=None):
    """Performs N-fold cross-validation on a given number of samples.
    Generates the indices of the validation subset for N folds, and writes them
    into a text file (the indices of the training samples are easy to compute
    once the indices of the validation subset are known). This method is
    intended for 2-class classification problems, therefore the number of both
    positive and negative samples should be given at the beginning. The method
    generates validation indices for both positive and negative samples
    separately. Each row of the output file are the validation indices of one
    fold; validation indices for the positive class are in the odd lines, and
    validation indices for the negative class are in the even lines.

    Keyword parameters:
   
    numpos
      Number of positive samples

    numneg
      Number of negative samples

    numfold
      Number of folds

    outfilename
      The filename of the output file
    """

    if outfilename == None:
      outfilename = os.path.join(self.location, 'folds', 'cross_valid.txt')
    f = open(outfilename, 'w')

    def cross_valid(numsamples, numfolds): 
      '''The actual cross-validation function, returns the validation indices
      in a tab-delimited null-terminated string'''

      from random import shuffle 
      X = range(0, numsamples)
      shuffle(X)
      retval = []
      for k in xrange(numfolds):
        tr = [X[i] for i in range(0, numsamples) if i % numfolds != k]
        vl = [X[i] for i in range(0, numsamples) if i % numfolds == k]
        valid = ""
        for ind in vl:
          valid += "%d\t" % ind
        retval.append(valid)
      return retval

    valid_pos = cross_valid(numpos, numfolds) # the validation indices of the positive set
    valid_neg = cross_valid(numneg, numfolds) # the validation indices of the negative set
    # it is enough to save just the validation indices, training indices are all the rest
    for i in range(0, numfolds):
      f.write(valid_pos[i] + '\n') # write the validation indices for the real samples (every odd line in the file)
      f.write(valid_neg[i] + '\n') # write the validation indices for the attack samples (every even line in the file)
    f.close()
    return 0

  def cross_valid_read(self, infilename=None):
    """Reads the cross-validation indices from a file and returns two lists of
    validation indices: for the positive and for the negative class. Each list
    actually consists of sublists; one sublist with validation indices for each
    fold.

    Keyword parameters:

    infilename:
      The input filename where the validation indices are stored
    """

    if infilename == None:
      infilename = os.path.join(self.location, 'folds', 'cross_valid.txt')
    lines = open(infilename, 'r').readlines()
    subsets_pos = [] 
    subsets_neg = []
    linenum = 1
    for line in lines:
      ind_list = [int(i) for i in line.rstrip('\n\t').split('\t')]
      if linenum % 2 == 1: subsets_pos.append(ind_list) # odd lines: validation indices for the positive class
      else: subsets_neg.append(ind_list) # even lines: validation indices for the negative class
      linenum += 1 
    return subsets_pos, subsets_neg

  def cross_valid_foldfiles(self, version, cls, infilename=None, fold_no=0, directory=None, extension=None):
    """Returns two dictionaries: one with the names of the files of the
    validation subset in one fold, and one with the names of the files in the
    training subset of that fold. The number of the cross_validation fold is
    given as a parameter.

    .. deprecated:: 1.1.0

      This function is *deprecated*, use :py:meth:`.Database.objects` instead.

    Keyword parameters:

    version
      The version of the database that is needed: 'raw', 'detected_face' or
      'normalized_face'.

    cls
      The class of the samples: 'real' or 'attack'
  
    infilename
      The name of the file where the cross-validation files are stored. If it
      is None, then the name of the filename with the cross-validation files is
      formed using the parameters version and cls. If this parameter is
      specified, then the parameters version and cls are ignored

    fold_no
      Number of the fold 

    directory
      This parameter will be prepended to all the filenames which are going to
      be returned by this procedure

    extension
      This parameter will be appended to all the filenames which are going to
      be returned by this procedure
    """

    import warnings
    warnings.warn("The method Database.cross_valid_foldfiles() is deprecated, use Database.cross_valid_foldobjects() for more powerful object retrieval", DeprecationWarning)

    if infilename == None:
      infilename = os.path.join(self.location, 'folds', version + '_' + cls + '.txt')
    lines = open(infilename, 'r').readlines()
    files_val = {} # the keys in the both dictionaries are just pro-forma, for compatibility with other databases
    files_train = {}
    k_val = 0; k_train = 0 # simple counters
    
    def make_path(stem, directory, extension):
      if not extension: extension = ''
      if directory: return os.path.join(directory, stem + extension)
      return stem + extension
   
    for line in lines:
      words = line.rstrip('\n\t').split('\t')
      if int(words[1]) == fold_no:
        files_val[k_val] = make_path(words[0], directory, extension); k_val += 1
      else:
        files_train[k_train] = make_path(words[0], directory, extension); k_train += 1

    return files_val, files_train
  

  def cross_valid_foldobjects(self, version, cls, infilename=None, fold_no=0):
    """Returns two lists of :py:class:`.File` objects, one with the files of the
    validation subset in one fold, and one with the files in the
    training subset of that fold. The number of the cross_validation fold is
    given as a parameter.

    Keyword parameters:

    version
      The version of the database that is needed: 'raw', 'detected_face' or
      'normalized_face'.

    cls
      The class of the samples: 'real' or 'attack'
  
    infilename
      The name of the file where the cross-validation files are stored. If it
      is None, then the name of the filename with the cross-validation files is
      formed using the parameters version and cls. If this parameter is
      specified, then the parameters version and cls are ignored

    fold_no
      Number of the fold 

    """

    if infilename == None:
      infilename = os.path.join(self.location, 'folds', version + '_' + cls + '.txt')
    lines = open(infilename, 'r').readlines()
    obj_val = [] 
    obj_train = []
    k_val = 0; k_train = 0 # simple counters
    
    for line in lines:
      words = line.rstrip('\n\t').split('\t')
      if int(words[1]) == fold_no:
        obj_val.append(File(words[0], version, cls, 'dev')) # the file still belongs to the training set, but is in dev set in cross-validation
      else:
        obj_train.append(File(words[0], version, cls, 'train'))

    return obj_val, obj_train


  def save_by_filename(self, filename, obj, directory, extension):
    """Saves a single object supporting the bob save() protocol.

     .. deprecated:: 1.1.0

      This function is *deprecated*, use :py:meth:`.File.save()` instead.

    This method will call save() on the the given object using the correct
    database filename stem for the given filename.
    
    Keyword parameters:

    filename
      The unique filename under which the object will be saved. Before calling this method, the method files() should be called (with no directory and extension arguments passed) in order to obtain the unique filenames for each of the files to be saved.

    obj
      The object that needs to be saved, respecting the bob save() protocol.

    directory
      This is the base directory to which you want to save the data. The
      directory is tested for existence and created if it is not there with
      os.makedirs()

    extension
      The extension determines the way each of the arrays will be saved.
    """

    import warnings
    warnings.warn("The method Database.save() is deprecated, use the File object directly as returned by Database.objects() for more powerful object manipulation.", DeprecationWarning)


    from ...io import save
    from bob.db.utils import makedirs_safe

    fullpath = os.path.join(directory, filename + extension)
    fulldir = os.path.dirname(fullpath)
    makedirs_safe(fulldir)
    save(obj, fullpath)

__all__ = dir()
