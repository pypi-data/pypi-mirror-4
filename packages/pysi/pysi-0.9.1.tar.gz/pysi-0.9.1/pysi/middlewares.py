# -*- coding: utf-8 -*-
import marshal
import base64

from pysi import cfg
from util import anticache_headers


cfg.set_defaults(
    BASIC_AUTH_PREFIXES = ('/', ),
    ANTICACHE_PREFIXES = ('/', ),
)

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

    

