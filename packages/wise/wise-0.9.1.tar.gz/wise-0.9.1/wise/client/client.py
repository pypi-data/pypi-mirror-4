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

import requests
import json
import mimetypes

def ret(res):
  try:
    return res.json()
  except:
    return res.json

class Client:
  """
  HTTP API client for the wise.io API. 
  
  This is a lower level API closer to the HTTP protocol used by the higher level APIs.
  For general use the higher level bindings available with the wise.project class is recommended.
  """

  def __init__(self, endpoint="https://wise.io/api", user=None, password=None):
    self.endpoint = endpoint
    self.user = user
    self._password = password
    self.headers = {'content-type': 'application/json'}
    # TODO: Direct way to get current user?
    accounts = self.list('account', username=self.user, limit=1)
    self.account = accounts['objects'][0]
    self.last_error = None

  def raise_for_status(self, res):
    try:
      res.raise_for_status()
    except requests.HTTPError:
      self.last_error = res.text
      print "[ERROR] %s" % self.last_error
    res.raise_for_status()

  def request(self, path):
    res = requests.get("%s/%s" % (self.endpoint, path), \
          auth=(self.user,self._password))
    self.raise_for_status(res)
    return ret(res)

  def list(self, resource, page=None, **params):
    if page == None:
      url = "%s/%s/" % (self.endpoint, resource)
    else:
      url = "%s/%s/?page=%d" % (self.endpoint, resource, page)
    res = requests.get(url, auth=(self.user,self._password), params=params)
    self.raise_for_status(res)
    return ret(res)
  
  def get(self, resource, id):
    res = requests.get("%s/%s/%d/" % (self.endpoint, resource, id), \
          auth=(self.user,self._password))
    self.raise_for_status(res)
    return ret(res)

  def create(self, resource, **data):
    data = json.dumps(data)
    res = requests.post("%s/%s/" % (self.endpoint, resource), \
          auth=(self.user,self._password), headers=self.headers, data=data)
    self.raise_for_status(res)
    return ret(res)

  def update(self, resource, id, **data):
    data = json.dumps(data)
    res = requests.put("%s/%s/%d/" % (self.endpoint, resource, id), \
          auth=(self.user,self._password), headers=self.headers, data=data)
    self.raise_for_status(res)
    return ret(res)
      
  def delete(self, resource, id):
    res = requests.delete("%s/%s/%d/" % (self.endpoint, resource, id), \
          auth=(self.user,self._password))
    self.raise_for_status(res)
    return ret(res)

  def query(self, resource, id, method, verb='GET', raw=False, **params):
    res = requests.request(verb, "%s/%s/%d/%s" % (self.endpoint, resource, id, method), \
          data=json.dumps(params), auth=(self.user,self._password), stream=raw)
    self.raise_for_status(res)
    if raw:
      return res.raw
    return ret(res)

  def upload(self, dataset_id, f):
    if type(f) == str:
      mimetype = mimetypes.guess_type(f)[0]
      f = open(f, 'r')
    else: # TODO: Assume text/csv. Better solution?
      mimetype = "text/csv"
    headers = {'content-type': mimetype}
    res = requests.post("%s/dataset/%d/upload" % (self.endpoint, dataset_id), \
          data=f, auth=(self.user,self._password), headers=headers)
    f.close()
    self.raise_for_status(res)
    return ret(res)

  def ingest(self, dataset_id, schema=None):
    data = {'schema': schema} if type(schema) == dict else {}
    res = requests.post("%s/dataset/%d/ingest" % (self.endpoint, dataset_id), \
          data=json.dumps(data), auth=(self.user,self._password), headers=self.headers)
    self.raise_for_status(res)
    return ret(res)

  def select(self, dataset_id, selection):
    res = requests.get("%s/dataset/%d/select" % (self.endpoint, dataset_id), \
            data=json.dumps(selection), auth=(self.user,self._password), headers=self.headers, stream=True)
    self.raise_for_status(res)
    return res.raw
  
  def predict(self, model_id, data, dataset=None):
    """
    :param data: a file-like object with CSV data with the same schema as the training input.
    """
    headers = {}
    params = ""
    if isinstance(data, dict) and isinstance(dataset, int):
      data = json.dumps(data)
      headers = self.headers
      params = "?dataset_id=%d"%dataset
    res = requests.get("%s/model/%d/predict%s" % (self.endpoint, model_id, params), \
            data=data, auth=(self.user,self._password), stream=True, headers=headers)
    self.raise_for_status(res)
    return res.raw
    
