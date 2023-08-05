#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Ivana Chingovska <ivana.chingovska@idiap.ch>
# Sun Mar 25 18:33:12 CEST 2012

"""Dumps lists of files.
"""

import os
import sys
from bob.db.driver import Interface as BaseInterface
from . import Database

# Driver API
# ==========

def dumplist(args):
  """Dumps lists of files based on your criteria"""

  from . import Database
  db = Database()

  objects = db.objects(groups=args.group, cls=args.cls, versions=args.database_version)

  output = sys.stdout
  if args.selftest:
    from bob.db.utils import null
    output = null()

  for obj in objects:
    output.write('%s\n' % (obj.make_path(directory=args.directory, extension=args.extension),))

  return 0
  
def dumpfold(args):
  """Dumps lists of files belonging to a certain cross validation fold based on your criteria"""

  from .__init__ import Database
  db = Database()

  r = db.cross_valid_foldfiles(version=args.database_version, cls=args.cls, fold_no=args.fold_no, directory=args.directory, extension=args.extension)
  
  output = sys.stdout
  if args.selftest:
    from bob.db.utils import null
    output = null()

  if args.subset == 'validation':
    for id, f in r[0].items():
      output.write('%s\n' % (f,))

  if args.subset == 'training':
    for id, f in r[1].items():
      output.write('%s\n' % (f,))

  if args.subset == '':
    output.write("Validations subset:\n")
    for id, f in r[0].items():
      output.write('%s\n' % (f,))
    output.write("Training subset:\n")
    for id, f in r[1].items():
      output.write('%s\n' % (f,))

  return 0

def checkfiles(args):
  """Checks the existence of the files based on your criteria""" 
    
  from .__init__ import Database
  db = Database()

  objects = db.objects(groups=args.group, cls=args.cls, versions=args.database_version)

  # go through all files, check if they are available on the filesystem
  good = []
  bad = []
  for obj in objects:
    if os.path.exists(obj.make_path(directory=args.directory, extension=args.extension)): good.append(obj)
    else: bad.append(obj)

  # report
  output = sys.stdout
  if args.selftest:
    from bob.db.utils import null
    output = null()

  if bad:
    for obj in bad:
      output.write('Cannot find file "%s"\n' % (obj.make_path(directory=args.directory, extension=args.extension),))
    output.write('%d files (out of %d) were not found at "%s"\n' % \
        (len(bad), len(objects), args.directory))

  return 0

class Interface(BaseInterface):

  def name(self):
    return 'nuaa'

  def files(self):
    from pkg_resources import resource_filename
    raw_files = (
        'raw_real.txt',
        'raw_attack.txt',
        'normalized_face_real.txt',
        'normalized_face_attack.txt',
        'detected_face_real.txt',
        'detected_face_attack.txt',
        'cross_valid.txt',
        os.path.join('raw', 'imposter_train_raw.txt'),
        os.path.join('raw', 'imposter_test_raw.txt'),
        os.path.join('raw', 'client_train_raw.txt'),
        os.path.join('raw', 'client_test_raw.txt'),
        os.path.join('NormalizedFace', 'imposter_train_normalized.txt'),
        os.path.join('NormalizedFace', 'imposter_test_normalized.txt'),
        os.path.join('NormalizedFace', 'client_train_normalized.txt'),
        os.path.join('NormalizedFace', 'client_test_normalized.txt'),
        os.path.join('Detectedface', 'imposter_train_face.txt'),
        os.path.join('Detectedface', 'imposter_test_face.txt'),
        os.path.join('Detectedface', 'client_train_face.txt'),
        os.path.join('Detectedface', 'client_test_face.txt'),
        )
    return [resource_filename(__name__, k) for k in raw_files]

  def version(self):
    import pkg_resources  # part of setuptools
    return pkg_resources.require('xbob.db.%s' % self.name())[0].version

  def type(self):
    return 'text'

  def add_commands(self, parser):  
    """Add specific subcommands that the action "dumplist" can use"""

    from . import __doc__ as docs
    
    subparsers = self.setup_parser(parser, "NUAA Face Spoofing Database", docs)

    db = Database()

    from argparse import SUPPRESS

    # add the dumplist command
    dump_message = "Dumps list of files based on your criteria"
    dump_parser = subparsers.add_parser('dumplist', help=dump_message)
    dump_parser.add_argument('-d', '--directory', dest="directory", default='', help="if given, this path will be prepended to every entry returned (defaults to '%(default)s')")
    dump_parser.add_argument('-e', '--extension', dest="extension", default='', help="if given, this extension will be appended to every entry returned (defaults to '%(default)s')")
    dump_parser.add_argument('-c', '--class', dest="cls", default=None, help="if given, limits the dump to a particular subset of the data that corresponds to the given class (defaults to '%(default)s')", choices=db.classes)
    dump_parser.add_argument('-g', '--group', dest="group", default=None, help="if given, this value will limit the output files to those belonging to a particular group. (defaults to '%(default)s')", choices=db.groups)
    dump_parser.add_argument('-v', '--version', dest="database_version", default=None, help="if given, this value will limit the output files to those belonging to a particular version of the database. (defaults to '%(default)s')", choices=db.versions)
    dump_parser.add_argument('--self-test', dest="selftest", default=False, action='store_true', help=SUPPRESS)
    dump_parser.set_defaults(func=dumplist) #action

    # add the checkfiles command
    check_message = "Check if the files exist, based on your criteria"
    check_parser = subparsers.add_parser('checkfiles', help=check_message)
    check_parser.add_argument('-d', '--directory', dest="directory", default='', help="if given, this path will be prepended to every entry returned (defaults to '%(default)s')")
    check_parser.add_argument('-e', '--extension', dest="extension", default='', help="if given, this extension will be appended to every entry returned (defaults to '%(default)s')")
    check_parser.add_argument('-c', '--class', dest="cls", default=None, help="if given, limits the dump to a particular subset of the data that corresponds to the given class (defaults to '%(default)s')", choices=db.classes)
    check_parser.add_argument('-g', '--group', dest="group", default=None, help="if given, this value will limit the output files to those belonging to a particular group. (defaults to '%(default)s')", choices=db.groups)
    check_parser.add_argument('-v', '--version', dest="database_version", default=None, help="if given, this value will limit the output files to those belonging to a particular version of the database. (defaults to '%(default)s')", choices=db.versions)
    check_parser.add_argument('--self-test', dest="selftest", default=False, action='store_true', help=SUPPRESS)
    check_parser.set_defaults(func=checkfiles) #action

    # add the dumpfold command
    dumpfold_message = "Dumps list of files belonging to a certain cross-fold validation fold based on your criteria"
    dumpfold_parser = subparsers.add_parser('dumpfold', help=dumpfold_message)
    dumpfold_parser.add_argument('cls', help="limits the dump to a particular subset of the data that corresponds to the given class (defaults to '%(default)s')", choices=db.classes)
    dumpfold_parser.add_argument('database_version', help="this value will limit the output files to those belonging to a particular version of the database. (defaults to '%(default)s')", choices=db.versions)
    dumpfold_parser.add_argument('-d', '--directory', dest="directory", default='', help="if given, this path will be prepended to every entry returned (defaults to '%(default)s')")
    dumpfold_parser.add_argument('-e', '--extension', dest="extension", default='', help="if given, this extension will be appended to every entry returned (defaults to '%(default)s')")
    dumpfold_parser.add_argument('--nf', '--fold_no', dest="fold_no", type=int, default=0, help="the number of fold whose files you would like to dump. (defaults to '%(default)s')")
    dumpfold_parser.add_argument('-s', '--subset', dest="subset", default='', help="specifies whether the dumped files should from the validation or the training subset for that particular fold (defaults to '%(default)s')", choices=('training', 'validation'))
    dumpfold_parser.add_argument('--self-test', dest="selftest", default=False, action='store_true', help=SUPPRESS)
    dumpfold_parser.set_defaults(func=dumpfold) #action
