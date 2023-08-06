
from .gateway import Gateway

class ConfigurationException(Exception):
	pass

class Environment(object):
	def __init__(self, server, port, is_ssl, version):
		self._server = server
		self._port = port
		self._is_ssl = is_ssl
		self._version = version

	@property
	def base_url(self):
		return "%s://%s/v%s" % (self.scheme, self.host, self._version)

	@property
	def scheme(self):
		return "https" if self._is_ssl else "http"
	
	@property
	def host(self):
		if self._port == "443" and self._is_ssl:
			return self._server
		elif self._port == "80" and not self._is_ssl:
			return self._server
		else:
			return "%s:%s" % (self._server, self._port)

	@property
	def version(self):
		return self._version

Environment.Development = Environment("dev.app55.com", "80", False, 1)
Environment.Sandbox = Environment("sandbox.app55.com", "443", True, 1)
Environment.Production = Environment("api.app55.com", "443", True, 1)

