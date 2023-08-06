
class ApiException(Exception):
	def __init__(self, type, message=None, code=None, body=None):
		super(ApiException, self).__init__(message)	
		self.type = type
		self.code = code
		self.body = body

	@staticmethod
	def create(type, message=None, code=None, body=None):
		if type == 'request-error':
			return RequestException(message, code, body)
		elif type == 'authentication-error':
			return AuthenticationException(message, code, body)
		elif type == 'server-error':
			return ServerException(message, code, body)
		elif type == 'validation-error':
			return ValidationException(message, code, body)
		elif type == 'resource-error':
			return ResourceException(message, code, body)
		elif type == 'card-error':
			return CardException(message, code, body)

class InvalidSignatureException(Exception):
	pass

class RequestException(ApiException):
	def __init__(self, message=None, code=None, body=None):
		super(RequestException, self).__init__('request-error', message, code, body)

class AuthenticationException(ApiException):
	def __init__(self, message=None, code=None, body=None):
		super(AuthenticationException, self).__init__('authentication-error', message, code, body)

class ServerException(ApiException):
	def __init__(self, message=None, code=None, body=None):
		super(ServerException, self).__init__('server-error', message, code, body)

class ValidationException(ApiException):
	def __init__(self, message=None, code=None, body=None):
		super(ValidationException, self).__init__('validation-error', message, code, body)

class ResourceException(ApiException):
	def __init__(self, message=None, code=None, body=None):
		super(ResourceException, self).__init__('resource-error', message, code, body)

class CardException(ApiException):
	def __init__(self, message=None, code=None, body=None):
		super(CardException, self).__init__('card-error', message, code, body)
