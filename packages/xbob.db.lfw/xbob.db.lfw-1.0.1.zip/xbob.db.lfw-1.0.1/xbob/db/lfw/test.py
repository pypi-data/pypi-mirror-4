#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <laurent.el-shafey@idiap.ch>
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

"""A few checks at the Labeled Faces in the Wild database.
"""

import os, sys
import unittest
from .query import Database

class LfwDatabaseTest(unittest.TestCase):
  """Performs various tests on the Labeled Faces in the Wild database."""

  # expected numbers of clients
  expected_clients = {
      'view1': (4038, 1711, 0),
      'fold1': (3959, 1189, 601),
      'fold2': (3984, 1210, 555),
      'fold3': (4041, 1156, 552),
      'fold4': (4082, 1107, 560),
      'fold5': (4070, 1112, 567),
      'fold6': (4095, 1127, 527),
      'fold7': (4058, 1094, 597),
      'fold8': (4024, 1124, 601),
      'fold9': (3971, 1198, 580),
      'fold10': (3959, 1181, 609)
    }

  expected_models = {
      'view1': (3443, 853, 0),
      'fold1': (5345, 916, 472),
      'fold2': (5333, 930, 462),
      'fold3': (5381, 934, 440),
      'fold4': (5434, 902, 459),
      'fold5': (5473, 899, 436),
      'fold6': (5467, 895, 441),
      'fold7': (5408, 877, 476),
      'fold8': (5360, 917, 462),
      'fold9': (5339, 938, 458),
      'fold10': (5367, 920, 458)
    }

  expected_probes = {
      'view1': (863, 0),
      'fold1': (931, 473),
      'fold2': (947, 454),
      'fold3': (927, 439),
      'fold4': (893, 451),
      'fold5': (890, 449),
      'fold6': (900, 450),
      'fold7': (899, 467),
      'fold8': (917, 462),
      'fold9': (929, 457),
      'fold10': (919, 474)
    }

  expected_restricted_training_images = {
      'view1': 3443,
      'fold1': 2267,
      'fold2': 2228,
      'fold3': 2234,
      'fold4': 2293,
      'fold5': 2341,
      'fold6': 2362,
      'fold7': 2334,
      'fold8': 2356,
      'fold9': 2368,
      'fold10': 2320
    }

  expected_unrestricted_training_images = {
      'view1': 9525,
      'fold1': 8874,
      'fold2': 8714,
      'fold3': 9408,
      'fold4': 9453,
      'fold5': 9804,
      'fold6': 9727,
      'fold7': 9361,
      'fold8': 9155,
      'fold9': 9114,
      'fold10': 9021
    }


  def test01_clients(self):
    # Tests if the clients() and models() functions work as expected
    db = Database()
    # check the number of clients per protocol
    for p,l in self.expected_clients.iteritems():
      self.assertEqual(len(db.clients(protocol=p, groups='world')), l[0])
      self.assertEqual(len(db.clients(protocol=p, groups='dev')), l[1])
      self.assertEqual(len(db.clients(protocol=p, groups='eval')), l[2])

    # check the number of models per protocol
    for p,l in self.expected_models.iteritems():
      self.assertEqual(len(db.models(protocol=p, groups='world')), l[0])
      self.assertEqual(len(db.models(protocol=p, groups='dev')), l[1])
      self.assertEqual(len(db.models(protocol=p, groups='eval')), l[2])


  def test02_objects(self):
    # Tests if the files() function returns the expected number and type of files
    db = Database()
    # check that the files() function returns the same number of elements as the models() function does
    for p,l in self.expected_models.iteritems():
      self.assertEqual(len(db.objects(protocol=p, groups='world')), l[0])
      self.assertEqual(len(db.objects(protocol=p, groups='dev', purposes='enrol')), l[1])
      self.assertEqual(len(db.objects(protocol=p, groups='eval', purposes='enrol')), l[2])

    # check the number of probe files is correct
    for p,l in self.expected_probes.iteritems():
      self.assertEqual(len(db.objects(protocol=p, groups='dev', purposes='probe')), l[0])
      self.assertEqual(len(db.objects(protocol=p, groups='eval', purposes='probe')), l[1])

    # also check that the training files in the restricted configuration fit
    for p,l in self.expected_restricted_training_images.iteritems():
      self.assertEqual(len(db.objects(protocol=p, groups='world', subworld='threefolds')), l)

    # check that the probe files sum up to 1000 (view1) or 600 (view2)
    for p in self.expected_models.iterkeys():
      expected_probe_count = len(db.pairs(protocol=p, groups='dev'))
      # count the probes for each model
      current_probe_count = 0
      models = db.models(protocol=p, groups='dev')
      for model_id in [model.id for model in models]:
        current_probe_count += len(db.objects(protocol=p, groups='dev', purposes='probe', model_ids = (model_id,)))
      # assure that the number of probes is equal to the number of pairs
      self.assertEqual(current_probe_count, expected_probe_count)


  def test03_pairs(self):
    # Tests if the pairs() function returns the desired output
    db = Database()
    # check the number of pairs
    numbers = ((2200, 1000, 0), (4200, 1200, 600))
    index = 10
    for p in sorted(self.expected_models.keys()):
      self.assertEqual(len(db.pairs(protocol=p, groups='world')), numbers[index > 0][0])
      self.assertEqual(len(db.pairs(protocol=p, groups='dev')), numbers[index > 0][1])
      self.assertEqual(len(db.pairs(protocol=p, groups='eval')), numbers[index > 0][2])
      # evil trick to get the first 10 times the numbers for view2, and once the numbers for view1
      index -= 1


  def test04_unrestricted(self):
    # Tests the unrestricted configuration
    db = Database()
    # check that the training files in the unrestricted configuration fit
    for p,l in self.expected_unrestricted_training_images.iteritems():
      self.assertEqual(len(db.objects(protocol=p, groups='world', world_type='unrestricted')), l)
      # for dev and eval, restricted and unrestricted should return the same number of files
      self.assertEqual(len(db.objects(protocol=p, groups='dev', purposes='enrol', world_type='unrestricted')), self.expected_models[p][1])
      self.assertEqual(len(db.objects(protocol=p, groups='eval', purposes='enrol', world_type='unrestricted')), self.expected_models[p][2])
      self.assertEqual(len(db.objects(protocol=p, groups='dev', purposes='probe', world_type='unrestricted')), self.expected_probes[p][0])
      self.assertEqual(len(db.objects(protocol=p, groups='eval', purposes='probe', world_type='unrestricted')), self.expected_probes[p][1])


  def test05_driver_api(self):
    from bob.db.script.dbmanage import main
    self.assertEqual(main('lfw dumplist --self-test'.split()), 0)
    self.assertEqual(main('lfw dumplist --protocol=fold8 --group=dev --purpose=enrol --self-test'.split()), 0)
    self.assertEqual(main('lfw dumppairs --self-test'.split()), 0)
    self.assertEqual(main('lfw dumppairs --protocol=fold8 --group=dev --class=client --self-test'.split()), 0)
    self.assertEqual(main('lfw checkfiles --self-test'.split()), 0)
    self.assertEqual(main('lfw reverse Thomas_Watjen/Thomas_Watjen_0001 --self-test'.split()), 0)
    self.assertEqual(main('lfw path Thomas_Watjen_0001 --self-test'.split()), 0)

