# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from twisted.internet import defer
from twisted.trial import unittest

class WallabyElasticsearchTest(unittest.TestCase):
    def setUp(self):
        self._dbName = "wallaby_es_test"
        self._docId  = "testdoc"

        self._designDoc = {
           "_id": "_design/wallaby_test",
           "language": "javascript",
           "filters": {
               "textDocs": "function(doc, req) { if(doc.text || doc.deleted) { return true; } return false;}"
           }
        }

        import wallaby.backends.couchdb as couch
        self._db = couch.Database.getDatabase(self._dbName)

        import wallaby.backends.elasticsearch as es
        self._es = es.Connection.getConnectionForIndex("wallaby_test")

    @defer.inlineCallbacks
    def test_00_create(self):
        try:
            info = yield self._db.info(keepOnTrying=False, returnOnError=True)
            if info != None: 
                yield self._db.destroy()
        except:
            pass

        res = yield self._db.create()
        self.assertTrue(res["ok"])

    @defer.inlineCallbacks
    def test_01_pushDesignDoc(self):
        res = yield self._db.save(self._designDoc)
        self.assertTrue(res["ok"])

    @defer.inlineCallbacks
    def test_02_createIndex(self):
        res = yield self._es.createIndex(filter="wallaby_test/textDocs")
        self.assertTrue(res["ok"])

    @defer.inlineCallbacks
    def test_03_createDoc(self):

        doc = {"_id": self._docId, "type": "typeA", "text": "Hello World!"}
        res = yield self._db.save(doc)

        self.assertTrue(res["ok"])
        self.assertTrue("rev" in res)

    @defer.inlineCallbacks
    def test_04_query(self):
        d = defer.Deferred()
        from twisted.internet import reactor
        reactor.callLater(2, d.callback, None)
        yield d

        res = yield self._es.doQuery({
            "query": {
                "query_string": {
                    "query": "*"
                } 
            }
        })
        self.assertEqual(res["hits"]["total"], 1)
        self.assertEqual(res["hits"]["hits"][0]["_source"]["text"], "Hello World!")

    @defer.inlineCallbacks
    def test_98_deleteIndex(self):
        res = yield self._es.deleteIndex()
        self.assertTrue(res[0]["ok"])
        self.assertTrue(res[1]["ok"])

    @defer.inlineCallbacks
    def test_99_destroy(self):
        res = yield self._db.destroy()
        self.assertTrue(res["ok"])
