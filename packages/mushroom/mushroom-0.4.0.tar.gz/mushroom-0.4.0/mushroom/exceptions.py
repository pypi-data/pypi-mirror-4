class HttpError(RuntimeError):
    code = ''
    message = ''
    headers = {}

    def __init__(self, message=None):
        self.message = message or self.message
        super(HttpError, self).__init__(self.message)


class HttpUnauthorized(HttpError):
    code = '401 Unauthorized'
    def __init__(self, auth_scheme=None):
        if not auth_scheme:
            auth_scheme = 'Mushroom'
        self.headers = [
            ('WWW-Authenticate', auth_scheme)
        ]
        super(HttpUnauthorized, self).__init__()


class HttpNotFound(HttpError):
    code = '404 Not Found'


class HttpMethodNotAllowed(HttpError):
    code = '405 Method Not Allowed'
    def __init__(self, allowed_methods):
        self.headers = [
            ('Allow', ', '.join(method.upper() for method in allowed_methods))
        ]
        super(HttpMethodNotAllowed, self).__init__()


class HttpInternalServerError(HttpError):
    code = '500 Internal Server Error'


class HttpNotImplemented(HttpError):
    code = '501 Not Implemented'
