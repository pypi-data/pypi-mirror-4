#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date:   Mon Dec 10 14:29:51 CET 2012
#
# Copyright (C) 2011-2012 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""A few checks for the CAS-PEAL database.
"""

import os, sys
import unittest
import xbob.db.caspeal
import random

class CasPealDatabaseTest(unittest.TestCase):
  """Performs various tests on the CAS-PEAL database."""

  def test01_clients(self):
    db = xbob.db.caspeal.Database()

    # test that the expected number of clients is returned
    self.assertEqual(len(db.client_ids()), 1040)
    self.assertEqual(len(db.client_ids(genders='M')), 595)
    self.assertEqual(len(db.client_ids(genders='F')), 445)
    self.assertEqual(len(db.client_ids(ages='Y')), 1026)
    self.assertEqual(len(db.client_ids(ages='M')), 10)
    self.assertEqual(len(db.client_ids(ages='O')), 4)
    self.assertEqual(len(db.client_ids(groups='world')), 300)
    self.assertEqual(len(db.client_ids(groups='dev')), 1040)

    self.assertEqual(db.model_ids(), [client.id for client in db.clients()])


  def test02_objects(self):
    db = xbob.db.caspeal.Database()

    # test that the objects() function returns reasonable numbers of files
    self.assertEqual(len(db.objects()), 31064 if db.has_protocol('pose') else 9232)

    # number of world files for the two genders
    self.assertEqual(len(db.objects(groups='world')), 1200)
    self.assertEqual(len(db.objects(groups='world', genders='F')), 512)
    self.assertEqual(len(db.objects(groups='world', genders='M')), 688)
    # no world files for a pose other than 'M+00'
    self.assertEqual(len(db.objects(groups='world', poses='M+00')), 1200)
    self.assertEqual(len(db.objects(groups='world', poses='D+45')), 0)

    # enroll files are independent from the protocol
    self.assertEqual(len(db.objects(groups='dev', purposes='enrol')), 1040)

    # probe files, see description of the database
    self.assertEqual(len(db.objects(groups='dev', purposes='probe', protocol='accessory')), 2285)
    self.assertEqual(len(db.objects(groups='dev', purposes='probe', protocol='aging')), 66)
    self.assertEqual(len(db.objects(groups='dev', purposes='probe', protocol='background')), 553)
    self.assertEqual(len(db.objects(groups='dev', purposes='probe', protocol='distance')), 275)
    self.assertEqual(len(db.objects(groups='dev', purposes='probe', protocol='expression')), 1570)
    self.assertEqual(len(db.objects(groups='dev', purposes='probe', protocol='lighting')), 2243)

    # This does not work. It seems that there are more images than given in the database description
    #self.assertEqual(len(db.objects(groups='dev', purposes='probe', protocol='pose')), 4998+4993+4998)
    # On the web-page they claim to have 21840 pose images (3 elevations * 7 azimuth * 1040 people)
    # but it seems that we ar missing some files...
    if db.has_protocol('pose'):
      self.assertEqual(len(db.objects(groups='dev', purposes='probe', protocol='pose')), 21832)
      # all pose images have neutral expression, frontal light, no accessoriesm the same distance, were taken at the same session with the same background
      self.assertEqual(len(db.objects(groups='dev', purposes='probe', protocol='pose', expressions='N', lightings='EU+00', accessories=0, distances=0, sessions=0, backgrounds='B')), 21832)


  def test03_annotations(self):
    # Tests that the annotations are available for all files
    db = xbob.db.caspeal.Database()

    # we test only one of the protocols
    for protocol in random.sample(db.m_protocols, 1):
      files = db.objects(protocol=protocol)
      # ...and some of the files
      for file in random.sample(files, 1000):
        annotations = db.annotations(file.id)
        self.assertTrue('leye' in annotations and 'reye' in annotations)
        self.assertEqual(len(annotations['leye']), 2)
        self.assertEqual(len(annotations['reye']), 2)

  def test04_driver_api(self):
    from bob.db.script.dbmanage import main
    self.assertEqual(main('caspeal dumplist --self-test'.split()), 0)
    self.assertEqual(main('caspeal dumplist  --group=dev --purpose=enrol --client=622 --protocol=aging --session=0 --gender=F --expression=N --lighting=EU+00 --pose=M+00 --distance=0 --accessory=0 --age=Y --background=B --self-test'.split()), 0)
    self.assertEqual(main('caspeal checkfiles --self-test'.split()), 0)
    self.assertEqual(main('caspeal reverse FRONTAL/Aging/MY_000064_IEU+00_PM+00_EN_A0_D0_T2_BB_M0_R1_S0 --self-test'.split()), 0)
    self.assertEqual(main('caspeal path 42 --self-test'.split()), 0)

