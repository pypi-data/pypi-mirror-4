#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Ivana Chingovska <ivana.chingovska@idiap.ch>
# Tue Mar  6 11:26:33 CET 2012
#
# Copyright (C) 2011-2012 Idiap Research Institute, Martigny, Switzerland
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""A few checks at the CASIA_FASD database.
"""

import os, sys
import unittest
from . import Database

class FASDDatabaseTest(unittest.TestCase):
  """Performs various tests on the CASIA_FASD spoofing attack database."""

  """
  def test01_query(self):
    db = Database()
    
    f = db.files()
    self.assertEqual(len(set(f.values())), 600) # number of all the videos in the database

    f = db.files(groups='train', ids=[21])
    self.assertEqual(len(set(f.values())), 0) # number of train videos for client 21
   
    f = db.files(groups='test', cls='real')
    self.assertEqual(len(set(f.values())), 90) # number of real test videos (30 clients * 3 qualitites)
    
    f = db.files(groups='test', cls='real', types='cut')
    self.assertEqual(len(set(f.values())), 0) # number of real test videos - cut attacks (can not be real and attacks at the same time of course)

    f = db.files(groups='train', cls='real', qualities='low')
    self.assertEqual(len(set(f.values())), 20) # number of real train videos with low quality (20 clients * 1 real low quality video)

    f = db.files(groups='train', cls='attack', qualities='normal')
    self.assertEqual(len(set(f.values())), 60) # number of real train videos with normal quality (20 clients * 3 attack types)

    f = db.files(groups='test', qualities='high')
    self.assertEqual(len(set(f.values())), 120) # number of real test videos with high quality (30 clients * 4 attack types)
    
    f = db.files(groups='test', types='warped')
    self.assertEqual(len(set(f.values())), 90) # number of test warped videos (30 clients * 3 qualities)

    f = db.files(groups='test', types='video', qualities='high', ids=[1,2,3])
    self.assertEqual(len(set(f.values())), 0) # clients with ids 1, 2 and 3 are not in the test set

    f = db.files(groups='train', types='video', qualities='high', ids=[1,2,3])
    self.assertEqual(len(set(f.values())), 3) # number of high quality video attacks of clients 1, 2 and 3 (3 clients * 1)
   
    f = db.files(directory = 'xxx', extension='.avi', groups='train', types='video', qualities='high', ids=1)
    self.assertEqual(len(set(f.values())), 1) # number of high quality video attacks of client 1(1 client * 1)
    self.assertEqual(f[0], 'xxx/train_release/1/HR_4.avi')
  """

  
  def test02_cross_valid(self): # testing the cross-validation subsets
    db = Database()
    '''
    db.cross_valid_gen(60, 60, 5) # 60 is the number of real samples as well as in each attack type of the database
    '''
    subsets_real, subsets_attack = db.cross_valid_read()
    self.assertEqual(len(subsets_real), 5)
    self.assertEqual(len(subsets_attack), 5)
    for i in range(0,5):
      self.assertEqual(len(subsets_real[i]), 12)
      self.assertEqual(len(subsets_attack[i]), 12)
    files_real_val, files_real_train = db.cross_valid_foldobjects(cls='real', fold_no=1)
    self.assertEqual(len(files_real_val), 12) # number of samples in validation subset of real accesses
    self.assertEqual(len(files_real_train), 48) # number of samples in training subset of real accesses
    files_real_val, files_real_train = db.cross_valid_foldobjects(types='warped', cls='attack', fold_no=2)
    self.assertEqual(len(files_real_val), 12) # number of samples in validation subset of warped attacks
    self.assertEqual(len(files_real_train), 48) # number of samples in training subset of warped attacks
    files_real_val, files_real_train = db.cross_valid_foldobjects(types=('warped', 'cut'), cls='attack', fold_no=3)
    self.assertEqual(len(files_real_val), 24) # number of samples in validation subset of warped and cut attacks
    self.assertEqual(len(files_real_train), 96) # number of samples in training subset of of warped and cut attacks
    files_real_val, files_real_train = db.cross_valid_foldobjects(types=('warped', 'cut', 'video'), cls='attack', fold_no=4)
    self.assertEqual(len(files_real_val), 36) # number of samples in validation subset of all attacks
    self.assertEqual(len(files_real_train), 144) # number of samples in training subset of all attacks
    files_real_val, files_real_train = db.cross_valid_foldobjects(types=None, cls='attack', fold_no=4)
    self.assertEqual(len(files_real_val), 36) # number of samples in validation subset of all attacks
    self.assertEqual(len(files_real_train), 144) # number of samples in training subset of all attacks
  

  def test03_dumplist(self):
    from bob.db.script.dbmanage import main
    self.assertEqual(main('casia_fasd dumplist --self-test'.split()), 0)

  def test04_checkfiles(self):
    from bob.db.script.dbmanage import main
    self.assertEqual(main('casia_fasd checkfiles --self-test'.split()), 0)
  
  def test05_manage_files(self):

    from bob.db.script.dbmanage import main

    self.assertEqual(main('casia_fasd files'.split()), 0)

  def test06_query_obj(self):
    db = Database()
    
    fobj = db.objects()
    self.assertEqual(len(fobj), 600) # number of all the videos in the database

    fobj = db.objects(groups='train', ids=[21])
    self.assertEqual(len(fobj), 0) # number of train videos for client 21
   
    fobj = db.objects(groups='test', cls='real')
    self.assertEqual(len(fobj), 90) # number of real test videos (30 clients * 3 qualitites)
    
    fobj = db.objects(groups='test', cls='real', types='cut')
    self.assertEqual(len(fobj), 0) # number of real test videos - cut attacks (can not be real and attacks at the same time of course)

    fobj = db.objects(groups='train', cls='real', qualities='low')
    self.assertEqual(len(fobj), 20) # number of real train videos with low quality (20 clients * 1 real low quality video)

    fobj = db.objects(groups='train', cls='attack', qualities='normal')
    self.assertEqual(len(fobj), 60) # number of real train videos with normal quality (20 clients * 3 attack types)

    fobj = db.objects(groups='test', qualities='high')
    self.assertEqual(len(fobj), 120) # number of real test videos with high quality (30 clients * 4 attack types)
    
    fobj = db.objects(groups='test', types='warped')
    self.assertEqual(len(fobj), 90) # number of test warped videos (30 clients * 3 qualities)

    fobj = db.objects(groups='test', types='video', qualities='high', ids=[1,2,3])
    self.assertEqual(len(fobj), 0) # clients with ids 1, 2 and 3 are not in the test set

    fobj = db.objects(groups='train', types='video', qualities='high', ids=[1,2,3])
    self.assertEqual(len(fobj), 3) # number of high quality video attacks of clients 1, 2 and 3 (3 clients * 1)
   
    fobj = db.objects(groups='train', types='video', qualities='high', ids=1)
    self.assertEqual(len(fobj), 1) # number of high quality video attacks of client 1(1 client * 1)
    self.assertEqual(fobj[0].filename, 'train_release/1/HR_4')
    self.assertEqual(fobj[0].make_path('xxx', '.avi'), 'xxx/train_release/1/HR_4.avi')

    fobj = db.objects(groups='test', types='warped', qualities='low', ids=21)
    self.assertEqual(len(fobj), 1) # number of high quality video attacks of client 21 (1 client * 1)
    self.assertFalse(fobj[0].is_real())
    self.assertEqual(fobj[0].get_clientid(), 21)
    self.assertEqual(fobj[0].get_type(), 'warped')
    self.assertEqual(fobj[0].get_quality(), 'low')
    self.assertTrue(os.path.exists(fobj[0].facefile()))
    
