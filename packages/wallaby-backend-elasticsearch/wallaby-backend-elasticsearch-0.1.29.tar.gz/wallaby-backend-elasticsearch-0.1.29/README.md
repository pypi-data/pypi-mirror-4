wallaby-backend-elasticsearch
=============================

This package provides an asynchronous python interface to elasticsearch (using twisted).

Installation
============

You can install the elasticsearch backend with pip

```bash
pip install wallaby-backend-elasticsearch
```

How to use
==========

The library is based on twisted's asynchronous pattern. To use the library in an asynchronous fassion you 
first need to create an reactor based application:
 
```python
from twisted.internet import defer

@defer.inlineCallbacks
def run():
    # wait 1 second
    d = defer.Deferred()
    reactor.callLater(1.0, d.callback)
    yield d

    # stop the reactor and quit the application
    reactor.stop()

from twisted.internet import reactor
reactor.callWhenRunning(run)
reactor.run()
```

Now we can connect to an existing elasticsearch cluster:

```python
@defer.inlineCallbacks
def run():
    # Create elasticsearch client object
    from wallaby.backends.elasticsearch import Connection
    es = Connection(
        baseURL="http://localhost:9200",
        index="<name of index>",
        username="<username>", 
        password="<password>",
    )

    # Send query
    res = yield es.doQuery({
            "query": {
                "query_string": {
                    "query": "*"
                }
            }
        })

    # stop the reactor and quit the application
    reactor.stop()
```
