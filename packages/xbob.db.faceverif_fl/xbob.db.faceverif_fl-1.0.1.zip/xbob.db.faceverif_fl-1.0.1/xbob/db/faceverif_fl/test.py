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

"""A few checks at the Face Verification File Lists database.
"""

import os, sys
import unittest
from .query import Database

class Faceverif_flDatabaseTest(unittest.TestCase):
  """Performs various tests on the Face Verification File Lists database."""

  def test01_query(self):
    from pkg_resources import resource_filename
    example_data = resource_filename(__name__, 'example_fl')
    db = Database(example_data, use_dense_probe_file_list = False)

    self.assertEqual(len(db.client_ids()), 6) # 6 client ids for world, dev and eval
    self.assertEqual(len(db.client_ids(groups='world')), 2) # 2 client ids for world
    self.assertEqual(len(db.client_ids(groups='dev')), 2) # 2 client ids for dev
    self.assertEqual(len(db.client_ids(groups='eval')), 2) # 2 client ids for eval

    self.assertEqual(len(db.tclient_ids()), 2) # 2 client ids for T-Norm score normalization
    self.assertEqual(len(db.zclient_ids()), 2) # 2 client ids for Z-Norm score normalization

    self.assertEqual(len(db.model_ids()), 6) # 6 model ids for world, dev and eval
    self.assertEqual(len(db.model_ids(groups='world')), 2) # 2 model ids for world
    self.assertEqual(len(db.model_ids(groups='dev')), 2) # 2 model ids for dev
    self.assertEqual(len(db.model_ids(groups='eval')), 2) # 2 model ids for eval

    self.assertEqual(len(db.tmodel_ids()), 2) # 2 model ids for T-Norm score normalization

    self.assertEqual(len(db.objects(groups='world')), 8) # 8 samples in the world set

    self.assertEqual(len(db.objects(groups='dev', purposes='enrol')), 8) # 8 samples for enrollment in the dev set
    self.assertEqual(len(db.objects(groups='dev', purposes='enrol', model_ids='3')), 4) # 4 samples for to enroll model '3' in the dev set
    self.assertEqual(len(db.objects(groups='dev', purposes='enrol', model_ids='7')), 0) # 0 samples for enrolling model '7' (it is a T-Norm model)
    self.assertEqual(len(db.objects(groups='dev', purposes='probe')), 8) # 8 samples as probes in the dev set
    self.assertEqual(len(db.objects(groups='dev', purposes='probe', classes='client')), 8) # 8 samples as client probes in the dev set
    self.assertEqual(len(db.objects(groups='dev', purposes='probe', classes='impostor')), 4) # 4 samples as impostor probes in the dev set

    self.assertEqual(len(db.tobjects(groups='dev')), 8) # 8 samples for enrolling T-norm models
    self.assertEqual(len(db.tobjects(groups='dev', model_ids='7')), 4) # 4 samples for enrolling T-norm model '7'
    self.assertEqual(len(db.tobjects(groups='dev', model_ids='3')), 0) # 0 samples for enrolling T-norm model '3' (no T-Norm model)
    self.assertEqual(len(db.zobjects(groups='dev')), 8) # 8 samples for Z-norm impostor accesses

    self.assertEqual(db.get_client_id_from_model_id('1'), '1')
    self.assertEqual(db.get_client_id_from_model_id('3'), '3')
    self.assertEqual(db.get_client_id_from_model_id('6'), '6')
    self.assertEqual(db.get_client_id_from_tmodel_id('7'), '7')


  def test02_query_dense(self):
    from pkg_resources import resource_filename
    example_data = resource_filename(__name__, 'example_fl')
    db = Database(example_data, probes_filename = 'for_probes.lst')

    self.assertEqual(len(db.objects(groups='world')), 8) # 8 samples in the world set

    self.assertEqual(len(db.objects(groups='dev', purposes='enrol')), 8) # 8 samples for enrollment in the dev set
    self.assertEqual(len(db.objects(groups='dev', purposes='probe')), 8) # 8 samples as probes in the dev set


  def test03_driver_api(self):
    from bob.db.script.dbmanage import main
    from pkg_resources import resource_filename
    example_data = resource_filename(__name__, 'example_fl')
    self.assertEqual(main(('faceverif_fl dumplist --list-directory=%s --self-test' % example_data).split()), 0)
    self.assertEqual(main(('faceverif_fl dumplist --list-directory=%s --purpose=enrol --group=dev --class=client --self-test' % example_data).split()), 0)
    self.assertEqual(main(('faceverif_fl checkfiles --list-directory=%s --self-test' % example_data).split()), 0)


