#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiagofrepereira@gmail.com>
# Tue 01 Oct 2012 16:48:44 CEST 

"""CASIA Face-AntiSpoofing Database (FASD) implementation as antispoofing.utils.db.Database."""

import os
from . import __doc__ as long_description
from . import File as CasiaFASDFile, Database as CasiaFASDDatabase
from antispoofing.utils.db import File as FileBase, Database as DatabaseBase

class File(FileBase):

  def __init__(self, f):
    """Initializes this File object with the xbob.db.casia_fasd.File equivalent"""
    self.__f = f

  def videofile(self, directory=None):
    return self.__f.videofile(directory=directory)
  videofile.__doc__ = FileBase.videofile.__doc__

  def facefile(self, directory=None):

    if directory!=None: 
      directory = os.path.join(directory, 'face-locations')
    return self.__f.facefile(directory=directory)
  facefile.__doc__ = FileBase.facefile.__doc__

  def bbx(self, directory=None):
    return self.__f.bbx(directory=directory)
  bbx.__doc__ = FileBase.bbx.__doc__

  def load(self, directory=None, extension='.hdf5'):
    return self.__f.load(directory=directory, extension=extension)
  load.__doc__ = FileBase.bbx.__doc__

  def save(self, data, directory=None, extension='.hdf5'):
    return self.__f.save(data, directory=directory, extension=extension)
  save.__doc__ = FileBase.save.__doc__

  def make_path(self, directory=None, extension=None):
    return self.__f.make_path(directory=directory, extension=extension)
  make_path.__doc__ = FileBase.make_path.__doc__

class Database(DatabaseBase):
  __doc__ = long_description

  def __init__ (self, args=None):
    self.__db = CasiaFASDDatabase()
    self.__kwargs = {}
    if args is not None:

      self.__kwargs = {
        'types': args.casia_types,
        'fold_no': args.casia_fold_number,
      }
  __init__.__doc__ = DatabaseBase.__init__.__doc__

  def create_subparser(self, subparser, entry_point_name):
    
    from argparse import RawDescriptionHelpFormatter

    ## remove '.. ' lines from rst
    desc = '\n'.join([k for k in self.long_description().split('\n') if k.strip().find('.. ') != 0])

    p = subparser.add_parser(entry_point_name, 
        help=self.short_description(),
        description=desc,
        formatter_class=RawDescriptionHelpFormatter)

    p.add_argument('--types', type=str, choices=self.__db.types, dest='casia_types', help='Defines the types of attack videos in the database that are going to be used (if not set return all types)')

    p.add_argument('--fold-number', choices=(1,2,3,4,5), type=int, default=1, dest='casia_fold_number', help='Number of the fold (defaults to %(default)s)')

    p.set_defaults(name=entry_point_name)
    p.set_defaults(cls=Database)
        
    return
  create_subparser.__doc__ = DatabaseBase.create_subparser.__doc__

  def short_description(self):
    return 'CASIA Face Anti-Spoofing database (FASD)'
  short_description.__doc__ = DatabaseBase.short_description.__doc__
 
  def long_description(self):
    return Database.__doc__
  long_description.__doc__ = DatabaseBase.long_description.__doc__
 
  def implements_any_of(self, propname):
    if isinstance(propname, (tuple,list)):
      return 'video' in propname
    elif propname is None:
      return True
    elif isinstance(propname, (str,unicode)):
      return 'video' == propname

    # does not implement the given access protocol
    return False
 
  def __parse_arguments(self):

    types = self.__kwargs.get('types', self.__db.types)
    if not types: types = self.__db.types
    return types, self.__kwargs.get('fold_no', 1)

  def get_train_data(self):

    types, fold_no = self.__parse_arguments()

    _, trainReal   = self.__db.cross_valid_foldobjects(cls='real', fold_no=fold_no)
    _, trainAttack = self.__db.cross_valid_foldobjects(cls='attack', types=types, fold_no=fold_no)

    return [File(f) for f in trainReal], [File(f) for f in trainAttack]
  get_train_data.__doc__ = DatabaseBase.get_train_data.__doc__

  def get_devel_data(self):
    __doc__ = DatabaseBase.get_devel_data.__doc__

    types, fold_no = self.__parse_arguments()

    develReal, _   = self.__db.cross_valid_foldobjects(cls='real', fold_no=fold_no)

    develAttack, _ = self.__db.cross_valid_foldobjects(cls='attack', types=types, fold_no=fold_no)
    
    return [File(f) for f in develReal], [File(f) for f in develAttack]
  get_devel_data.__doc__ = DatabaseBase.get_devel_data.__doc__

  def get_test_data(self):
    __doc__ = DatabaseBase.get_test_data.__doc__

    types, _ = self.__parse_arguments()

    testReal = self.__db.objects(groups='test', cls='real')
    testAttack = self.__db.objects(groups='test', cls='attack', types=types)

    return [File(f) for f in testReal], [File(f) for f in testAttack]
  get_test_data.__doc__ = DatabaseBase.get_test_data.__doc__

  def get_all_data(self):
    __doc__ = DatabaseBase.get_all_data.__doc__

    types, _ = self.__parse_arguments()

    allReal   = self.__db.objects(cls='real')
    allAttacks  = self.__db.objects(cls='attack',types=types)

    return [File(f) for f in allReal], [File(f) for f in allAttacks]
  get_all_data.__doc__ = DatabaseBase.get_all_data.__doc__
