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
#  Error codes and exception classes. Currently all symbols are exported.
#  This module is NOT intended for direct import. Import symbols from jsonrpc.
#
#############################################################################


# Error codes

class ErrorOrigin:
  '''JSON-RPC error origins'''

  Server      = 1
  Application = 2
  Transport   = 3
  Client      = 4


class ErrorCode:
  '''JSON-RPC server-generated error codes'''

  Unknown           = 0
  IllegalService    = 1
  ServiceNotFound   = 2
  ClassNotFound     = 3
  MethodNotFound    = 4
  ParameterMismatch = 5
  PermissionDenied  = 6


# Exceptions

class Error(Exception):
  '''Base class for all JSON-RPC specific exceptions.'''

  origin = None
  code   = ErrorCode.Unknown


  def getJsonRpcError(self):
    '''Returns JSON-RPC error object to encode into response'''

    return dict(
      origin  = self.origin,
      code    = self.code,
      message = '[%s] %s' % (self.__class__.__name__, str(self))
    )


class ServerError(Error):
  '''A subclass of this class is raised when the error is orginated form
  the JSON-RPC server itself. Only the JSON-RPC server can raise this.'''

  origin = ErrorOrigin.Server


class ApplicationError(Error):
  '''A subclass of this class is raised when the error is orginated form
  the application (a service served by the JSON-RPC server). Only the
  server-side applications can raise this.'''

  origin = ErrorOrigin.Application


class TransportError(Error):
  '''A subclass of this class is raised when the error is orginated form
  the transport used (communication errors). Only JSON-RPC clients
  can raise this.'''

  origin = ErrorOrigin.Transport


class ClientError(Error):
  '''A subclass of this class is raised when an error is caused at the
  client side. Only JSON-RPC clients can raise this.'''

  origin = ErrorOrigin.Client


class UnknownError(ServerError):
  '''This exception is raised by the JSON-RPC server if an unknown error
  raised in the server. The reasion should be described by the error
  message (exception text).'''

  code = ErrorCode.IllegalService


class IllegalServiceError(ServerError):
  '''This exception is raised by the JSON-RPC server if the service name
  contains illegal characters or is otherwise deemed unacceptable.'''

  code = ErrorCode.IllegalService


class ServiceNotFoundError(ServerError):
  '''This exception is raised by the JSON-RPC server if the requested
  service does not exist.'''

  code = ErrorCode.ServiceNotFound


class ClassNotFoundError(ServerError):
  '''This exception is raised by the JSON-RPC server if a method name
  with dots is specified and the object containing a subobject or the
  final method is not found in the service.'''

  code = ErrorCode.ClassNotFound


class MethodNotFoundError(ServerError):
  '''This exception is raised by the JSON-RPC server if the method
  specified in the request is not found in the requested service.'''

  code = ErrorCode.MethodNotFound

class ParameterMismatchError(ServerError):
  '''This exception is raised by the JSON-RPC server if a method
  discovers that the parameters (arguments) provided to it do not match
  the requisite types for the method's parameters. TypeError exceptions
  originating from the method call are automatically translated to this
  exception.'''

  code = ErrorCode.ParameterMismatch

class PermissionDeniedError(ServerError):
  '''This exception is raised by the JSON-RPC server if the service
  requires authentication, and that authentication is failed.'''

  code = ErrorCode.PermissionDenied
