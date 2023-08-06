# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from twisted.internet import task, defer
import re, time, os
import json, base64
from twisted.python.failure import *
from twisted.internet.error import ConnectionRefusedError, DNSLookupError, ConnectionLost
from wallaby.backends.http import JSONProtocol, DataProducer, WebClientContextFactory, UnknownError
from twisted.web.client import Agent
from twisted.web.http_headers import Headers

class Connection(object):
    connections = {}
    urls = {} 
    logins = {}

    @staticmethod
    def setURLForIndex(index, url):
        Connection.urls[index] = url 

    @staticmethod
    def setLoginForIndex(index, user, pwd):
        Connection.logins[index] = (user, pwd) 

    @staticmethod
    def getConnectionForIndex(index, *args, **ka):
        url = u'http://localhost:9200'

        if index in Connection.urls:
            url = str(Connection.urls[index])
        elif None in Connection.urls:
            url = str(Connection.urls[None])

        baseURL = url

        url = url + '/' + str(index)

        if index in Connection.logins:
            login = Connection.logins[index]
        elif None in Connection.logins:
            login = Connection.logins[None]
        
            return Connection.getConnection(url, username=login[0], password=login[1], baseURL=baseURL, index=index, *args, **ka)
        else:
            return Connection.getConnection(url, baseURL=baseURL, index=index, *args, **ka)

    @staticmethod
    def getConnection(url, *args, **ka):
        if url not in Connection.connections:
            Connection.connections[url] = Connection(url + '/_search', *args, **ka)

        return Connection.connections[url]

    def __init__(self, url=None, baseURL=None, index=None, username=None, password=None):
        self._baseURL = str(baseURL)
        self._index = str(index)

        if username != None and password != None:
            basicAuth = base64.encodestring('%s:%s' % (username, password))
            self._authHeader = "Basic " + basicAuth.strip()
        else:
            self._authHeader = None

        if url == None:
            url = self._baseURL + '/' + self._index + '/_search'

        self._url = url
        self._contextFactory = WebClientContextFactory()
        from twisted.internet import reactor
        self._agent = Agent(reactor, self._contextFactory)

    def deleteIndex(self):
        d = defer.Deferred()
        from twisted.internet import reactor
        reactor.callLater(0, self._deleteIndex, d)
        return d

    def reindex(self, filter=None, **ka):
        d = defer.Deferred()
        from twisted.internet import reactor
        reactor.callLater(0, self._reindex, d, filter, **ka)
        return d

    def createIndex(self, filter=None, **ka):
        d = defer.Deferred()
        from twisted.internet import reactor
        reactor.callLater(0, self._createIndex, d, filter, **ka)
        return d

    @defer.inlineCallbacks
    def _deleteIndex(self, d):
        headers = None
        if self._authHeader:
            headers = {"Authorization": [self._authHeader]}

        try:
            response = yield self._agent.request(
                'DELETE',
                self._baseURL + "/" + (self._index) + "/",
                Headers(headers))

            d1 = defer.Deferred()
            response.deliverBody(JSONProtocol(d1, response.length))
            obj1 = yield d1

            response = yield self._agent.request(
                'DELETE',
                self._baseURL + "/_river/" + str(self._index) + "/",
                Headers(headers))

            d1 = defer.Deferred()
            response.deliverBody(JSONProtocol(d1, response.length))
            obj2 = yield d1

            d.callback((obj1, obj2))
            return
        except (Exception, Failure)  as e:
            d.errback(UnknownError(e))
            return
        except:
            d.errback(UnknownError())
            return

    @defer.inlineCallbacks
    def _reindex(self, d, filter=None, **ka):
        headers = None
        if self._authHeader:
            headers = {"Authorization": [self._authHeader]}

        try:
            response = yield self._agent.request(
                'DELETE',
                self._baseURL + "/" + (self._index) + "/",
                Headers(headers))

            d1 = defer.Deferred()
            response.deliverBody(JSONProtocol(d1, response.length))
            obj1 = yield d1

            response = yield self._agent.request(
                'DELETE',
                self._baseURL + "/_river/" + (self._index) + "/",
                Headers(headers))

            d1 = defer.Deferred()
            response.deliverBody(JSONProtocol(d1, response.length))
            obj2 = yield d1

            # ignore obj1 and obj2
        except (Exception, Failure)  as e:
            d.errback(UnknownError(e))
            return
        except:
            d.errback(UnknownError())
            return

        from twisted.internet import reactor
        reactor.callLater(1, self._createIndex, d, filter, **ka) 

    @defer.inlineCallbacks
    def _createIndex(self, d, filter=None, templatePath=None):
        if filter is None:
            d.errback("No filter selected")
            return

        import wallaby.backends.couchdb as couchDB
        db = couchDB.Database.getDatabase()
        user, password = db.credentials()

        headers = None
        if self._authHeader:
            headers = {"Authorization": [self._authHeader]}

        if templatePath != None and os.path.exists(os.path.join(templatePath, self._index + ".json")): 
            f = open(os.path.join(templatePath, self._index + ".json"))
            jsonIndex = f.read()
            jsonIndex = jsonIndex.replace('$dbname$', db.name())
            f.close()
            body = DataProducer(jsonIndex)

            try:
                response = yield self._agent.request(
                    'PUT',
                    self._baseURL + "/" + (self._index),
                    Headers(headers),
                    body)

                d1 = defer.Deferred()
                response.deliverBody(JSONProtocol(d1, response.length))
                yield d1
            except (Exception, Failure)  as e:
                d.errback(UnknownError(e))
                return
            except:
                d.errback(UnknownError())
                return

        if user != None and password != None:
            request = {
                "type":"couchdb",
                "couchdb" : {
                    "host" : "localhost",
                    "port" : 5984,
                    "user": user,
                    "password": password,
                    "db" : db.name(),
                    "filter" : filter,
                },
                "index" : {
                    "index" : self._index
                }
            }
        else:
            request = {
                "type":"couchdb",
                "couchdb" : {
                    "host" : "localhost",
                    "port" : 5984,
                    "db" : db.name(),
                    "filter" : filter,
                },
                "index" : {
                    "index" : self._index
                }
            }

        jsonRequest = json.dumps(request)
        body = DataProducer(jsonRequest)

        try:
            response = yield self._agent.request(
                'PUT',
                self._baseURL + "/_river/" + (self._index) + "/_meta",
                Headers(headers),
                body)

            # print "GET", self._url, headers
            response.deliverBody(JSONProtocol(d, response.length))
        except (Exception, Failure)  as e:
            d.errback(UnknownError(e))
        except:
            d.errback(UnknownError())

    def doQuery(self, request):
        jsonRequest = json.dumps(request)
        body = DataProducer(jsonRequest)

        d = defer.Deferred()
        from twisted.internet import reactor
        reactor.callLater(0, self._doQuery, body, d)
        return d

    @defer.inlineCallbacks
    def _doQuery(self, body, d):
        headers = None
        if self._authHeader:
            headers = {"Authorization": [self._authHeader]}

        try:
            response = yield self._agent.request(
                'GET',
                str(self._url),
                Headers(headers),
                body)

            # print "GET", self._url, headers
            response.deliverBody(JSONProtocol(d, response.length))
        except (ConnectionRefusedError,DNSLookupError,ConnectionLost) as e:
            from twisted.internet import reactor
            reactor.callLater(1, self._doQuery, body, d) #retry in one second
        except (Exception, Failure)  as e:
            d.errback(UnknownError(e))
        except:
            d.errback(UnknownError())

    def stringQuery(self, term, defaultField=None, onlyIDs=True, sort=None, desc=False):
        d = defer.Deferred()

        if desc == None: desc = False

        from twisted.internet import reactor
        reactor.callLater(0, self._stringQuery, defaultField, term, onlyIDs, sort, desc, d)

        return d

    @defer.inlineCallbacks
    def _stringQuery(self, defaultField, term, onlyIDs, sort, desc, d):
        if re.match('^\w*$', term): term = u"*" + term + u"*"
        if defaultField != None:
            query = {'from': 0, 'size': 100, 'query_string':{'default_field': defaultField, 'query' :term}}
        else:
            query = {'from': 0, 'size': 100, 'query_string':{'query' :term}}

        # request = {'fields':[],'query':query}
        request = {'query':query}
        # , 'source': {"enabled": True} }

        if sort != None:
            if desc:
                request['sort'] = [ { sort : {"order" : "desc"} },{ "_id": {"order":"desc"} } ]
            else:
                request['sort'] = [ { sort : {"order" : "asc"} }, { "_id": {"order":"asc"}} ]

        # print "JSON: " + json.dumps(request)

        try:
            response = yield self.doQuery(request)
        except Exception as e:
            d.errback(e)
            return
        except:
            d.errback(UnknownError())
            return

        # print response

        if onlyIDs:
            ids = []
            if 'hits' in response and 'hits' in response['hits']:
                for hit in response['hits']['hits']:
                    if '_id' in hit:
                        ids.append(hit['_id'])
            else:
                d.errback(UnknownError(response))
                return

            d.callback(ids)
        else:
            values = []

            if 'hits' in response and 'hits' in response['hits']:
                for hit in response['hits']['hits']:
                    values.append(hit)
            else:
                d.errback(UnknownError(response))
                return

            # print values
            d.callback(values)
