import oauth.oauth as oauth
import httplib
import json
import sys
import requests

class BaseClient:

	def __init__(self, baseURL, key, secret, api_version = 0, debug_level = 0):
		self.url = baseURL
		self.consumer = oauth.OAuthConsumer(str(key), str(secret))
		self.api_key = key
		self.api_secret = secret
		self.debug_level = debug_level
		self.api_version = api_version
	
	def _debug(self, s):
		if(self.debug_level > 0):
			print "%s\n"%(s)
		
	def _execute(self, http_method, path, body, typeHints):
		if path[0] == '/': path = path[1:]
		full_url = "http://%s/%s"%(self.url, path)
		
		request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, http_method=http_method, http_url=full_url)
		request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), self.consumer, None)
		
		headers = request.to_header()
		headers["Content-Type"] = "application/json"
		headers["Accept"] = "application/vnd.stackmob+json; version=%d"%(self.api_version)
		headers["X-StackMob-API-Key"] = str(self.api_key)
		headers["User-Agent"] = "StackMob Python"
		headers["X-StackMob-Relations"] = typeHints
		self._debug("%s %s %s"%(http_method, full_url, body))
		self._debug(headers)
		
		body_string = ''
		if(body != None):
			self._debug("\n%s"%(body_string))
			body_string = json.dumps(body)
		
		
		if http_method == 'GET':
			return requests.get(full_url, headers = headers)
		elif http_method == 'POST':
			return requests.post(full_url, headers = headers, data = body_string)
		elif http_method == 'PUT':
			return requests.put(full_url, headers = headers, data = body_string)
		elif http_method == 'DELETE':
			return requests.delete(full_url, headers = headers)
	
	def get(self, path):
		return self._execute("GET", path, None)
	def post(self, path, body, hints):
		return self._execute("POST", path, body, hints)
	def put(self, path, body):
		return self._execute("PUT", path, body)
	def delete(self, path):
		return self._execute("DELETE", path, None)

class DatastoreClient(BaseClient):
	def __init__(self, key, secret, debug_level = 0, api_version = 0):
		BaseClient.__init__(self, "api.stackmob.com", key, secret, debug_level=debug_level, api_version=api_version)
