'''
This bottle-pycassa plugin allows for the passing of Cassandra Connection pools
around your application

The plugin inject an argument to all route callbacks that require a `db`
keyword.

Usage Example::

    import bottle
    from bottle import HTTPError
    from bottle.ext import pycassa
    from pycassa.pool import ConnectionPool
    from pycassa.columnfamily import ColumnFamily
    from pycassa import NotFoundException

    pool = ConnectionPool(keyspace, hosts, pool_timeout = 5, pool_size=24)

    app = bottle.Bottle()
    plugin = pycassa.Plugin(pool, keyword="cass")
    app.install(plugin)


    @app.get('/:query')
    def show(query, cass):
        my_column_family = ColumnFamily(cass, 'my_column_family_name')

        try:
            result = my_column_family.get(query)
            return(result)
        except NotFoundException, nfe:
            return HTTPError(404, 'Entity not found.') 

Copyright (c) 2012, David McNelis
License: MIT (see LICENSE for details)
'''

import inspect

import bottle
from pycassa.pool import ConnectionPool

# PluginError is defined to bottle >= 0.10
if not hasattr(bottle, 'PluginError'):
    class PluginError(bottle.BottleException):
        pass
    bottle.PluginError = PluginError

class PycassaPlugin(object):

    name = 'pycassa'
    api = 2

    def __init__(self, pool, 
                 keyword='cass', use_kwargs=False):
        '''
        :param pool: pycassa pool, created with pycassa.pool.ConnectionPool
        :param keyword: Keyword used to inject session database in a route

        '''
        self.pool = pool
        self.keyword = keyword
        self.use_kwargs = use_kwargs


    def setup(self, app):
        ''' Make sure that other installed plugins don't affect the same
            keyword argument and check if metadata is available.'''
        for other in app.plugins:
            if not isinstance(other, PycassaPlugin):
                continue
            if other.keyword == self.keyword:
                raise bottle.PluginError("Found another SQLAlchemy plugin with "\
                                  "conflicting settings (non-unique keyword).")
            elif other.name == self.name:
                self.name += '_%s' % self.keyword

    def apply(self, callback, route):
        # hack to support bottle v0.9.x
        if bottle.__version__.startswith('0.9'):
            allconfig = route['config']
            _callback = route['callback']
        else:
            allconfig = route.config
            _callback = route.callback

        config = allconfig.get('pycassa', {})
        keyword = config.get('keyword', self.keyword)
        use_kwargs = config.get('use_kwargs', self.use_kwargs)

        argspec = inspect.getargspec(_callback)
        if not ((use_kwargs and argspec.keywords) or keyword in argspec.args):
            return callback

        def wrapper(*args, **kwargs):
            kwargs[keyword] = self.pool
            try:
                rv = callback(*args, **kwargs)

            except bottle.HTTPError:
                raise
            except bottle.HTTPResponse:
                raise
            return rv

        return wrapper


Plugin = PycassaPlugin
