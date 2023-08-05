# -*- coding: utf-8 -*-


class Cfg(object):
    DEBUG = False
    BASIC_AUTH_SSL_ONLY = False  # basic-авторизация только по https
    BASIC_AUTH_DB = {}
    INSTALLED_APPS = []
    CONTEXT_PROCESSORS = []
    REQUEST_MIDDLEWARES = []
    RESPONSE_MIDDLEWARES = []
    MIDDLEWARES = []
    CHARSET = 'utf-8'
    POST_MAX_SIZE = 1024 * 1024 * 1  # максимальный размер пост-данных, None - не ограничивать
    POST_MAX_MEMFILE = 1024 * 100  # максимальный размер POST-данных, загружаемый в память. Если больше, создаётся временный файл.
    ERROR_PAGES = {}
    TEMPLATE_CACHE_SIZE = 250
    TEMPLATE_AUTO_RELOAD = False
    TEMPLATE_LOADER = 'pysi.template.file_loader'
    FLASH_COOKIE_NAME = u'pysi.flash'
    ROUTING_QUEUE = ['pysi.auto_routing']  # очередь функций роутинга
    JINJA2_EXTENSIONS = ['jinja2.ext.with_']

    STATIC_PATH = 'static'
    STATIC_URL_PREFIX  = '/static/'
    STATIC_VERSION_CACHING = True  # кэшировать посчитанные версионные хеши

    def set_defaults(self, **kwargs):
        '''
        Добавляем дефолтные атрибуты
        '''
        for k, v in kwargs.iteritems():
            if not hasattr(self, k) and k.isupper():
                setattr(self, k, v)

cfg = Cfg()
