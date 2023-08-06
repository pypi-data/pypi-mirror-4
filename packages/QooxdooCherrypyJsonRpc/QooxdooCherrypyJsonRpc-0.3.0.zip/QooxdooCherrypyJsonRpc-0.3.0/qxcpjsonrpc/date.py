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
#    * saaj (mail@saaj.me)
#
#############################################################################
#
#  Date ISO 8601 parsing and dumping.
#  This module is NOT intended for direct import. Import symbols from jsonrpc.
#
#############################################################################


import datetime


class Utc(datetime.tzinfo):
  '''UTC timezone'''
  
  _zero = datetime.timedelta(0)
  
   
  def utcoffset(self, dt):
    return self._zero
  
  def dst(self, dt):
    return self._zero

_utc = Utc()


def toJsonDate(obj):
  if not obj:
    return None
  
  if not isinstance(obj, datetime.datetime):
    obj = datetime.datetime(*obj.timetuple()[:-3])
  # is datetime naive or aware
  if obj.tzinfo is not None and obj.tzinfo.utcoffset(obj) is not None:
    return obj.astimezone(_utc).isoformat("T").replace("+00:00", "Z")
  else:
    return obj.isoformat("T") + "Z"

def fromJsonDate(s):
  if not s:
    return None
  
  try:
    result = datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ")
  except ValueError:
    # IE8 JSON implementation produces date without miliseconds
    result = datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")

  return result.replace(tzinfo = _utc)
