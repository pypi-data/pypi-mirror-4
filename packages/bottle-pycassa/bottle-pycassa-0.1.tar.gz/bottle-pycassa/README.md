bottle-pycassa
==============

Plugin for bottle to allow for cassandra connection pools

Usage example:
```
import bottle
from bottle import run, get
from bottle import HTTPError
from bottle.ext import pycassa
from pycassa.pool import ConnectionPool
from pycassa.columnfamily import ColumnFamily
from pycassa import NotFoundException

pool = ConnectionPool("my_keyspace", 
    ['127.0.0.1'], 
    pool_timeout = 5, pool_size=24)

app = bottle.Bottle()
plugin = pycassa.Plugin(pool, keyword="cass")
app.install(plugin)


@app.get('/:query')
def show(query, cass):
    my_column_family = ColumnFamily(cass, 'my_column_family')

    try:
        result = my_column_family.get(1167864277)
        return result
    except NotFoundException, nfe:
        return HTTPError(404, 'Entity not found.') 

run(app=app, host='localhost', port=80, reloader=True)
```