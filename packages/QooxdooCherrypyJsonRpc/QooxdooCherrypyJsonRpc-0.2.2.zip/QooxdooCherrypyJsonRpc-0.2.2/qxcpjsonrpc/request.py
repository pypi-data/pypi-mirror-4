#############################################################################
#
#  jsonrpc
#
#  Based on:
#    http://qooxdoo.org/contrib/project#rpcpython
#
#  License:
#    LGPL: http://www.gnu.org/licenses/lgpl.html
#    EPL: http://www.eclipse.org/org/documents/epl-v10.php
#
#  Authors:
#    * Viktor Ferenczi (python@cx.hu)
#    * Christian Boulanger (cboulanger)
#    * saaj (mail@saaj.me)
#
#############################################################################
#
#  This module provides the JSON-RPC Request class. The Request class is able
#  to load JSON-RPC requests from various formats. It processes the request,
#  then returns valid JSON-RPC response string. All exceptions are handled
#  and returned as valid JSON-RPC error responses, except for
#  KeyboardInterrupt. Exception tracebacks are dumped to the log.
#  This module is NOT intended for direct import. Import symbols from jsonrpc.
#
#############################################################################


import sys
import traceback
import json
import cherrypy
import logging
import datetime
import decimal

from date import toJsonDate
from access import getMethodAccessCheckers 
from error import ServerError, Error, MethodNotFoundError, ClassNotFoundError,\
  ServiceNotFoundError, PermissionDeniedError, ApplicationError


# Exported symbols
__all__ = ['Request']


class Request(object):
  '''JSON-RPC request. Request object stores all important information
  about the request. References in the Request object connect the objects
  (server, client, etc) required to handle the request.

  Request objects can be reused to achieve better performance. The server
  can use one Request object for all requests from the same client on the
  same logical connection. It's not allowed to share Request objects
  between multiple threads, since they are not thread safe, no locking
  mechanism is implemented.

  The server's request handler must load request data by calling the
  load() or loadJson() method of the Request instance. Then the request
  can be processed by calling the process() method. Finally the request
  object should be cleared by calling clear() on it. This is not required,
  but helps to prevent hard-to-debug errors and lower memory footprint.

  Request should not be subclassed, since this does only common JSON-RPC
  request handling not depending on specific transport or other parties.

  Request objects has human readable representation for easy logging and
  debugging. This is returned also as string form.

  Request attributes (defined as slots for better performance):

  - Set by the constructor, should not be changed later:

  domain = domain address/identifier or None if the current transport does not support domains

  - Loaded for each request, then cleared:

  id      = current request's ID or None if no request has been loaded
  server  = reference to the JsonRpcServer object
  service = service name
  method  = method name or path with dots
  params  = list or dictionary of parameters to be passed to the method or []
  data    = server_data or None'''

  __slots__ = ['server', 'domain', 'id', 'service', 'method', 'params', 'data']
  

  def __init__(self, server, domain = None):
    '''Initialize common request attributes.'''

    self.server = server # JsonRpcServer instance handling the request
    self.domain = domain # Request's domain name if applicable to the current transport or None
    self.clear()         # No request specific data

  def __str__(self):
    return repr(self)

  def __repr__(self):
    attributes = [(k, getattr(self,k)) for k in self.__slots__]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(['%s=%r' % (k, v) for k, v in attributes]))

  def clear(self):
    '''Clear request data. Should be called after each request handling.'''

    self.id      = None
    self.service = None
    self.method  = None
    self.params  = None
    self.data    = None

  def load(self, _decode_keys_ = (), **kw):
    '''Load request from keyword arguments, optionally JSON decode some of them'''

    # Check for required request arguments
    for n in ('id', 'service', 'method'):
      if n not in kw:
        raise ServerError('Request does not contain %s!' % n)

    # JSON decode some arguments as requested
    for n in _decode_keys_:
      if n not in kw:
        continue

      try:
        kw[n] = json.loads(kw[n])
      except ValueError, e:
        raise ServerError('Error decoding JSON request argument %r: %s' % (n, e)), None, sys.exc_info()[2]

    # Extract request arguments with defaults
    self.service = kw['service']
    self.method  = kw['method']
    self.params  = kw.get('params', [])
    self.data    = kw.get('server_data')

    # Check type of request arguments (not method parameters)
    if not isinstance(self.service, basestring):
      raise ServerError('Service name is not a string: %r' % self.service)
    if not isinstance(self.method, basestring):
      raise ServerError('Method name is not a string: %r' % self.method)
    if not isinstance(self.params, (list, dict)):
      raise ServerError('Parameters passed are not in the form of list or dictionary: %r' % self.params)

    # Store request ID
    self.id = kw['id']
    if self.id is None:
      raise ServerError('Request ID cannot be None!')

  def loadJson(self, jsonRequest):
    '''Load request from JSON request string'''

    # Decode JSON request as Python object
    try:
      request = json.loads(jsonRequest)
    except ValueError, e:
      raise ServerError('Error decoding JSON request: %s' % e), None, sys.exc_info()[2]

    # Ensure that all keys are string (Python does not allow
    # unicode keys when passing as keyword arguments)
    req = {}
    for k, v in request.items():
      if isinstance(k, unicode):
        k = k.decode('ascii')
      req[k] = v

    # Load request
    self.load(**req)

  def log(self, message, error):
    cherrypy.log(message, severity = logging.DEBUG if not error else logging.ERROR)
    
  def _serialize(self, obj):
    '''Serialization for objects that not handled by json package''' 
    
    if isinstance(obj, datetime.date):
      return toJsonDate(obj)

    if isinstance(obj, decimal.Decimal):
      return str(obj)

    return None

  def process(self):
    '''Process request, returns JSON-RPC response object (not JSON string).
    Always produces valid JSON-RPC response object, except when a
    System Exit or KeyboardInterrupt raised, since they are propagated.'''

    assert self.id is not None, 'Load request into this instance before processing!'

    self.log('REQUEST: %r' % self, False)

    service = None
    try:
      service = self.server.getService(self.service)

      service.preDispatch(self)
      try:
        method = self.getMethod(service)
        result = self.callMethod(service, method)
      finally:
        service.postDispatch(self)
    except (SystemExit, KeyboardInterrupt):
      raise # For python 2.4 compatibility
    except Error, e:
      message = 'REQUEST: %r\nAPPLICATION ERROR [%s]: %s\nTRACEBACK:\n%s'
      self.log(message % (self, e.__class__.__name__, e, traceback.format_exc()), True)
      # if service found and original exception has not already been passed to the service
      if not isinstance(e, (ServiceNotFoundError, ApplicationError)):
        service.onException(e)

      response = dict(id = self.id, result = None, error = e.getJsonRpcError())
    except Exception, e:
      message = 'REQUEST: %r\nINTERNAL SERVER ERROR [%s]: %s\nTRACEBACK:\n%s'
      self.log(message % (self, e.__class__.__name__, e, traceback.format_exc()), True)
      # if original exception has not already been passed to the service
      if not isinstance(e, ApplicationError) and service:
        service.onException(e)

      e = ServerError('Internal server error.')
      response = dict(id = self.id, result = None, error = e.getJsonRpcError())
    else:
      response = dict(id = self.id, result = result, error = None)

    self.log('RESPONSE: %r' % response, False)

    try:
      if hasattr(response["result"], "readall"):
        response = response["result"].readall()
      elif hasattr(response["result"], "getvalue"):
        response = response["result"].getvalue()
      else:
        # iframe response case
        if cherrypy.response.headers['content-type'] != 'text/plain':
          cherrypy.response.headers['content-type'] = 'application/json'

        response = json.dumps(response, default = self._serialize)
    except ValueError, e:
      e = ServerError('Error JSON encoding response: %s' % e)
      response = dict(id = self.id, result = None, error = e.getJsonRpcError())
      response = json.dumps(response)

    return response

  def getMethod(self, service):
    '''Get method (function object) by method name.'''

    name = self.method
    if '.' in name:
      name = name.split('.')
      for clsname in name[:-1]:
        try:
          service = getattr(service, clsname)
        except AttributeError:
          message = 'Class %r not found when searching for method %r in service %r!'
          raise ClassNotFoundError(message % (clsname, self.method, self.service))
      name = name[-1]

    try:
      return getattr(service, name)
    except AttributeError:
      raise MethodNotFoundError('Method %r not found in service %r!' % (self.method, self.service))

  def callMethod(self, service, method):
    '''Call requested method, returns result.'''

    # Check if access is allowed
    accessCheckers = getMethodAccessCheckers(method)
    for accessChecker in accessCheckers:
      if not accessChecker(method, self):
        raise PermissionDeniedError('Access denied on %r.' % self.method)

    # Check if method is callable
    if not callable(method):
      raise MethodNotFoundError('Method %r in service %r is not callable!' % (self.method, self.service))

    # Build positional and keyword arguments passed to the method
    if isinstance(self.params, list):
      params = self.params
      kw = {}
    else:
      params = []
      # NOTE: Does not copy parameters to save time. This is not a bug,
      # since params are used only once for each request.
      kw = self.params

    # Call method with error handling
    try:
      return method(*params, **kw)
    except (SystemExit, KeyboardInterrupt):
      raise # For python 2.4 compatibility
    except Exception, e:
      if service:
        service.onException(e)
      raise ApplicationError(str(e)), None, sys.exc_info()[2]
