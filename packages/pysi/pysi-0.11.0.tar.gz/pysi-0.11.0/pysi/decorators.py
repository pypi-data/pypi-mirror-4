# -*- coding: utf-8 -*-
from wsgi import Response
from exceptions import BasicAuth
from routing import urls
from config import cfg
from util import anticache_headers
from template import render


def view(url_or_code, render_to=None, **response_kwargs):
    '''
    *url_or_code - урл для роутинга или код http-ошибки
    *render_to   - шаблон или 'json', 'text', 'html'
    '''
    def decorator(func):
        urlname = _get_urlname(func)
        if render_to:
            real_func = func
            def func(rq, *args, **kwargs):
                res = real_func(rq, *args, **kwargs)
                if isinstance(res, Response):
                    return res
                return render(rq, render_to, res, **response_kwargs)
            func._pysi_urlname = urlname
        if isinstance(url_or_code, int):
            cfg.ERROR_PAGES[url_or_code] = func
        else:
            urls.add_rule(url_or_code, func, urlname)
        return func
    return decorator

def anticache(func):
    ''' Декоратор браузерного антикэша '''
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        res.headers.update(anticache_headers())
        return res
    wrapper._pysi_urlname = _get_urlname(func)
    return wrapper

def basic_auth(func):
    '''
    Basic-авторизация.
    '''
    def wrapper(rq, *args, **kwargs):
        rq.basic_user
        return func(rq, *args, **kwargs)
    wrapper._pysi_urlname = _get_urlname(func)
    return wrapper

def _get_urlname(func):
    if not getattr(func, '_pysi_urlname', None):
        mod_name = func.func_globals['__name__']
        app_name = mod_name[:-6] if mod_name.endswith('.views') else None
        urlname = '%s.%s' % (app_name, func.__name__) if app_name else func.__name__
        setattr(func, '_pysi_urlname', urlname)
    return func._pysi_urlname