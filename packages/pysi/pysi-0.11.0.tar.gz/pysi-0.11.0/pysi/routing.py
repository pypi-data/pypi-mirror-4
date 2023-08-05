# -*- coding: utf-8 -*-
import urllib
import datetime

def main():
    # добавление
    m = Map()
    m.add_rule('/user/<int:id>/', 'user1', 'user')
    m.add_rule('/user/<int:id>/<str:name>/', 'user2', 'user')
    m.add_rule('/user/<*:slug>', 'user3', 'user')

    from om.pp import pp
    pp(m.queue)
    pp(m.rev)
    return

    print m.find('/user/41/---/')
    print m.reverse('user', id=1)
    print m.reverse('user', id=1, name='pysi', x=4)
    print m.reverse('user', slug='ddd/bbb/sss/')


class Map(object):
    queue = []
    rev = {}
    charset = 'utf-8'
    url_prefix = None

    def add_rule(self, url, target, urlname=None):
        if self.url_prefix:
            url = '/%s/%s' % (self.url_prefix, url.lstrip('/'))
        match_funcs = []  # функции проверки папок пути
        path_size = None  # длина пути, -1 = бесконечный
        rev_chunks = ['']
        var_names = []
        for dir in url.lstrip('/ ').split('/'):
            func = get_match(dir)
            if func.__name__ == 'slug_dir':
                path_size = -1
            match_funcs.append(func)
            if dir.startswith('<') and dir.endswith('>'):
                var_type, var_name = dir[1:-1].split(':')
                rev_chunks.append(REVERSES[var_type](var_name))
                var_names.append(var_name)
            else:
                rev_chunks.append(dir)
        if path_size is None:
            path_size = len(match_funcs)
        self.queue.append((match_funcs, path_size, var_names, target))
        if urlname:
            self.rev.setdefault(urlname, []).append(
                ('/'.join(rev_chunks), var_names))
            if len(self.rev[urlname]) > 1:
                # сортируем, чтобы reverse использовал максимум переменных
                self.rev[urlname].sort(key=lambda x: -len(x[1]))

    def find(self, url):
        dirs = url.lstrip('/ ').split('/')
        for match_funcs, path_size, var_names, target in self.queue:
            if path_size == -1 or path_size == len(dirs):
                vals = []
                for i, func in enumerate(match_funcs):
                    match, val = func(dirs[i])
                    if match:
                        if val is not None:
                            if val == '<//__slug__//>':
                                vals.append('/'.join(dirs[i:]))
                            else:
                                vals.append(val)
                    else:
                        break
                else:
                    return target, dict(zip(var_names, vals)) if vals else {}
        return None, None

    def reverse(self, urlname, **kwargs):
        try:
            items = self.rev[urlname]
        except KeyError:
            assert 0, 'Could not find url for "%s"' % urlname
        # выбераем с максимальным количеством используемых переменных
        for tpl, vars in items:
            try:
                url = urllib.quote(tpl % kwargs)
            except (TypeError, KeyError):
                pass
            else:
                # GET параметры
                if len(kwargs) > len(vars):
                    ext_vars = {}
                    for k, v in kwargs.iteritems():
                        if k not in vars:
                            if isinstance(v, unicode):
                                v = v.encode(self.charset)
                            ext_vars[k] = v
                    if ext_vars:
                        url += '?' + urllib.urlencode(ext_vars)
                return url
        assert 0, 'Could not find url for "%s" witch kwargs: %s' % (urlname,
            ', '.join('%s %s' % (k, type(v)) for k, v in kwargs.iteritems()))

def match_const(var):
    def const_dir(dir):
        return dir == var, None
    return const_dir

def match_str(var):
    def str_dir(dir):
        return True, urllib.unquote_plus(dir)
    return str_dir

def match_int(var):
    def int_dir(dir):
        if dir.isdigit():
            return True, int(dir)
        else:
            return False, None
    return int_dir

def match_date(var):
    def data_dir(dir):
        try:
            dt = datetime.datetime.strptime(dir, '%Y-%m-%d')
        except:
            return False, None
        return True, datetime.date(dt.year, dt.month, dt.day)
    return data_dir

def match_slug(var):
    def slug_dir(dir):
        return (True, '<//__slug__//>')
    return slug_dir


MATCHS = {
    'int': match_int,
    'str': match_str,
    'date': match_date,
    '*': match_slug,
}

def get_match(dir):
    if dir.startswith('<') and dir.endswith('>'):
        name = dir[1:-1]
        name, var = name.split(':')
        func = MATCHS.get(name)
        if func:
            return func(dir)
    return match_const(dir)

REVERSES = {
    'int': lambda var: '%%(%s)i' % var,
    'str': lambda var: '%%(%s)s' % var,
    'date': lambda var: '%%(%s)s' % var,
    '*': lambda var: '%%(%s)s' % var,
}


if __name__ == '__main__':
    main()
else:
    #######################
    ### Привязка к pysi ###
    #######################
    from config import cfg
    import wsgi


    urls = Map()
    urls.charset = cfg.CHARSET

    def auto_routing(rq):
        '''
        Автоматический роутинг
        '''
        func, kwargs = urls.find(rq.path)
        if func is None:
            if not rq.path.endswith('/'):
                # забыли закрывающий слеш?
                func, kwargs = urls.find(rq.path + '/')
                if func:
                    return wsgi.redirect(rq.path + '/')
            wsgi.abort(404)
        return func(rq, **kwargs)

    def add_urls(*rules):
        ''' Добавление правил списком'''
        for rule in rules:
            urls.add_rule(*rule)

    def url4(*args, **kwargs):
        return urls.reverse(*args, **kwargs)

    def add_apps(apps):
        '''
        Добавление приложений
            apps = ['mod1', ('mod2', url_prefix), 'mod3']
        '''
        for mod in apps:
            if isinstance(mod, tuple):
                mod, prefix = mod
                urls.url_prefix = prefix.strip().strip('/') or None
            app_name = '%s.%s' % (mod, 'views')
            __import__(app_name)
            urls.url_prefix = None

