'''
@author: saaj
'''


import json
import hashlib
import os.path
import urllib

import test
from request import Request


class TestGeneral(test.TestCase):
  
  def testIndex(self):
    self.getPage('/')
    
    self.assertHeader('content-type', 'text/html;charset=utf-8')
    self.assertBody('Testing qxcpjsonrpc')
  
  def testServiceEmpty(self):
    self.getPage('/service')
    self.assertHeader('content-type', 'text/html;charset=utf-8')
    self.assertStatus(500)
  
  def testServiceServiceNotFound(self):
    request = json.dumps({
      'id'      : 1,
      'service' : 'something.User',
      'method'  : 'do',
      'params'  : []
    })
    headers = [('content-length', len(request))]
    
    self.getPage('/service', method = 'post', body = request, headers = headers)
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    response = json.loads(self.body)
    self.assertTrue(response['result'] is None)
    message = "[ServiceNotFoundError] Service u'something.User' not found!" 
    self.assertEqual(message, response['error']['message'])
    
  def testServiceMethodNotFound(self):
    self._post('do')
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    response = json.loads(self.body)
    self.assertTrue(response['result'] is None)
    message = u"[MethodNotFoundError] Method u'do' not found in service u'test.Service'!" 
    self.assertEqual(message, response['error']['message'])
  
  def testServicePost(self):
    self._post('add', 12, 13)
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    response = json.loads(self.body)
    self.assertTrue(response['error'] is None)
    self.assertEqual(12 + 13, response['result'])
    
  def testServiceGet(self):
    request = {
      '_ScriptTransport_data' : json.dumps({
        'id'      : 1,
        'service' : 'test.Service',
        'method'  : 'add',
        'params'  : [12, 13]
      }),
      '_ScriptTransport_id'   : 1 
    }
    
    self.getPage('/service?' + urllib.urlencode(request), method = 'get')
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    scriptTransport = 'qx.io.remote.transport.Script._requestFinished(1,{0});'
    self.assertBody(scriptTransport.format('{"error": null, "id": 1, "result": 25}'))
    
  def testDispatchOrder(self):
    self._post('add', 12, 13)


    self.assertEqual(3, len(test.Service.state))
    
    self.assertIs(test.Service.state[0][1], test.Service.state[2][1], 'same Request object')
    
    item = test.Service.state.pop(0)
    self.assertEqual('preDispatch', item[0])
    self.assertIsInstance(item[1], Request)
    
    item = test.Service.state.pop(0)
    self.assertEqual('add', item[0])
    self.assertIsNone(item[1])

    item = test.Service.state.pop(0)
    self.assertEqual('postDispatch', item[0])
    self.assertIsInstance(item[1], Request)
    
  def testException(self):
    self._post('error')
    
    self.assertEqual(3, len(test.Service.state))
    
    self.assertIs(test.Service.state[0][1], test.Service.state[2][1], 'same Request object')
    
    item = test.Service.state.pop(0)
    self.assertEqual('preDispatch', item[0])
    self.assertIsInstance(item[1], Request)
    
    item = test.Service.state.pop(0)
    self.assertEqual('onException', item[0])
    self.assertIsInstance(item[1], ValueError)

    item = test.Service.state.pop(0)
    self.assertEqual('postDispatch', item[0])
    self.assertIsInstance(item[1], Request)
    

class TestAccess(test.TestCase):
  
  def testServiceEmpty(self):
    self.getPage('/withauth')
    self.assertStatus(401)
    self.assertHeader('WWW-Authenticate', 'Basic realm="musicians"')
    
    self.getPage('/withauth', headers = [('Authorization', 'Basic am9uZXM6YmxhaC1ibGFo')])
    self.assertStatus(401)
    
    token = 'Basic {0}'.format('jones:XpasS3'.encode('base64').strip())
    self.getPage('/withauth', headers = [('Authorization', token)])
    self.assertStatus(500)
    
  def testServiceMethodInternal(self):
    self._post('internal')
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    response = json.loads(self.body)
    self.assertTrue(response['result'] is None)
    message = u"[PermissionDeniedError] Access denied on u'internal'." 
    self.assertEqual(message, response['error']['message'])
    
  def testServiceMethodFail(self):
    self._post('forbidden')
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    response = json.loads(self.body)
    self.assertTrue(response['result'] is None)
    message = u"[PermissionDeniedError] Access denied on u'forbidden'." 
    self.assertEqual(message, response['error']['message'])
    
  def testAccessAllowed(self):
    request = json.dumps({
      'id'      : 1,
      'service' : 'test.Service',
      'method'  : 'subtract',
      'params'  : [13, 12]
    })
    headers = [
      ('content-length', len(request)),
      ('Authorization', 'Basic {0}'.format('burns:XpaSs2'.encode('base64').strip()))
    ]
    
    self.getPage('/withauth', method = 'post', body = request, headers = headers)
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    response = json.loads(self.body)
    self.assertTrue(response['error'] is None)
    self.assertEqual(13 - 12, response['result'])
  
  def testAccessForbidden(self):
    request = json.dumps({
      'id'      : 1,
      'service' : 'test.Service',
      'method'  : 'subtract',
      'params'  : [13, 12]
    })
    headers = [
      ('content-length', len(request)),
      ('Authorization', 'Basic {0}'.format('jones:XpasS3'.encode('base64').strip()))
    ]
    
    self.getPage('/withauth', method = 'post', body = request, headers = headers)

    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    response = json.loads(self.body)
    self.assertTrue(response['result'] is None)
    message = u"[PermissionDeniedError] Access denied on u'subtract'." 
    self.assertEqual(message, response['error']['message'])
    

class TestJsonExtra(test.TestCase):
  
  def testDecimal(self):
    self._post('decimal')
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    response = json.loads(self.body)
    self.assertTrue(response['error'] is None)
    self.assertEqual(u'12.13', response['result'])
  
  def testDate(self):
    self._post('today')
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    response = json.loads(self.body)
    self.assertTrue(response['error'] is None)
    
    self.assertEqual([
      u'2012-03-17T19:09:12.217000Z',
      u'2012-03-17T00:00:00Z',
      u'2012-03-17T17:09:12.217000Z'
    ], response['result'])
    
    dates = map(lambda d: str(test.rpc.fromJsonDate(d)), response['result'])
    self.assertEqual('2012-03-17 19:09:12.217000+00:00', dates[0])
    self.assertEqual('2012-03-17 00:00:00+00:00',        dates[1])
    self.assertEqual('2012-03-17 17:09:12.217000+00:00', dates[2])
  
  def testCustomRequest(self):
    request = json.dumps({
      'id'      : 1,
      'service' : 'test.Service',
      'method'  : 'today',
      'params'  : ()
    })
    headers = [('content-length', len(request))]
    
    self.getPage('/customrequest', method = 'post', body = request, headers = headers)
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    response = json.loads(self.body)
    self.assertTrue(response['error'] is None)
    
    self.assertEqual([
      u'2012-03-17T19:09:12.217000', 
      u'2012-03-17', 
      u'2012-03-17T19:09:12.217000+02:00'
    ], response['result'])


class TestFile(test.TestCase):
  
  def testDownloadStringIo(self):
    self._post('downloadStringIo')
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/octet-stream')

    self.assertEqual(3528, len(self.body))
    self.assertEqual('06184ee1826a72ff03a70905219d7ea4', hashlib.md5(self.body).hexdigest())
  
  def testDownloadFileIo(self):
    self._post('downloadFileIo')
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/octet-stream')

    self.assertEqual(256 * 1024, len(self.body))
    self.assertEqual('e46bef01e89e00cdb2622f94c6e430f1', hashlib.md5(self.body).hexdigest())
    
  def testUpload(self):
    boundary  = '900150983cd24fb0d6963f7d28e17f72'
    bodyLines = []
    def addLine(name, value, type = None):
      bodyLines.append('--' + boundary)
      bodyLines.append('Content-Disposition: {0}'.format(name))
      if type:
        bodyLines.append('Content-Type: {0}'.format(type))
      bodyLines.append('')
      bodyLines.append(value)
    addLine(
      'form-data; name="_ScriptTransport_id"',
      '123'
    )
    addLine(
      'form-data; name="_ScriptTransport_data"',
      urllib.quote(json.dumps({
        'id'      : 1,
        'service' : 'test.Service',
        'method'  : 'upload',
        'params'  : [dict(v = 1209)]
      }))
    )
    addLine(
      'form-data; name="random-binary"; filename="upload.bin"',
      open(os.path.dirname(__file__) + '/fixture/binary', 'rb').read(),
      'application/octet-stream',
    )
    bodyLines.append('--' + boundary + '--')
    
    body    = '\r\n'.join(bodyLines)
    headers = [
      ('content-type',   'multipart/form-data; boundary={0}'.format(boundary)),
      ('content-length', len(body))
    ]
    
    self.getPage('/service', method = 'post', body = body, headers = headers)
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'text/plain;charset=utf-8')
    
    response = json.loads(self.body)
    self.assertTrue(response['error'] is None)
    self.assertEqual(dict(v = 1209), response['result']['passthrough'])
    self.assertEqual('e46bef01e89e00cdb2622f94c6e430f1', response['result']['hash'])
