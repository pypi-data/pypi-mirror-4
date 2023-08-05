#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date: Wed Oct 24 10:47:43 CEST 2012
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

"""
This file defines simple Client and File interfaces that should be comparable
with other xbob.db databases.
"""

import os
import bob
import fileinput
import re

import xbob.db.verification.utils

class Client:
  """The clients of this database contain ONLY client ids. Nothing special."""
  def __init__(self, client_id):
    self.id = client_id


class File (xbob.db.verification.utils.File):
  """Files of this database are composed from the client id, a file id, (a model id) and a claimed (client) id."""
  def __init__(self, file_name, client_id, model_id = None, claimed_id = None):
    # call base class constructor
    # the file id is the full file name
    xbob.db.verification.utils.File.__init__(self, file_id = file_name, path = file_name, client_id = client_id)

    # Note: in case of probe files, model ids are considered to be the ids of the model for the given probe file.
    # Hence, there might be several probe files with the same file id, but different model ids.
    # Therefore, please DO NOT USE the model_id outside of this class (or the according database queries).
    # when the model id is not specified, we use the client id instead
    self._model_id = client_id if model_id is None else model_id
    # when the claimed id is not specified, we use the client id instead
    self.claimed_id = client_id if claimed_id is None else claimed_id



#############################################################################
### internal access functions for the file lists; do not export!
#############################################################################

def _read_multi_column_list(list_file):
  rows = []
  if not os.path.isfile(list_file):
    raise RuntimeError, 'File %s does not exist.' % (list_file,)
  try:
    for line in fileinput.input(list_file):
      parsed_line = re.findall('[\w/(-.)]+', line)
      if len(parsed_line):
        # perform some sanity checks
        if len(parsed_line) not in (2,3,4):
          raise IOError("The read line '%s' from file '%s' could not be parsed successfully!" (line, list_file))
        if len(rows) and len(rows[0]) != len(parsed_line):
          raise IOError("The parsed line '%s' from file '%s' has a different number of elements than the first parsed line '%s'!" (parsed_line, list_file, rows[0]))
        # append the read line
        rows.append(parsed_line)
    fileinput.close()
  except IOError as e:
    raise RuntimeError, 'Error reading the file %s.' % (list_file,)

  # return the read list as a vector of columns
  return rows


def _read_column_list(list_file, column_count):
  # read the list
  rows = _read_multi_column_list(list_file)
  # extract the file from the first two columns
  file_list = []
  for row in rows:
    if column_count == 2:
      assert len(row) == 2
      # we expect: filename client_id
      file_list.append(File(file_name = row[0], client_id = row[1]))
    elif column_count == 3:
      assert len(row) in (2, 3)
      # we expect: filename, model_id, client_id
      file_list.append(File(file_name = row[0], client_id = row[2] if len(row) > 2 else row[1], model_id = row[1]))
    elif column_count == 4:
      assert len(row) in (3, 4)
      # we expect: filename, model_id, claimed_id, client_id
      file_list.append(File(file_name = row[0], client_id = row[3] if len(row) > 3 else row[1], model_id = row[1], claimed_id = row[2]))
    else:
      raise ValueError("The given column count %d cannot be interpreted. This is a BUG, please report to the author." % column_count)

  return file_list


def _create_model_dictionary(files):
  # remember model ids
  retval = {}
  for file in files:
    if file._model_id not in retval:
      retval[file._model_id] = file.client_id
    else:
      if retval[file._model_id] != file.client_id:
        raise ValueError("The read model id '%s' is associated to two different client ids '%s' and '%s'!" % (file._model_id, file.client_id, retval[file._model_id]))
  return retval

read_lists = {}
model_dicts = {}

def read_list(list_file, group, type = None, store_lists = True):
  """Reads the list of Files from the given list file (if not done yet) and returns it."""
  if group == 'world':
    if group not in read_lists:
      # read the world list into memory
      list = _read_column_list(list_file, 2)
      if store_lists:
        read_lists[group] = list
      return list
    # just return the previously read list
    return read_lists[group]
  else:
    if group not in read_lists:
      read_lists[group] = {}
    if type not in read_lists[group]:
      if type in ('for_models', 'for_tnorm'):
        list = _read_column_list(list_file, 3)
      elif type == 'for_scores':
        list = _read_column_list(list_file, 4)
      elif type in ('for_probes', 'for_znorm'):
        list = _read_column_list(list_file, 2)
      else:
        raise ValueError("The given type must be one of %s, but not '%s'" %(('for_models', 'for_scores', 'for_probes', 'for_tnorm', 'for_znorm'), type))
      if store_lists:
        read_lists[group][type] = list
      return list
    return read_lists[group][type]

def read_models(list_file, group, type= None, store_lists = True):
  """Generates a dictionary from model_ids to client_ids for the given list file, if not done yet, and returns it"""
  assert group in ('dev', 'eval', 'world')
  assert type in ('for_models', 'for_tnorm')
  if group not in model_dicts:
    model_dicts[group] = {}
  if type not in model_dicts[group]:
    dict = _create_model_dictionary(read_list(list_file, group, type, store_lists))
    if store_lists:
      model_dicts[group][type] = dict
    return dict
  return model_dicts[group][type]
