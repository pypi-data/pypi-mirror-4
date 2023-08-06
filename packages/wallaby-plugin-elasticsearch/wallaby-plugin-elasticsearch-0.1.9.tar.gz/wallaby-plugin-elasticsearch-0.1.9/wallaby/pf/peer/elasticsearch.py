# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from wallaby.pf.peer.peer import *
from wallaby.pf.peer.database import *
from wallaby.pf.peer.abstractQuery import *
from wallaby.pf.peer.documentIDQueryResult import *
from wallaby.pf.peer.valueQueryResult import *
from wallaby.common.queryDocument import *
from twisted.python.failure import Failure
import wallaby.FX as FX
from twisted.internet import defer
import socket, re, errno
from wallaby.backends.elasticsearch import *

class Elasticsearch(Peer, AbstractQuery):
    Description = ("Provides access to Elasticsearch", '{"index":"default", "idQuery":false, "filter":null}')

    Reindex = Pillow.In
    DeleteIndex = Pillow.In

    def __init__(self, room, url=None, index='default', idQuery=False, filter=None):
        Peer.__init__(self, room)
        AbstractQuery.__init__(self)

        self._roomName = room
        self._idQuery = idQuery
        self._url = url
        self._filter = filter
        self._index = index

        self._catch(Elasticsearch.In.Reindex, self._reindex)
        self._catch(Elasticsearch.In.DeleteIndex, self._deleteIndex)

    @defer.inlineCallbacks
    def _reindex(self, pillow, feathers):
        if self._index == None:
            return 

        if self._url == None:
            searcher = Connection.getConnectionForIndex(self._index)
        else:
            searcher = Connection.getConnection(self._url, self._index)

        try:
            import os.path
            yield searcher.reindex(filter=self._filter, templatePath=os.path.join(FX.appPath, "es"))
        except (Exception, Failure) as e:
            print "Exception while reindexing:", str(e)

    @defer.inlineCallbacks
    def _deleteIndex(self, pillow, feathers):
        if self._index == None:
            return 

        if self._url == None:
            searcher = Connection.getConnectionForIndex(self._index)
        else:
            searcher = Connection.getConnection(self._url, self._index)

        try:
            yield searcher.deleteIndex()
        except (Exception, Failure) as e:
            print "Exception while deleting index:", str(e)

    @defer.inlineCallbacks
    def _query(self, pillow, doc):
        if doc is None: return

        if doc.get("args") != None:
            from twisted.internet import reactor
            reactor.callLater(0, self._oldStyleQuery, pillow, doc)
            return

        if self._url == None:
            searcher = Connection.getConnectionForIndex(self._index)
        else:
            searcher = Connection.getConnection(self._url, self._index)

        query = doc._data
        if "_id" in query: del query["_id"]
        if "_rev" in query: del query["_rev"]

        # import json
        # print json.dumps(query)

        try:
            response = yield searcher.doQuery(query)
            values = []

            if 'hits' in response and 'hits' in response['hits']:
                values = response['hits']['hits']
            else:
                print "Error in search query"
                print doc._data
                print response

                if re.search("IndexMissingException", response.get('error', '')):
                    yield searcher.createIndex(filter=self._filter, templatePath=os.path.join(FX.appPath, "es"))
                    from twisted.internet import reactor
                    reactor.callLater(2, self._query, pillow, doc)
                    return
 
            self._throw(AbstractQuery.Out.Result, ValueQueryResult(None, doc, values, self._roomName))

        except (Exception, Failure) as e:
            if re.search("IndexMissingException", str(e)):
                yield searcher.createIndex(filter=self._filter, templatePath=os.path.join(FX.appPath, "es"))
                from twisted.internet import reactor
                reactor.callLater(2, self._query, pillow, doc)
            else:
                print "Exception in query:", str(e)

        except:
            print "Unknown Error in _query"

    @defer.inlineCallbacks
    def _oldStyleQuery(self, pillow, doc):
        query = doc.get('query')
        if query == None: query = doc.get('args.query')
        if query == None: return

        sort  = doc.get('sort')
        desc  = doc.get('args.descending')
        index = doc.get('args.index')

        if sort == None:
            sort = doc.get('args.sort')

        if sort == '__default__':
            sort = doc.get('args.defaultSort')

        if index == None: index=str(self._index)
        else: index = str(index)

        if self._url == None:
            searcher = Connection.getConnectionForIndex(index)
        else:
            searcher = Connection.getConnection(self._url, index)

        try:
            if self._idQuery and not doc.get('dataView') == True:
                ids = yield searcher.stringQuery(query, sort=sort, desc=desc)
                self._throw(AbstractQuery.Out.Result, DocumentIDQueryResult(None, doc, ids, self._roomName))
            else:
                values = yield searcher.stringQuery(query, onlyIDs=False, sort=sort, desc=desc)
                self._throw(AbstractQuery.Out.Result, ValueQueryResult(None, doc, values, self._roomName))
        except (Exception, Failure) as e:
            if re.search("IndexMissingException", str(e)):
                yield searcher.createIndex(filter=self._filter, templatePath=os.path.join(FX.appPath, "es"))
                from twisted.internet import reactor
                reactor.callLater(2, self._oldStyleQuery, pillow, doc)
            else:
                print "Exception in query:", str(e)

        except:
            print "Unknown Error in _query"
