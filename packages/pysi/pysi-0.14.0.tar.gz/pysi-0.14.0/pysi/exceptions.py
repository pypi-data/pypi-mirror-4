# -*- coding: utf-8 -*-
import wsgi


class HttpError(Exception): pass

class BasicAuth(Exception):
    def __init__(self):
        self.res = wsgi.Response('Authorization Error',
            code=401, content_type='text/plain',
            headers={'WWW-Authenticate' : 'Basic realm="Enter password"'},
        )
