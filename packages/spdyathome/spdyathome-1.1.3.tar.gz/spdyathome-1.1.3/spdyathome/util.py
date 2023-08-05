"""
General purpose helpers and decorators
"""
import random
import os
import string


def register_all(cls):
    for methodname in dir(cls):
        method = getattr(cls, methodname)
        if hasattr(method, '_route') and hasattr(method, '_method'):
            cls.paths[make_ident(method._method, method._route)] = method


def register(method, path, *args):
    def wrapper(func):
        func._route = path
        func._method = method
        return func
    return wrapper

def rel_path(f):
    dirpath = os.path.dirname(__file__)
    return os.path.join(dirpath, f)

def make_ident(method, route):
    """
    For the time being, if a path ends in '/', it expects an argument to follow
    """
    # FIXME: This path stuff is dumb. Do this better if time permits
    parts = route.rstrip('/1234567890.cu')
    return method + '->' + parts


def make_ident_spdy(method, route):
    """
    For the time being, if a path ends in '/', it expects an argument to follow
    """
    # FIXME: This path stuff is dumb. Do this better if time permits
    parts = route.rstrip('/1234567890.cu').split('/')[-1]
    return method + '->' + parts


def fill_junk(size):
    return ''.join([random.choice(string.letters) for i in xrange(size)])


def load_list(f):
    ls = []
    for line in open(rel_path(f), 'r'):
        ls.append(line.split()[0])
    return ls


def make_assets(site):
    assets = []
    for asset in site['assets'].values():
        if asset['compressible']:
            trailer = '.c'
        else:
            trailer = '.u'
        if asset['remote']:
            header = 'host2/'
        else:
            header = 'host1/'
        assets.append(header + str(asset['size']) + trailer)
    return assets


class resmap(object):

    def __init__(self, func, uri):
        self.func = func
        self.uri = uri

    def response_start(self, code, phrase, headers):
        x, y = self.func(code,
                phrase,
                headers,
                dummy)
        self.response_body = self.resp_body_wrap(x)
        self.response_done = self.resp_done_wrap(y)

    def resp_body_wrap(self, func):
        def wrap(body):
            func(body)
        return wrap

    def resp_done_wrap(self, func):
        def wrap(body):
            func(body)
        return wrap
