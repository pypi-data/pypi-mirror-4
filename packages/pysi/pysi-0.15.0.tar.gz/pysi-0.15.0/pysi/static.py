import os
import logging
import hashlib

from config import cfg


log = logging.getLogger(__name__)
VERSION_CACHE = {}  # {path : version_hash}


def static_url(path, caching=None, prefix=None):
    path = path.lstrip('/')
    if caching is None:
        caching = cfg.STATIC_VERSION_CACHING
    if prefix is None:
        prefix = cfg.STATIC_URL_PREFIX
    ret = '/%s/%s' % (prefix.strip('/'), path)
    version_hash = get_version(path, caching)
    if version_hash:
        ret += "?v=" + version_hash
    return ret

def get_version(path, caching):
    if caching:
        try:
            return VERSION_CACHE[path]
        except KeyError:
            pass
    log.debug(u'Calculate version hash for static file %s' % path)
    abs_path = os.path.join(cfg.STATIC_PATH, path)
    try:
        f = open(abs_path, "rb")
        ret = hashlib.md5(f.read()).hexdigest()[:5]
        f.close()
    except Exception:
        log.error(u'Could not open static file %r', path)
        ret = None
    if caching:
        VERSION_CACHE[path] = ret
    return ret
