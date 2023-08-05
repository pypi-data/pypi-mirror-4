import urlparse, urllib2, hashlib, base64
from datetime import datetime
from . import http

class Gateway(object):
	def __init__(self, environment, api_key, api_secret):
		self._environment = environment
		self._api_key = api_key
		self._api_secret = api_secret

		auth_handler = http.HTTPPreemptiveBasicAuthHandler()
		auth_handler.add_password(
			realm=None,
			uri=self.environment.base_url,
			user=self.api_key,
			passwd=self.api_secret
		)
		https_handler = http.HTTPSHandler()
		self._url_opener = urllib2.build_opener(https_handler, auth_handler)

	@property
	def environment(self):
		return self._environment

	@property
	def api_key(self):
		return self._api_key

	@property
	def api_secret(self):
		return self._api_secret

	@property
	def url_opener(self):
		return self._url_opener	
