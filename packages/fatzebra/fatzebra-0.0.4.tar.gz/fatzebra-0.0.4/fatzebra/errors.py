class GatewayError(Exception):
    def __init__(self, errors=None):
        self.errors = errors or []

    def __str__(self):
        return ', '.join(self.errors)

class AuthenticationError(Exception):
    pass

class GatewayUnknownResponseError(Exception):
    def __init__(self, code, response):
        self.code = code
        self.response = response

    def __str__(self):
        return '%s: %s' % (self.code, self.response)
