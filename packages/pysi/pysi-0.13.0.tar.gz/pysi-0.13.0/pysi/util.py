# -*- coding: utf-8 -*-
import sys
import datetime
import traceback


WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug',
    'Sep', 'Oct', 'Nov', 'Dec']


def obj_from_str(str_or_obj):
    '''
    Если передана строка, пытается проимпортировать модуль и вернуть объект.
    '''
    if isinstance(str_or_obj, basestring):
        if '.' not in str_or_obj:
            str_or_obj = str_or_obj + '.'
        mod_name, obj_name = str_or_obj.rsplit('.', 1)
        __import__(mod_name)
        mod = sys.modules[mod_name]
        return getattr(mod, obj_name) if obj_name else mod
    else:
        return str_or_obj

def list_obj_from_str(lst):
    for i, obj in enumerate(lst):
        lst[i] = obj_from_str(obj)
    return lst

class cached_property(object):
    def __init__(self, f):
        self.f = f

    def __get__(self, instance, owner):
        value = self.f(instance)
        setattr(instance, self.f.__name__, value)
        return value

def cached_function(func):
    '''
    Кешируемая функция
    '''
    def _func(*args, **kwargs):
        try:
            return _func._retval
        except AttributeError:
            _func._retval = func(*args, **kwargs)
            return _func._retval
    return _func

def make_traceback(host):
    head = '%s | %s' % (host, datetime.datetime.now())
    line = '-' * len(head)
    return '\n%s\n%s\n%s\n%s' % (line, head, line,
        ''.join(traceback.format_exception(*sys.exc_info())[1:]))

def anticache_headers():
    expires = http_date(datetime.datetime.utcnow())
    return {
        'Expires' : expires,
        'Last-Modified' : expires,
        'Pragma' : 'no-cache',
        'Cache-Control' : 'private, no-cache, no-store, must-revalidate, max-age=0, pre-check=0, post-check=0',
    }

def http_date(dt):
    '''
    Дата обновления документа в http формате
    '''
    week = WEEKDAYS[dt.weekday()]
    month = MONTHS[dt.month - 1]
    return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (week, dt.day, month,
        dt.year, dt.hour, dt.minute, dt.second)
