import hashlib
import hmac
import json
import urllib2
import logging

class GroovesharkException(Exception):
  pass


class Grooveshark:

  def __init__(self, key, secret, token=None):
    self.key = key
    self.secret = secret
    self._session_id = None
    self.authenticated = False
    self.user_id = None

  def session_id():
      doc = "The session_id property."
      def fget(self):
          if not self._session_id:
              logging.info("No Session ID; retrieving..")
              url, params = self._build_request('startSession')
              self._session_id = self._make_request(url, params)['result']['sessionID']
          return self._session_id
      def fset(self, value):
          self._session_id = value
      def fdel(self):
          del self._session_id
      return locals()
  session_id = property(**session_id())

# This method copied heavily from https://github.com/pixfabrik/grooveshark_py/blob/master/__init__.py#L28
  def _build_request(self, method, params={}, session_id=None):
    logging.info("REQUEST: %s (%s), Session ID: %s" % (method, params, session_id))
    host = 'api.grooveshark.com'
    endpoint = 'ws3.php'
    protocol = 'http'
    # authenticate, authenticateUser, authenticateToken
    if method == 'startSession' or method.startswith('authenticate'):
      protocol = 'https'

    header = {"wsKey": self.key}
    if session_id:
      header["sessionID"] = session_id

    request = {"method": method, "header": header, "parameters": params}
    request_json = json.dumps(request)
    sig = hmac.new(self.secret, request_json).hexdigest()
    url = "%(protocol)s://%(host)s/%(endpoint)s?sig=%(signature)s" % {
      'protocol': protocol,
      'host': host,
      'endpoint': endpoint,
      'signature': sig
    }
    return url, request_json

  def _user_token(self, username, password):
    token = hashlib.md5(username.lower() + hashlib.md5(password).hexdigest())
    return token.hexdigest()

  def authenticate(self, username, password):
    logging.info("AUTHENTICATE: %s, %s" % (username, password))
    response = self.call('authenticateUser', {'username': username.lower(), 'token': self._user_token(username, password)})
    if 'errors' in response:
      # TODO: what if there's more than one error?
      raise GroovesharkException(response['errors'][0]['message'])
    else:
      # We assume that the authenticate went successfully, because there are no error messages in the response.
      self.user_id = response['result']['UserID']
      self.user_email = response['result']['emailAddress']
      self.username = username
      self.authenticated = True
      return True

  def call(self, method, params={}):
    logging.info("%s: %s" % (method, params))
    AUTHENTICATION_REQUIRED_METHODS = ['getUserLibrarySongs', 'getUserPlaylists']
    if method in AUTHENTICATION_REQUIRED_METHODS and not self.authenticated:
      raise GroovesharkException("Method requires an authenticated session.")
    url, params = self._build_request(method, params, self.session_id)
    response = self._make_request(url, params)
    return response

  # Expects params to already be urlencoded/etc.
  def _make_request(self, url, params):
    logging.info("MAKING REQUEST: %s (%s)" % (url, params))
    req = urllib2.Request(url, params)
    response = urllib2.urlopen(req)
    return json.loads(response.read())