# Copyright (c) <2013>, <wise.io LLC>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, 
# are permitted provided that the following conditions are met:
#
# - Redistributions of source code must retain the above copyright notice, 
#   this list of conditions and the following disclaimer.
#
# - Redistributions in binary form must reproduce the above copyright notice, 
#   this list of conditions and the following disclaimer in the documentation 
#   and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. 
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, 
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT 
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import json
import md5
import numpy as np
import pandas
import shutil
import tempfile
from StringIO import StringIO
import pickle
import os
import base64
import time
import cPickle

from wise import Client

class adict(dict):
  """Helper class for giving attribute access to dict members."""

  def __getattr__(self, attr):
    return self[attr]
  def __setattr__(self, attr, value):
    self[attr] = value 

def adict_list(data):
  objects = []
  for e in data['objects']:
    objects.append( adict(e) )
  return objects

def _prepare_data(ds):
  if ds != None and 'schema' in ds:
    ds['schema'] = json.loads(ds['schema'])
  return ds

def _prepare_model(m):
  try:
    m['importances'] = json.loads(m['importances'])
    m['selection'] = json.loads(m['selection'])
  except:
    pass
  return m

class project:
  """Main class of the wise package. Provides a unique context for your data and ML projects.
  
  **Example usage**:

  .. code-block:: python

    import wise
    # Connect to project
    w = wise.project("/account/project", user="account", password="...")
    # Add some data
    w.upload("training_data", "wisconsin_train.csv")
    w.upload("testing_data", "wisconsin_test.csv")
    # Prepare a training data selection and build a model
    model = w.learn("model", selection={'exclude': ['ID']}, target="class")
    w.wait(model)
    # Make predictions on new samples
    example = w.select("testing_data", rows=[1])
    w.predict(model, example)

  """

  def __init__(self, path, address="https://wise.io", user = None, password = None):
    """Returns a wise.io project or creates it if possible.

    :param path: the wise.io path to the project.
    :keyword address: the address to the wise.io platform (defaults to localhost).
    :keyword user: wise.io username (default is to get this from ~/.wise/auth ).
    :keyword password: wise.io password (default is to get this from ~/.wise/auth ).

    """
    # Set attrs
    self.address = address
    owner, project = path.split('/')[1:]

    # Authentication
    self.user = user
    self.password = password
    self.c = Client("%s/api"%self.address, user=self.user, password=self.password)

    # Get project info
    projects = self.c.list('project', name=project, owner__username=owner, limit=1)
    if len(projects['objects']) == 0:
      # Create project
      if self.c.account['username'] == owner:
        self.project = adict(self.c.create('project', name=project, owner=self.c.account['id']))
      else:
        raise ValueError("Can only create projects with yourself as the owner.")
    else:
      self.project = adict(projects['objects'][0])

  def users(self):
    """List users in the project.
    """
    members = adict_list( self.c.list('membership', project=self.project.id) )
    return members

  def _id_user(self, obj):
    if isinstance(obj, dict) and 'id' in obj:
      return obj['id']
    elif isinstance(obj, str):
      objs = self.c.list('account', username=obj)['objects']
      return objs[0]['id']
    elif isinstance(obj, int):
      return obj
    else:
      raise ValueError("Can not determine id of object.")

  def add_user(self, user, admin=False):
    """Add a new user to the project.

    :param user: id, name or full user resource.
    :keyword admin: if `True`, the new member can administrate the project.
    """
    user = self._id_user(user)
    member = self.c.create('membership', project=self.project.id, account=user, is_admin=admin)
    return member

  def remove_user(self, user):
    """Remove user from projec.

    :param user: id, name or full user resource.
    """
    user = self._id_user(user)
    membership = self.c.list('membership', project=self.project.id, account=user, limit=1)['objects'][0]
    res = self.c.delete('membership', membership['id'])
    return res

  ### Data methods ###
  
  def upload(self, label, f, ingest=True):
    """Upload data to the project.

    :param label: The label for the data. Will be used to refer to the data later.
    :param f: the file to add. Path to file, open file object or pandas DataFrame
    :keyword ingest: if `True` the data is automatically ingested and prepared for model building (default). 
      Otherwise, if you'd like to change the schema before ingestion, set this to false and call `ingest` subsequently.
    """
    ds = adict(self.c.create('dataset', name=label, project=self.project.id))
    if isinstance(f, str) and os.path.exists(f):
      f = open(f, 'r')
    elif isinstance(f, pandas.DataFrame):
      df = f
      f = tempfile.TemporaryFile()
      df.to_csv(f, na_rep="?", index=False)
      f.seek(0)
    elif not isinstance(f, file):
      return None
    ds = adict(self.c.upload(ds.id, f))
    f.close()
    if ingest:
      ds = adict(self.c.ingest(ds.id))
    ds = _prepare_data(ds)
    return ds

  def _id(self, resource, obj):
    if isinstance(obj, dict) and 'id' in obj:
      return obj['id']
    elif isinstance(obj, str):
      objs = self.c.list(resource, name=obj, project=self.project.id, ordering='-created_at', limit=1)['objects']
      try:
        return objs[0]['id']
      except:
        raise ValueError("Could not find object with name '%s'"%obj)
    elif isinstance(obj, int):
      return obj
    else:
      raise ValueError("Can not determine id of object.")
  
  def ingest(self, dataset, schema):
    """Ingest data and prepare for model building. This is done by default when uploading, 
    so you only have to use this is you've changed the schema of the dataset.

    :param dataset: the dataset label, id or full resource.
    :param schema: the new schema to use for ingestion.
    """
    dataset = self._id('dataset', dataset)
    dataset = adict(self.c.ingest(dataset, schema))
    dataset = _prepare_data(dataset)
    return dataset

  def data(self, dataset=None):
    """Get information on all or specific datasets in the project. 
    
    .. note::
      This will not return any actual data, use :meth:`select` for that.
    
    :param label: if given, return only the specific dataset.
    """
    if dataset == None:
      # Get all datasets
      ds = adict_list(self.c.list('dataset', project=self.project.id))
      ds = map(_prepare_data, ds)
    else:
      id = self._id("dataset", dataset)
      ds = adict(self.c.get("dataset", id))
    ds = _prepare_data(ds)
    return ds

  def remove_data(self, dataset):
    """Remove the dataset.

    :param ds: the dataset label, id or resource to remove.
    """
    dataset = self._id('dataset', dataset)
    res = self.c.delete('dataset', dataset)
    return res  
  
  def select(self, dataset, raw=False, **args):
    """Download a subset of data from the dataset.

    :param dataset: a dataset label, id or resource to select from.
    :keyword rows: a list of rows to select (optional).
    :keyword slice: (optional)
      If a pair of ints, defines the low and high (not included) of a slice of the data. 
    :keyword cols: A list of column names included in the selection. If not given, all are selected (default)
    :keyword exclude: A list of column names to exclude from the selection. Ignored if cols is given.
    :keyword selection: All keywords above can be substituted by a selection dictionary prepared manually or by calling `selection`.
    :keyword raw: will return a file-like object if `True`, otherwise it will return a pandas dataframe (default).

    """
    dataset = self._id('dataset', dataset)
    if 'selection' in args:
      selection = args['selection']
    else:
      selection = self.selection(**args)
    res = self.c.select(dataset, selection)
    if not raw:
      try:
        res = pandas.read_csv(res)
      except:
        res = pandas.read_csv(res.data)
    # TODO: Check this for pandas 0.9.1
    return res

  def selection(self, rows=None, slice=None, cols=None, exclude=None):
    selection = {}
    if rows is not None: selection['rows'] = rows
    if slice is not None: selection['slice'] = slice
    if cols is not None: selection['cols'] = cols
    if exclude is not None: selection['exclude'] = exclude
    return selection

  
  ### Modelling methods ###


  def train(self, label, dataset, target, selection={}, kind='prediction', size=10):
    """Trains a model on the given dataset. 
    
    This method returns immediately. The training process status can be found by calling `status`,
    and `wait` can be used to wait until the model finishes training.
    When status is `done`, use `prediction` to make predictions on the model

    :param label: the model identifier.
    :param dataset: the dataset label, id or resource that this model should be trained on.
    :param target: the target variable.
    :keyword selection: a data selection, used to train on a subset of the dataset. See `select`.
    :keyword kind: the type of model. Currently supported is "prediction".
    :keyword size: the number of submodels to build for the model (default 10).
    :returns: model resource.

    """
    dataset = self._id('dataset', dataset)
    model = adict( self.c.create('model', project=self.project.id, name=label, dataset=dataset,\
            target=target, selection=json.dumps(selection), kind=kind, size=size) )
    status = self.c.query('model', model.id, 'train', verb='POST', raw=True).text
    model.status = status
    return _prepare_model(model)

  def status(self, model):
    """Get the status of the model training process. Possible values are:

    * initialized -- model created but training not started.
    * spawning -- model building process is being spawned.
    * loading -- data for the model building is loading.
    * training -- model is currently being trained.
    * done -- model has been succesfully trained.
    * error -- an error occured while training.

    :param model: the model label, id or resource.
    """
    model = self._id('model', model)
    return self.c.query('model', model, 'status', raw=True).text

  def wait(self, model):
    """Wait for a  model to finish building.

    :param model: the model id, label or resource returned by the `train` or `model` methods.
    :returns: the updated model with additional information from the training. If `model` is a resource, it will be updated with this information.

    """
    while self.status(model) not in ['done', 'error']:
      time.sleep(1)
    new_model = self.model(model)
    if isinstance(model, dict):
      model.update(new_model)
    return new_model

  def models(self):
    """Get a list of models in the project."""
    models = adict_list( self.c.list('model', project=self.project.id) )
    return map(_prepare_model, models)

  def model(self, model):
    """Get a single model in the project.

    :param model: the model id, label or resource.

    """
    id = self._id('model', model)
    model = adict( self.c.get('model', id) )
    return _prepare_model(model)

  def remove_model(self, model):
    """Remove the model.

    :param model: the model label, id or resource to remove.
    """
    model = self._id('model', model)
    res = self.c.delete('model', model)
    return res  
  
  def predict(self, model, f, dataset=None, raw=False):
    """Make predictions on new data from the given model.
    
    ..note:
      The data passed to this method must have the same structure as the data that was used for training the model.

    :param model: the model label, id or resource. 
    :param f: the data to use for prediction. This should be a path to a CSV file, a file handle, or a pandas DataFrame. 
              Can also be a selection dictionary prepared manually or by calling `selection`, in which case the `dataset` keyword is required.

    :keyword dataset: The dataset label, id or resource. Required if `f` is a selection dictionary.
    :keyword raw: if `True`, return the raw response body instead of a pandas DataFrame (default False).

    """
    model = self._id('model', model)
    if isinstance(f, str) and os.path.exists(f):
      f = open(f, 'r')
    elif isinstance(f, pandas.DataFrame):
      df = f
      f = tempfile.TemporaryFile()
      df.to_csv(f, na_rep="?", index=False)
      f.seek(0)
    elif isinstance(f, dict) and dataset is not None:
      # f is a data selection
      dataset = self._id('dataset', dataset)
    elif not isinstance(f, file):
      return None
    res = self.c.predict(model, f, dataset=dataset)
    if not raw:
      try:
        res = pandas.read_csv(res)
      except:
        res = pandas.read_csv(res.data)
    return res
  
  def download_model(self, model):
    """Download the model. Requires WiseRF installed. See http://about.wise.io/wiserf.html

    :param model: the model label, id or resource to remove.
    """
    from PyWiseRF import WiseRF
    model = self._id('model', model)
    res = self.c.query('model', model, 'download', raw=True)
    rf = cPickle.loads(res.data)
    return rf 
