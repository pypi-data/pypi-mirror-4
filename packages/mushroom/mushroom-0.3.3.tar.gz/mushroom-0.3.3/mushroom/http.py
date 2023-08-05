try:
    import simplejson as json
except:
    import json


class HttpRequest(object):

    def __init__(self, environ):
        # FIXME add validation
        self.environ = environ
        self.method = environ['REQUEST_METHOD']
        self.raw_data = environ['wsgi.input'].read()
        if self.raw_data:
            self.data = json.loads(self.raw_data)
        else:
            self.data = None
        # Convert path to list of atoms
        self.path = filter(bool, environ['PATH_INFO'].split('/'))


class HttpResponse(object):

    def __init__(self, code='200 OK', content='', extra_headers=None):
        self.code = code
        self.content = content
        self.headers = {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'text/plain',
        }
        self.headers.update(extra_headers or {})


class JsonResponse(HttpResponse):

    def __init__(self, data):
        super(JsonResponse, self).__init__(
            content=json.dumps(data),
            extra_headers={
                'Content-Type': 'application/json',
            }
        )
