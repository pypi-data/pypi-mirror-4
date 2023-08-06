import urllib2, base64, ssl, httplib, os, socket

class HTTPPreemptiveBasicAuthHandler(urllib2.BaseHandler):
	def __init__(self):
		self.passwd = urllib2.HTTPPasswordMgrWithDefaultRealm()
		self.add_password = self.passwd.add_password
	
	def https_request(self, request):
		return self.http_request(request)
		
	def http_request(self, request):
		uri = request.get_full_url()
		user, passwd = self.passwd.find_user_password(None, uri)

		if passwd is None:
			return request

		auth = 'Basic %s' % base64.b64encode('%s:%s' % (user, passwd)).strip()
		request.add_unredirected_header('Authorization', auth)
		return request	

class HTTPSConnection(httplib.HTTPSConnection):
	def connect(self):
		sock = socket.create_connection((self.host, self.port), self.timeout)
		if self._tunnel_host:
			self.sock = sock
			self._tunnel()
		self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file, cert_reqs = ssl.CERT_REQUIRED, ca_certs='%s/thawte.pem' % os.path.dirname(__file__))

		cert = self.sock.getpeercert()
		subject = dict((i[0][0], i[0][1]) for i in cert['subject'])

		if not self.host == subject['commonName']:
			if subject['commonName'][0] != '*' or subject['commonName'][2:] != self.host[-len(subject['commonName'][2:]):]: 
				self.sock.close()
				raise Exception('Invalid certificate presented for domain %s' % self.host)		

class HTTPSHandler(urllib2.HTTPSHandler):
	def __init__(self):
		self.https_conn_class = HTTPSConnection
		urllib2.HTTPSHandler.__init__(self)

	def https_open(self, req):
		return self.do_open(self.https_conn_class, req)
	
