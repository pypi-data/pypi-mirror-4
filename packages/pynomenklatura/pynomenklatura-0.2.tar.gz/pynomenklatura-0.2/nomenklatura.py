import requests
import json


class NKObject(object):
  """ The basic Object we'll be inheriting from """

  def __init__(self,data):
    self.__data__=data
  
  def __getattr__(self,k):
    return self.__data__[k]

  def __str__(self):
    return self.__repr__()

  class NKException(Exception):

    def __init__(self,data):
      self.__data__=data
  
    def __getattr__(self,k):
      return self.__data__[k]

    def __repr__(self):
      return "<NKException>"

    def __str__(self):
      return self.__repr__()


  class DatasetException(NKException):

    def __repr__(self):
        return "<DatasetException(%s:%s)>" % (self,
                                               getattr(self, 'message', None))


  class NoMatch(NKException):

    def __repr__(self):
      return "<NoMatch(%s:%s)>" % (self.dataset,
                                       self.key)


  class Invalid(NKException):

    def __repr__(self):
      return "<Invalid(%s:%s)>" % (self.dataset,
                                     self.key)


class Value(NKObject):

  def __init__(self, dataset, data):
    self._dataset = dataset
    super(Value,self).__init__(data)

  def __repr__(self):
    return "<Value(%s:%s:%s)>" % (self._dataset.name,
                                      self.id, self.value)

  def __str__(self):
    return self.value

class Link(NKObject):

  INVALID = "INVALID"
  NEW = "NEW"

  def __init__(self, dataset, data):
      self._dataset = dataset
      super(Link,self).__init__(data)

  def __repr__(self):
      return "<Link(%s:%s:%s:%s)>" % (self._dataset.name,
                                     self.id, self.key, self.is_matched)


class Dataset(NKObject):
  """ A Nomenklatura dataset. Helps you to access values and links from
  Nomenklatura...
  
  Dataset(name,host="http://nomenklatura.okfnlabs.org",api_key=None)

  usage:
    
    from nomenklatura import dataset
    ds=Dataset("offenesparlament")
    ds.lookup("Angela Merkel")

  Methods defined here:

  get_value(id=None,value=None) """



  def __init__(self, dataset,
               host='http://nomenklatura.okfnlabs.org',
               api_key=None):
      self.host = host
      self.name = dataset
      self.api_key = api_key
      self._fetch()

  @property
  def _session(self):
      if not hasattr(self, '_session_obj'):
          headers = {'Accept': 'application/json',
                     'Content-Type': 'application/json'}
          if self.api_key:
              headers['Authorization'] = self.api_key
          self._session_obj = requests.Session()
          self._session_obj.headers.update(headers)
      return self._session_obj

  def _get(self, path, params={}, retry=True):
      response = self._session.get(self.host + '/' + self.name + path,
                                   params=params)
      if not response.ok:
          #print [response.status_code, response.content]
          del self._session_obj
      return response.status_code, response.json()

  def _post(self, path, data={}, retry=True):
      data = json.dumps(data)
      response = self._session.post(self.host + '/' + self.name + path,
                                    allow_redirects=True,
                                    data=data)
      if not response.ok:
          #print [response.status_code, response.content]
          del self._session_obj
      return (response.status_code,
              json.loads(response.content) if response.content else {})

  def _fetch(self):
      code, data = self._get('')
      if not (code == 200 and data):
          data = data or {'code': code}
          raise self.DatasetException(data)
      super(Dataset,self).__init__(data)    

  def get_value(self, id=None, value=None):
    """ get a value from the dataset 
        get_value(id=23) -> get value with id 23
        get_value(value="FOO") -> get value with value "FOO"

        if neither id nor value are specified - raises a Value
        Error
    """

    if not (id or value):
      raise ValueError("Need to give an ID or a value")
    if id is not None:
        code, val = self._get('/values/%s' % id)
    else:
        code, val = self._get('/value', params={'value': value})
    if code != 200:
        raise self.NKException(val or {})
    return Value(self, val)

  def add_value(self, value, data={}):
    """ Add a value to the dataset """
    code, val = self._post('/values',
                           data={'value': value, 'data': data})
    if code == 400:
        raise self.NKException(val)
    return Value(self, val)

  def ensure_value(self, value, data={}):
    """ Makes sure you have a value to work with:
      ensure_value(value,data) ->
        Returns a Value if it exists - adds the value otherwise
        """
    try:
        return self.get_value(value=value)
    except self.NKException:
        return self.add_value(value=value, data=data)

  def values(self):
    """ Returns a generator of all Values in the dataset """
    code, vals = self._get('/values')
    return (Value(self, v) for v in vals) 

  def get_link(self, id=None, key=None):
      if not (id or key):
        raise ValueError("Need to give an ID or a Key")
      if id:
          code, val = self._get('/links/%s' % id)
      else:
          code, val = self._get('/link', params={'key': key})
      if code != 200:
          raise self.NKException(val)
      return Link(self, val)

  def links(self):
    """ Returns a generator of all links in the dataset """
    code, vals = self._get('/links')
    return (Link(self, v) for v in vals)

  def lookup(self, key, context={}, readonly=False):
      code, val = self._post('/lookup',
                             data={'key': key,
                                   'readonly': readonly})
      if code == 404:
          raise self.NoMatch(val)
      elif code == 418:
          raise self.Invalid(val)
      else:
          return Value(self, val.get('value'))

  def match(self, link_id, value_id):
      code, val = self._post('/links/%s/match' % link_id,
                             data={'choice': value_id,
                                   'value': ''})
      if code != 200:
          raise self.NKException(val)
      return None

  def __repr__(self):
    return "<Dataset(%s)>" % self.name

if __name__ == "__main__":
  ds = Dataset('offenesparlament')
