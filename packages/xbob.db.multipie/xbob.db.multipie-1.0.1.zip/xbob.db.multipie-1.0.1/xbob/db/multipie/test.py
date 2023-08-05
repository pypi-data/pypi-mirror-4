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

"""A few checks at the Multi-PIE database.
"""

import os, sys
import unittest
from .query import Database

class MultipieDatabaseTest(unittest.TestCase):
  """Performs various tests on the Multi-PIE database."""

  def test01_clients(self):

    db = Database()

    clients = db.clients()
    self.assertEqual(len(clients), 337) #337 clients overall
    # Number of clients in each set
    c_dev = db.clients(groups='dev')
    self.assertEqual(len(c_dev), 64) #64 clients in the dev set
    c_eval = db.clients(groups='eval')
    self.assertEqual(len(c_eval), 65) #65 clients in the eval set
    c_world = db.clients(groups='world')
    self.assertEqual(len(c_world), 208) #208 clients in the world set
    # Check client ids
    self.assertTrue(db.has_client_id(1))
    self.assertFalse(db.has_client_id(395))
    # Check subworld
    self.assertEqual(len(db.clients(groups='world', subworld='sub41')), 41)
    self.assertEqual(len(db.clients(groups='world', subworld='sub81')), 81)
    self.assertEqual(len(db.clients(groups='world', subworld='sub121')), 121)
    self.assertEqual(len(db.clients(groups='world', subworld='sub161')), 161)

    # check models and t-models
    self.assertEqual(len(db.model_ids(groups='dev')), 64)
    self.assertEqual(len(db.model_ids(groups='eval')), 65)
    self.assertEqual(len(db.tmodel_ids(groups='dev')), 65)
    self.assertEqual(len(db.tmodel_ids(groups='eval')), 64)

    # Check files relationship
    c = db.client(1)
    len(c.files) # Number depends on the way the database was created (pose only, etc.)

  def test02_protocols(self):

    db = Database()

    # TODO: Depends on the way the database was created (pose only, etc.)
    #self.assertEqual(len(db.protocols()), 4)
    #self.assertEqual(len(db.protocol_names()), 4)
    #self.assertTrue(db.has_protocol('M'))

    self.assertEqual(len(db.subworlds()), 4)
    self.assertEqual(len(db.subworld_names()), 4)
    self.assertTrue(db.has_subworld('sub41'))

  def test03_files(self):

    # TODO: depends on the way the database was created (pose only, etc.)
    db = Database()

    # TODO: better tests for this
    self.assertTrue(len(db.objects()) > 0)
    self.assertTrue(len(db.zobjects()) > 0)
    self.assertTrue(len(db.tobjects()) > 0)

  def test04_driver_api(self):

    from bob.db.script.dbmanage import main

    db = Database()
    self.assertEqual(main('multipie dumplist --self-test'.split()), 0)
    if db.has_protocol('M'):
      self.assertEqual(main('multipie dumplist --protocol=M --class=client --group=dev --purpose=enrol --self-test'.split()), 0)
    elif db.has_protocol('P051'):
      self.assertEqual(main('multipie dumplist --protocol=P051 --class=client --group=dev --purpose=enrol --self-test'.split()), 0)
    self.assertEqual(main('multipie checkfiles --self-test'.split()), 0)
    self.assertEqual(main('multipie reverse session02/multiview/108/01/05_1/108_02_01_051_17 --self-test'.split()), 0)
    self.assertEqual(main('multipie path 6578 --self-test'.split()), 0)

