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
#  This is the main server that listens for requests, imports service classes
#  and calls the service methods. It receives a service name in dot-separated path
#  format and expect to find the class containing the service in a file.
#  If the service name is "foo.bar.baz", the class is named "Baz" in the
#  "foo.bar.baz" module, located in "foo/bar/baz.py" somewhere on the python
#  class path. The class file is dynamically loaded when the request is received.
#  The classes and methods are protected.
#
#############################################################################


import sys
import cherrypy
import urllib

from error import ServiceNotFoundError, ServerError
from request import Request


class JsonRpcServer:
  '''HTTP JSON-RPC server backend for qooxdoo and other json-rpc clients'''

  _serviceClasses = {}
  '''Cache of service classes'''
  _requestClass = None
  '''Class of request object, provides override for custom serialization''' 


  def __init__(self, requestClass = Request):
    self._requestClass = requestClass

  def _get(self, request):
    try:
      # Determine request domain
      request.domain = cherrypy.request.headers.get('host', None)

      # Expand ScriptTransport arguments if any
      scriptTransportId   = cherrypy.request.params['_ScriptTransport_id']
      scriptTransportData = cherrypy.request.params['_ScriptTransport_data']

      # Determine transport type
      if scriptTransportId and scriptTransportData:
        # ScriptTransport, JSON encoded request object is in _ScriptTransport_data
        request.loadJson(scriptTransportData)
        response = request.process()
        # Encode qooxdoo specific ScriptTransport response
        if cherrypy.response.headers.get('content-type') == "application/json":
          response = 'qx.io.remote.transport.Script._requestFinished(%s,%s);' % (scriptTransportId, response)
      else:
        # Request is defined as queryvariables, params and server_data are JSON encoded
        request.load(('id', 'params', 'server_data'), **cherrypy.request.params)
        response = request.process()

      return response
    except ServerError, e:
      raise cherrypy.HTTPError(400, '[%s]: %s' % (e.__class__.__name__, e)), None, sys.exc_info()[2]
    except Exception, e:
      raise cherrypy.HTTPError(500, 'Internal server error: %s' % e), None, sys.exc_info()[2]

  def _post(self, request):
    try:
      # Determine request domain
      request.domain = cherrypy.request.headers.get('host', None)

      # Read POST data
      contentLength = int(cherrypy.request.headers.get('content-length', '0'))
      if contentLength < 1:
        message = 'No Content-Length header or zero length specified!'
        raise cherrypy.HTTPError(400, message)
      formData = cherrypy.request.body.read()

      # Form data contains direct JSON data?
      if formData[:1] == '{' and formData[-1:] == '}':
        formParams = dict(_data_ = formData)
      else:
        formParams = cherrypy.request.params

      # Determine transport type
      if '_data_' in formParams:
        request.loadJson(formParams['_data_'])
      elif '_ScriptTransport_data' in formParams:
        request.loadJson(urllib.unquote(formParams['_ScriptTransport_data']))
      elif 'id' in formParams and 'service' in formParams and 'method' in formParams:
        # Request is defined as form variables, params and server_data are JSON encoded
        fields = ('id', 'service', 'method', 'params', 'server_data')
        params = dict([(k, formParams[k]) for k in fields if k in formParams])
        request.load(('id', 'params', 'server_data'), **params)
      else:
        raise cherrypy.HTTPError(400, 'Invalid form contents in POST request: %r' % formParams)

      # Handle request
      return request.process()
    except ServerError, e:
      raise cherrypy.HTTPError(400, '[%s]: %s' % (e.__class__.__name__, e)), None, sys.exc_info()[2]
    except Exception, e:
      raise cherrypy.HTTPError(500, 'Internal server error: %s' % e), None, sys.exc_info()[2]

  def run(self):
    request = self._requestClass(self)
    if cherrypy.request.method == "GET":
      return self._get(request)
    elif cherrypy.request.method == "POST":
      return self._post(request)
    else:
      raise cherrypy.HTTPError(400, "Services require JSON-RPC")

  def getService(self, name):
    if name not in self._serviceClasses:
      try:
        self._serviceClasses[name] = self._loadClass(name)
      except Exception:
        raise ServiceNotFoundError('Service %r not found!' % name), None, sys.exc_info()[2]

    return self._serviceClasses[name]()

  def _loadClass(self, fullClassName):
    """Retrieve a class object from a full dotted-package name."""

    # Parse out the path, module, and function
    lastDot = fullClassName.rfind(u".")
    if lastDot is not -1:
      className = fullClassName[lastDot + 1:]
      modPath   = fullClassName[:lastDot]
    else:
      className = fullClassName
      modPath   = fullClassName

    aMod   = self._loadModule(modPath)
    aClass = getattr(aMod, className)

    # Assert that the function is a *callable* attribute.
    assert callable(aClass), "%s is not callable." % fullClassName

    # check access: service class is instance of jsonrpc.server.JsonRpcService
    if not issubclass(aClass, JsonRpcService):
      raise ServiceNotFoundError('%r is not a RPC service!' % modPath)

    # Return a reference to the function itself,
    # not the results of the function.
    return aClass

  def _loadModule(self, modulePath):
    """Import a module programmatically"""
    try:
      aMod = sys.modules[modulePath]
    except KeyError:
      # The last [''] is very important!
      try:
        aMod = __import__(modulePath, globals(), locals(), [''])
        sys.modules[modulePath] = aMod
      except ImportError:
        raise ServiceNotFoundError('Service %r not found!' % modulePath), None, sys.exc_info()[2]

    return aMod


class JsonRpcService(object):
  '''Superclass for a service'''

  def onException(self, exception):
    pass

  def preDispatch(self, request):
    pass

  def postDispatch(self, request):
    pass
