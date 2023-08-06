#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>

"""This module provides the Dataset interface allowing the user to query the
face verification database based on file lists in the most obvious ways.
"""

import os

from .models import Client, File, read_list, read_models

import xbob.db.verification.utils

class Database(xbob.db.verification.utils.ZTDatabase):
  """This class provides a user-friendly interface to databases that are given as file lists.
  The API is comparable to other xbob.db databases."""

  def __init__(
      self,
      base_dir,
      dev_subdir = None,
      eval_subdir = None,

      world_filename = None,
      models_filename = None,

      # For probing, use ONE of the two score file lists:
      probes_filename = None,  # File containing the probe files -> dense model/probe score matrix
      scores_filename = None,  # File containing list of model and probe files -> sparse model/probe score matrix
      # For ZT-Norm:
      tnorm_filename = None,
      znorm_filename = None,
      use_dense_probe_file_list = None,   # if both probe_filename and scores_filename is given, what kind of list should be used?
      keep_read_lists_in_memory = True    # if set to True (the RECOMMENDED default) lists are read only once and stored in memory.
  ):
    """Initializes the database with the file lists from the given base directory,
    and the given sub-directories and file names (which default to useful values if not given)."""

    # call base class constrcutor
    xbob.db.verification.utils.ZTDatabase.__init__(self)

    self.m_base_dir = os.path.abspath(base_dir)
    if not os.path.isdir(self.m_base_dir):
      raise RuntimeError, 'Invalid directory specified %s.' % (self.m_base_dir)

    # sub-directories for dev and eval set:
    self.m_dev_subdir = dev_subdir if dev_subdir is not None else 'dev'
    self.m_eval_subdir = eval_subdir if eval_subdir is not None else 'eval'

    # training list:     format:   filename client_id
    self.m_world_filename = world_filename if world_filename is not None else os.path.join('norm', 'train_world.lst')
    # model list:        format:   filename model_id client_id
    self.m_models_filename = models_filename if models_filename is not None else 'for_models.lst'
    # scores list:       format:   filename model_id claimed_client_id client_id
    self.m_scores_filename = scores_filename if scores_filename is not None else 'for_scores.lst'
    # probe list:        format:   filename client_id
    self.m_probes_filename = probes_filename if probes_filename is not None else 'for_probes.lst'
    # T-Norm models      format:   filename model_id client_id
    self.m_tnorm_filename = tnorm_filename if tnorm_filename is not None else 'for_tnorm.lst'
    # Z-Norm files       format:   filename client_id
    self.m_znorm_filename = znorm_filename if znorm_filename is not None else 'for_znorm.lst'

    # decide, which scoring type we have:
    if   probes_filename is not None and scores_filename is None:
      self.m_use_dense_probes = True
    elif probes_filename is None and scores_filename is not None:
      self.m_use_dense_probes = False
    elif os.path.exists(self.get_list_file('dev', 'for_probes')) and not os.path.exists(self.get_list_file('dev', 'for_scores')):
      self.m_use_dense_probes = True
    elif not os.path.exists(self.get_list_file('dev', 'for_probes')) and os.path.exists(self.get_list_file('dev', 'for_scores')):
      self.m_use_dense_probes = False
    elif use_dense_probe_file_list is not None:
      self.m_use_dense_probes = use_dense_probe_file_list
    else:
      raise ValueError("Unable to determine, which way of probing should be used. Please specify.")

    self.m_store_lists = keep_read_lists_in_memory

  def get_base_directory(self):
    """Returns the base directory where the filelists defining the database
       are located."""
    return self.m_base_dir

  def set_base_directory(self, base_dir):
    """Resets the base directory where the filelists defining the database
      are located."""
    self.m_base_dir = base_dir
    if not os.path.isdir(self.base_dir):
      raise RuntimeError, 'Invalid directory specified %s.' % (self.base_dir)

  def get_list_file(self, group, type = None):
    if group == 'world':
      return os.path.join(self.get_base_directory(), self.m_world_filename)
    else:
      group_dir = self.m_dev_subdir if group == 'dev' else self.m_eval_subdir
      list_name = { 'for_models' : self.m_models_filename,
                    'for_probes' : self.m_probes_filename,
                    'for_scores' : self.m_scores_filename,
                    'for_tnorm' : self.m_tnorm_filename,
                    'for_znorm' : self.m_znorm_filename
                   }[type]
      return os.path.join(self.get_base_directory(), group_dir, list_name)


  def get_client_id_from_model_id(self, model_id, groups=None):
    """Returns the client id that is connected to the given model id.

    Keyword parameters:

    model_id
      The model id for which the client id should be returned.

    groups
      (optional) the groups, the client belongs to.
      Might be one or more of ('dev', 'eval', 'world').
      If groups are given, only these groups are considered.

    Returns: The client id for the given model id, if found.
    """
    groups = self.check_parameters_for_validity(groups, "group", ('dev', 'eval', 'world'))

    for group in groups:
      model_dict = read_models(self.get_list_file(group, 'for_models'), group, 'for_models', self.m_store_lists)
      if model_id in model_dict:
        return model_dict[model_id]

    raise ValueError("The given model id '%s' cannot be found in one of the groups '%s'" %(model_id, groups))


  def get_client_id_from_tmodel_id(self, model_id, groups = None):
    """Returns the client id that is connected to the given T-Norm model id.

    Keyword parameters:

    model_id
      The model id for which the client id should be returned.

    groups
      (optional) the groups, the client belongs to.
      Might be one or more of ('dev', 'eval', 'world').
      If groups are given, only these groups are considered.

    Returns: The client id for the given model id of a T-Norm model, if found.
    """
    groups = self.check_parameters_for_validity(groups, "group", ('dev', 'eval'))

    for group in groups:
      model_dict = read_models(self.get_list_file(group, 'for_tnorm'), group, 'for_tnorm', self.m_store_lists)
      if model_id in model_dict:
        return model_dict[model_id]

    raise ValueError("The given T-norm model id '%s' cannot be found in one of the groups '%s'" %(model_id, groups))


  def clients(self, protocol=None, groups=None):
    """Returns a list of Client objects for the specific query by the user.

    Keyword Parameters:

    protocol
      Ignored.

    groups
      The groups to which the clients belong ("dev", "eval", "world").

    Returns: A list containing all the Client objects which have the given properties.
    """

    client_ids = self.client_ids(protocol, groups)
    return [Client(id) for id in client_ids]

  def tclients(self, protocol=None, groups=None):
    """Returns a list of T-Norm Client objects for the specific query by the user.

    Keyword Parameters:

    protocol
      Ignored.

    groups
      The groups to which the clients belong ("dev", "eval").

    Returns: A list containing all the T-Norm Client objects which have the given properties.
    """
    tclient_ids = self.tclient_ids(protocol, groups)
    return [Client(id) for id in tclient_ids]


  def zclients(self, protocol=None, groups=None):
    """Returns a list of Z-Norm Client objects for the specific query by the user.

    Keyword Parameters:

    protocol
      Ignored.

    groups
      The groups to which the models belong ("dev", "eval").

    Returns: A list containing all the Z-Norm Client objects which have the given properties.
    """
    zclient_ids = self.zclient_ids(protocol, groups)
    return [Client(id) for id in zclient_ids]


  def __client_id_list__(self, groups, type):
    ids = set()
    # read all lists for all groups and extract the model ids
    for group in groups:
      files = read_list(self.get_list_file(group, type), group, type, self.m_store_lists)
      for file in files:
        ids.add(file.client_id)
    return ids


  def client_ids(self, protocol=None, groups=None):
    """Returns a list of client ids for the specific query by the user.

    Keyword Parameters:

    protocol
      Ignored.

    groups
      The groups to which the clients belong ("dev", "eval", "world").

    Returns: A list containing all the client ids which have the given properties.
    """

    groups = self.check_parameters_for_validity(groups, "group", ('dev', 'eval', 'world'))

    return self.__client_id_list__(groups, 'for_models')


  def tclient_ids(self, protocol=None, groups=None):
    """Returns a list of T-Norm client ids for the specific query by the user.

    Keyword Parameters:

    protocol
      Ignored.

    groups
      The groups to which the clients belong ("dev", "eval").

    Returns: A list containing all the T-Norm client ids which have the given properties.
    """

    groups = self.check_parameters_for_validity(groups, "group", ('dev', 'eval'))

    return self.__client_id_list__(groups, 'for_tnorm')


  def zclient_ids(self, protocol=None, groups=None):
    """Returns a list of Z-Norm client ids for the specific query by the user.

    Keyword Parameters:

    protocol
      Ignored.

    groups
      The groups to which the clients belong ("dev", "eval").

    Returns: A list containing all the Z-Norm client ids which have the given properties.
    """

    groups = self.check_parameters_for_validity(groups, "group", ('dev', 'eval'))

    return self.__client_id_list__(groups, 'for_znorm')



  def __model_id_list__(self, groups, type):
    ids = set()
    # read all lists for all groups and extract the model ids
    for group in groups:
      dict = read_models(self.get_list_file(group, type), group, type, self.m_store_lists)
      ids.update(dict.keys())
    return list(ids)


  def model_ids(self, protocol=None, groups=None):
    """Returns a list of model ids for the specific query by the user.

    Keyword Parameters:

    protocol
      Ignored.

    groups
      The groups to which the models belong ("dev", "eval", "world").

    Returns: A list containing all the model ids which have the given properties.
    """

    groups = self.check_parameters_for_validity(groups, "group", ('dev', 'eval', 'world'))

    return self.__model_id_list__(groups, 'for_models')


  def tmodel_ids(self, protocol=None, groups=None):
    """Returns a list of T-Norm model ids for the specific query by the user.

    Keyword Parameters:

    protocol
      Ignored.

    groups
      The groups to which the models belong ("dev", "eval").

    Returns: A list containing all the T-Norm model ids belonging to the given group.
    """

    groups = self.check_parameters_for_validity(groups, "group", ('dev', 'eval'))

    return self.__model_id_list__(groups, 'for_tnorm')



  def objects(self, protocol=None, purposes=None, model_ids=None, groups=None, classes=None):
    """Returns a set of filenames for the specific query by the user.

    Keyword Parameters:

    protocol
      Ignored.

    purposes
      The purposes required to be retrieved ("enrol", "probe") or a tuple
      with several of them. If 'None' is given (this is the default), it is
      considered the same as a tuple with all possible values. This field is
      ignored for the data from the "world" group.

    model_ids
      Only retrieves the files for the provided list of model ids (claimed
      client id). If 'None' is given (this is the default), no filter over
      the model_ids is performed.

    groups
      One of the groups ("dev", "eval", "world") or a tuple with several of them.
      If 'None' is given (this is the default), it is considered the same as a
      tuple with all possible values.

    classes
      The classes (types of accesses) to be retrieved ('client', 'impostor')
      or a tuple with several of them. If 'None' is given (this is the
      default), it is considered the same as a tuple with all possible values.
      Note: classes are not allowed to be specified when the 'probes_filename' is used.

    Returns: A list of File objects considering all the filtering criteria.
    """

    if self.m_use_dense_probes and classes is not None:
      raise ValueError("To be able to use the 'classes' keyword, please use the 'for_scores.lst' list file.")

    purposes = self.check_parameters_for_validity(purposes, "purpose", ('enrol', 'probe'))
    groups = self.check_parameters_for_validity(groups, "group", ('dev', 'eval', 'world'))
    classes = self.check_parameters_for_validity(classes, "class", ('client', 'impostor'))

    if (isinstance(model_ids, str)):
      model_ids = (model_ids,)

    # first, collect all the lists that we want to process
    lists = []
    probe_lists = []
    if 'world' in groups:
      lists.append(read_list(self.get_list_file('world'), 'world', store_lists = self.m_store_lists))

    for group in ('dev', 'eval'):
      if group in groups:
        if 'enrol' in purposes:
          lists.append(read_list(self.get_list_file(group, 'for_models'), group, 'for_models', self.m_store_lists))
        if 'probe' in purposes:
          if self.m_use_dense_probes:
            probe_lists.append(read_list(self.get_list_file(group, 'for_probes'), group, 'for_probes', self.m_store_lists))
          else:
            probe_lists.append(read_list(self.get_list_file(group, 'for_scores'), group, 'for_scores', self.m_store_lists))

    # now, go through the lists and filter the elements

    # remember the file ids that are already in the list
    file_ids = set()
    retval = []

    # non-probe files; just filter by model id
    for list in lists:
      for file in list:
        # check if we already have this file
        if file.id not in file_ids:
          if model_ids is None or file._model_id in model_ids:
            file_ids.add(file.id)
            retval.append(file)

    # probe files; filter by model id and by class
    for list in probe_lists:
      if self.m_use_dense_probes:
        # dense probing is used; do not filter over the model ids and not over the classes
        # -> just add all probe files
        for file in list:
          if file.id not in file_ids:
            file_ids.add(file.id)
            retval.append(file)

      else:
        # sparse probing is used; filter over model ids and over the classes
        for file in list:
          # filter by model id
          if model_ids is None or file._model_id in model_ids:
            # filter by class
            if ('client' in classes and file.client_id == file.claimed_id) or \
             ('impostor' in classes and file.client_id != file.claimed_id):
              # check if we already have this file
              if file.id not in file_ids:
                file_ids.add(file.id)
                retval.append(file)

    return retval


  def tobjects(self, protocol=None, model_ids=None, groups=None):
    """Returns a list of File objects for enrolling T-norm models for score normalization.

    Keyword Parameters:

    protocol
      Ignored.

    model_ids
      Only retrieves the files for the provided list of model ids (claimed
      client id). If 'None' is given (this is the default), no filter over
      the model_ids is performed.

    groups
      The groups to which the models belong ("dev", "eval").

    Returns: A list of File objects considering all the filtering criteria.
    """

    groups = self.check_parameters_for_validity(groups, "group", ('dev', 'eval'))

    if(isinstance(model_ids, str)):
      model_ids = (model_ids,)

    # iterate over the lists and extract the files
    # we assume that there is no duplicate file here...
    retval = []
    for group in groups:
      for file in read_list(self.get_list_file(group, 'for_tnorm'), group, 'for_tnorm', self.m_store_lists):
        if model_ids is None or file._model_id in model_ids:
          retval.append(file)

    return retval


  def zobjects(self, protocol=None, groups=None):
    """Returns a list of File objects to perform Z-norm score normalization.

    Keyword Parameters:

    protocol
      Ignored.

    groups
      The groups to which the clients belong ("dev", "eval").

    Returns: A list of File objects considering all the filtering criteria.
    """

    groups = self.check_parameters_for_validity(groups, "group", ('dev', 'eval'))

    # iterate over the lists and extract the files
    # we assume that there is no duplicate file here...
    retval = []
    for group in groups:
      retval.extend([file for file in read_list(self.get_list_file(group, 'for_znorm'), group, 'for_znorm', self.m_store_lists)])

    return retval
