# -*- coding: utf-8 -*-
import marshal
import base64
import uuid

try:
    from jinja2 import Markup
except ImportError:
    Makrup = None

from pysi import cfg
from util import anticache_headers
from wsgi import get_error_page


cfg.set_defaults(
    BASIC_AUTH_PREFIXES = ('/', ),
    ANTICACHE_PREFIXES = ('/', ),
    CSRF_TOKEN_COOKIE_NAME = 'csrf',
    CSRF_TOKEN_POST_NAME = 'csrf',
    CSRF_TOKEN_TEMPLATE_NAME = 'csrf',
    CSRF_TOKEN_TEMPLATE_INPUT_NAME = 'csrf_token',
    CSRF_EXEMPT_PREFIXES = (),
)


class CSRF(object):
    def process_request(self, rq):
        token = rq.COOKIES.get(cfg.CSRF_TOKEN_COOKIE_NAME)
        if token:
            token = token.value
        if rq.method == 'POST':
            if not rq.path.startswith(cfg.CSRF_EXEMPT_PREFIXES):
                if token != rq.POST.get(cfg.CSRF_TOKEN_POST_NAME):
                    res = get_error_page(rq, 403)
                    if token is not None:
                        res.delete_cookie(cfg.CSRF_TOKEN_COOKIE_NAME)
                    raise res
        token = token or uuid.uuid4().hex
        rq.context[cfg.CSRF_TOKEN_TEMPLATE_NAME] = token
        if Markup:
            rq.context[cfg.CSRF_TOKEN_TEMPLATE_INPUT_NAME] = Markup(
                '<div style="display:none">' +
                '<input type="hidden" name="%s" value="%s" /></div>' %
                    (cfg.CSRF_TOKEN_TEMPLATE_NAME, token))

    def process_response(self, rq, res):
        if cfg.CSRF_TOKEN_COOKIE_NAME not in rq.COOKIES:
            res.set_cookie(cfg.CSRF_TOKEN_COOKIE_NAME,
                    rq.context[cfg.CSRF_TOKEN_TEMPLATE_NAME])


class BasicAuth(object):
    def process_request(self, rq):
        if rq.path.startswith(cfg.BASIC_AUTH_PREFIXES):
            rq.basic_user


class AntiCache(object):
    def process_response(self, rq, res):
        '''Browser anti-cache response middleware'''
        if rq.path.startswith(cfg.ANTICACHE_PREFIXES):
            res.headers.update(anticache_headers())


class Flash(object):
    def process_response(self, rq, res):
        '''Flash messages response middleware'''
        if rq._new_flashes:
            val = base64.urlsafe_b64encode(marshal.dumps(rq._new_flashes))
            res.set_cookie(cfg.FLASH_COOKIE_NAME, val)
        elif rq._clear_flashes:
            res.delete_cookie(cfg.FLASH_COOKIE_NAME)



