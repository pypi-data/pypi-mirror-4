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

"""A few checks at the SCface database.
"""

import os, sys
import unittest
from .query import Database
from .models import *

class SCfaceDatabaseTest(unittest.TestCase):
  """Performs various tests on the SCface database."""

  def test01_clients(self):

    db = Database()

    clients = db.clients()
    self.assertEqual(len(clients), 130) #130 clients used by the protocols
    # Number of clients in each set
    c_dev = db.clients(groups='dev')
    self.assertEqual(len(c_dev), 44) #43 clients in the dev set
    c_eval = db.clients(groups='eval')
    self.assertEqual(len(c_eval), 43) #44 clients in the eval set
    c_world = db.clients(groups='world')
    self.assertEqual(len(c_world), 43) #43 clients in the world set
    # Check client ids
    self.assertTrue(db.has_client_id(1))
    self.assertFalse(db.has_client_id(395))
    # Check subworld
    self.assertEqual(len(db.clients(groups='world', subworld='onethird')), 14)
    self.assertEqual(len(db.clients(groups='world', subworld='twothirds')), 29)
    # Check files relationship
    c = db.client(1)
    self.assertEqual(len(c.files), 22)

  def test02_protocols(self):

    db = Database()

    self.assertEqual(len(db.protocols()), 4)
    self.assertEqual(len(db.protocol_names()), 4)
    self.assertTrue(db.has_protocol('combined'))

    self.assertEqual(len(db.subworlds()), 2)
    self.assertEqual(len(db.subworld_names()), 2)
    self.assertTrue(db.has_subworld('onethird'))

  def test03_objects(self):

    db = Database()

    # Protocol combined
    # World group
    self.assertEqual(len(db.objects(protocol='combined', groups='world')), 688)
    self.assertEqual(len(db.objects(protocol='combined', groups='world', purposes='train')), 688)
    self.assertEqual(len(db.objects(protocol='combined', groups='world', purposes='train', model_ids=3)), 16)

    # Dev group
    self.assertEqual(len(db.objects(protocol='combined', groups='dev')), 704)
    self.assertEqual(len(db.objects(protocol='combined', groups='dev', purposes='enrol')), 44)
    self.assertEqual(len(db.objects(protocol='combined', groups='dev', purposes='probe')), 660)
    self.assertEqual(len(db.objects(protocol='combined', groups='dev', purposes='probe', classes='client')), 660)
    self.assertEqual(len(db.objects(protocol='combined', groups='dev', purposes='probe', classes='impostor')), 660)
    self.assertEqual(len(db.objects(protocol='combined', groups='dev', purposes='probe', classes='client', model_ids=47)), 15)
    self.assertEqual(len(db.objects(protocol='combined', groups='dev', purposes='probe', classes='impostor', model_ids=47)), 645)

    # Eval group
    self.assertEqual(len(db.objects(protocol='combined', groups='eval')), 688)
    self.assertEqual(len(db.objects(protocol='combined', groups='eval', purposes='enrol')), 43)
    self.assertEqual(len(db.objects(protocol='combined', groups='eval', purposes='probe')), 645)
    self.assertEqual(len(db.objects(protocol='combined', groups='eval', purposes='probe', classes='client')), 645)
    self.assertEqual(len(db.objects(protocol='combined', groups='eval', purposes='probe', classes='impostor')), 645)
    self.assertEqual(len(db.objects(protocol='combined', groups='eval', purposes='probe', classes='client', model_ids=100)), 15)
    self.assertEqual(len(db.objects(protocol='combined', groups='eval', purposes='probe', classes='impostor', model_ids=100)), 630)

    # Protocol close
    # World group
    self.assertEqual(len(db.objects(protocol='close', groups='world')), 688)
    self.assertEqual(len(db.objects(protocol='close', groups='world', purposes='train')), 688)
    self.assertEqual(len(db.objects(protocol='close', groups='world', purposes='train', model_ids=3)), 16)

    # Dev group
    self.assertEqual(len(db.objects(protocol='close', groups='dev')), 264)
    self.assertEqual(len(db.objects(protocol='close', groups='dev', purposes='enrol')), 44)
    self.assertEqual(len(db.objects(protocol='close', groups='dev', purposes='probe')), 220)
    self.assertEqual(len(db.objects(protocol='close', groups='dev', purposes='probe', classes='client')), 220)
    self.assertEqual(len(db.objects(protocol='close', groups='dev', purposes='probe', classes='impostor')), 220)
    self.assertEqual(len(db.objects(protocol='close', groups='dev', purposes='probe', classes='client', model_ids=47)), 5)
    self.assertEqual(len(db.objects(protocol='close', groups='dev', purposes='probe', classes='impostor', model_ids=47)), 215)

    # Eval group
    self.assertEqual(len(db.objects(protocol='close', groups='eval')), 258)
    self.assertEqual(len(db.objects(protocol='close', groups='eval', purposes='enrol')), 43)
    self.assertEqual(len(db.objects(protocol='close', groups='eval', purposes='probe')), 215)
    self.assertEqual(len(db.objects(protocol='close', groups='eval', purposes='probe', classes='client')), 215)
    self.assertEqual(len(db.objects(protocol='close', groups='eval', purposes='probe', classes='impostor')), 215)
    self.assertEqual(len(db.objects(protocol='close', groups='eval', purposes='probe', classes='client', model_ids=100)), 5)
    self.assertEqual(len(db.objects(protocol='close', groups='eval', purposes='probe', classes='impostor', model_ids=100)), 210)

    # Protocol medium
    # World group
    self.assertEqual(len(db.objects(protocol='medium', groups='world')), 688)
    self.assertEqual(len(db.objects(protocol='medium', groups='world', purposes='train')), 688)
    self.assertEqual(len(db.objects(protocol='medium', groups='world', purposes='train', model_ids=3)), 16)

    # Dev group
    self.assertEqual(len(db.objects(protocol='medium', groups='dev')), 264)
    self.assertEqual(len(db.objects(protocol='medium', groups='dev', purposes='enrol')), 44)
    self.assertEqual(len(db.objects(protocol='medium', groups='dev', purposes='probe')), 220)
    self.assertEqual(len(db.objects(protocol='medium', groups='dev', purposes='probe', classes='client')), 220)
    self.assertEqual(len(db.objects(protocol='medium', groups='dev', purposes='probe', classes='impostor')), 220)
    self.assertEqual(len(db.objects(protocol='medium', groups='dev', purposes='probe', classes='client', model_ids=47)), 5)
    self.assertEqual(len(db.objects(protocol='medium', groups='dev', purposes='probe', classes='impostor', model_ids=47)), 215)

    # Eval group
    self.assertEqual(len(db.objects(protocol='medium', groups='eval')), 258)
    self.assertEqual(len(db.objects(protocol='medium', groups='eval', purposes='enrol')), 43)
    self.assertEqual(len(db.objects(protocol='medium', groups='eval', purposes='probe')), 215)
    self.assertEqual(len(db.objects(protocol='medium', groups='eval', purposes='probe', classes='client')), 215)
    self.assertEqual(len(db.objects(protocol='medium', groups='eval', purposes='probe', classes='impostor')), 215)
    self.assertEqual(len(db.objects(protocol='medium', groups='eval', purposes='probe', classes='client', model_ids=100)), 5)
    self.assertEqual(len(db.objects(protocol='medium', groups='eval', purposes='probe', classes='impostor', model_ids=100)), 210)

    # Protocol far
    # World group
    self.assertEqual(len(db.objects(protocol='far', groups='world')), 688)
    self.assertEqual(len(db.objects(protocol='far', groups='world', purposes='train')), 688)
    self.assertEqual(len(db.objects(protocol='far', groups='world', purposes='train', model_ids=3)), 16)

    # Dev group
    self.assertEqual(len(db.objects(protocol='far', groups='dev')), 264)
    self.assertEqual(len(db.objects(protocol='far', groups='dev', purposes='enrol')), 44)
    self.assertEqual(len(db.objects(protocol='far', groups='dev', purposes='probe')), 220)
    self.assertEqual(len(db.objects(protocol='far', groups='dev', purposes='probe', classes='client')), 220)
    self.assertEqual(len(db.objects(protocol='far', groups='dev', purposes='probe', classes='impostor')), 220)
    self.assertEqual(len(db.objects(protocol='far', groups='dev', purposes='probe', classes='client', model_ids=47)), 5)
    self.assertEqual(len(db.objects(protocol='far', groups='dev', purposes='probe', classes='impostor', model_ids=47)), 215)

    # Eval group
    self.assertEqual(len(db.objects(protocol='far', groups='eval')), 258)
    self.assertEqual(len(db.objects(protocol='far', groups='eval', purposes='enrol')), 43)
    self.assertEqual(len(db.objects(protocol='far', groups='eval', purposes='probe')), 215)
    self.assertEqual(len(db.objects(protocol='far', groups='eval', purposes='probe', classes='client')), 215)
    self.assertEqual(len(db.objects(protocol='far', groups='eval', purposes='probe', classes='impostor')), 215)
    self.assertEqual(len(db.objects(protocol='far', groups='eval', purposes='probe', classes='client', model_ids=100)), 5)
    self.assertEqual(len(db.objects(protocol='far', groups='eval', purposes='probe', classes='impostor', model_ids=100)), 210)

    # TODO: T-norm and Z-norm files

  def test04_driver_api(self):

    from bob.db.script.dbmanage import main
    self.assertEqual(main('scface dumplist --self-test'.split()), 0)
    self.assertEqual(main('scface dumplist --protocol=combined --class=client --group=dev --purpose=enrol --client=66 --self-test'.split()), 0)
    self.assertEqual(main('scface checkfiles --self-test'.split()), 0)
    self.assertEqual(main('scface reverse mugshot_frontal_cropped_all/066_frontal --self-test'.split()), 0)
    self.assertEqual(main('scface path 65 --self-test'.split()), 0)

