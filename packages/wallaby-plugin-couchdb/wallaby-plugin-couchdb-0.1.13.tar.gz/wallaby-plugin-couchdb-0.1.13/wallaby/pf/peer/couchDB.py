# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *
from database import Database
from abstractQuery import AbstractQuery
import wallaby.backends.couchdb as couchdb
from wallaby.plugins.couchdb.document import CouchdbDocument
from wallaby.common.document import Document

class CouchDB(Database, AbstractQuery):

    Description = ("Provides access to CouchDB", '{"query":true,"createIfMissing":false}')
    Suggests = [
        "DocumentDatabase",
        "DocumentCache",
        "Elasticsearch"
    ]

    def __init__(self, room, url=None, databaseName=None, query=True, idQuery=False, createIfMissing=False):
        Peer.__init__(self, room)
        AbstractQuery.__init__(self)
        Database.__init__(self)

        self._doQuery = query
        self._createIfMissing = createIfMissing

        self._lastQuery = {}

        if query:
            AbstractQuery.__init__(self)

        self._viewDocs = {}

        if url != None and databaseName != None:
            self._database = couchdb.Database.getDatabase(url+'/'+databaseName, self._connectionStatusChanged)
        else:
            self._database = couchdb.Database.getDatabase(databaseName, self._connectionStatusChanged)

    def initialize(self):
        self._database.changes(self._dbChanged)

    def destroy(self, remove=False):
        Peer.destroy(self, remove)
        self._database.unchanges(self._dbChanged)
    
        for viewID in self._lastQuery.keys():
            self._database.unchanges(self._viewChanged, filter='_view', view=viewID)

    def _connectionStatusChanged(self, connectionStatus):
        if connectionStatus == couchdb.Database.CONNECTED:
            self._throw(Database.Out.ConnectionEstablished, _database._name)
        elif connectionStatus == couchdb.Database.DISCONNECTED:
            self._throw(Database.Out.ConnectionRefused, self._database._name)

    def _dbChanged(self, changes, viewID=None):
        if changes is None: return

        if 'id' in changes: 
            # if changes['id'] in self._viewDocs and 'deleted' in changes and changes['deleted']:
            # FIXME: Dup detection
            if changes['id'] in self._viewDocs:
                for viewID in self._viewDocs[changes['id']]:
                    self._viewChanged(changes, viewID=viewID, fromChanges=True)

            self._throw(Database.Out.DocumentChanged, (changes['id'], changes['changes'][-1]) )

    @defer.inlineCallbacks
    def _getDocument(self, pillow, documentID):
        if documentID:
            document = yield self._database.get(documentID)
            if document:
                self._throw(Database.Out.RequestedDocument, CouchdbDocument(data=document, database=self._database))
            else:
                if self._createIfMissing:
                    self._throw(Database.Out.RequestedDocument, CouchdbDocument(documentID=documentID, database=self._database))
                else: 
                    self._throw(Database.Out.DocumentNotFound, documentID)
        else:
            self._throw(Database.Out.DocumentNotFound, documentID)

    def save(self, document):
        if not document: return
        if isinstance(document, (list, tuple)):
            docs = []
            for d in document:
                docs.append(d._data)

            return self._database.save({"docs": docs})
        else:
            return self._database.save(document._data)

    @defer.inlineCallbacks
    def _setDocument(self, pillow, lst):
        document, oldDocument = lst 

        if not document: return

        if isinstance(document, (list, tuple)):
            docs = []
            for d in document:
                docs.append(d._data)

            try:
                yield self._database.save({'docs': docs})
                self._throw(Database.Out.DocumentSaved, document.documentID)

            except Exception as e:
                self._throw(Database.Out.DocumentNotSaved, (e, None))

        elif isinstance(document, (Document, CouchdbDocument)):
            newDoc = False
            if not '_rev' in document._data: newDoc = True

            try:
                yield self._database.save(document._data)

                if newDoc:
                    self._throw(Database.Out.DocumentCreated, document.documentID)
                else:
                    self._throw(Database.Out.DocumentSaved, document.documentID)

                for name in document._deletedAttachments:
                    yield self._database.delete_attachment(document._data, name)

                for name in document._changedAttachments:
                    yield self._database.put_attachment(document._data, name, document._attachmentData[name])
            except Exception as e:
                self._throw(Database.Out.DocumentNotSaved, (e, document.documentID))


    @defer.inlineCallbacks
    def _deleteDocument(self, pillow, document):
        try:
            yield self._database.delete(document._data)

            self._throw(Database.Out.DocumentDeleted, document.documentID)
        except Exception as e:
            self._throw(Database.Out.DocumentNotDeleted, (e, document.documentID))

    def _createDocument(self, pillow, param):
        if type(param) is dict:
            document = CouchdbDocument(data=param, database=self._database)
        else:
            document = CouchdbDocument(documentID=param, database=self._database)

        self._throw(Database.Out.NewDocument, document)
        return document

    def _createAndSaveDocument(self, pillow, param):
        document = self._createDocument(pillow, param)
        from twisted.internet import reactor
        reactor.callLater(0, self._setDocument, None, (document, None))

    @defer.inlineCallbacks
    def _updateQuery(self, d, query, getCount=False):
        if query is None: return
        postfix = query.get('postfix')

        view = query.get('view')
        if view == None:
            return

        if postfix != None:
            view = view + postfix

        import copy
        args = copy.deepcopy(query.get('args'))
        cnt  = None

        if args and 'group_level' in args: args['group_level'] = int(args['group_level'])

        if not args or not ('reduce' in args or 'group' in args):
            if not args: 
                args = {}

            args['reduce'] = False

        doCount = ('count' in args)
        if doCount: del args['count']

        if 'includeCount' in args:
            rows, cnt = yield self._database.view(name=view, **args)
        else:
            rows = yield self._database.view(name=view, **args)

        viewID = None
        import re
        m = re.search('_design/(.*?)/_view/(.*)', view)
        if m is not None:
            viewID = m.group(1) + "/" + m.group(2)
            # print "START CHANGES FOR", viewID
            self._database.changes(self._viewChanged, filter='_view', view=viewID)
            viewID = unicode("_view__" + viewID)
            self._lastQuery[viewID] = query

        if not getCount:
            d.callback((rows, -1))
            return

        if doCount:
            if 'limit' in args: del args['limit']
            if 'skip' in args: del args['skip']
            if 'group_level' in args: del args['group_level']
            if 'reduce' in args: del args['reduce']

            level = 0
            key = []
            if 'start_key' in args: key = args['start_key']
            if 'startkey' in args: key = args['startkey']

            if isinstance(key, list):
                level = len(key)-1

            if level < 0:
                level = 0

            cnt=0
            cntResult = yield self._database.view(name=view, group_level=level, **args)
            if len(cntResult) > 0:
                cnt = cntResult[0]['value']

        for row in rows:
            if 'id' in row: 
                if row['id'] not in self._viewDocs:
                    self._viewDocs[row['id']] = {}

                self._viewDocs[row['id']][viewID] = True

        d.callback((rows, cnt))

    def updateQuery(self, query, **ka):
        d = defer.Deferred()
        from twisted.internet import reactor
        reactor.callLater(0, self._updateQuery, d, query, **ka)
        return d

    def _viewChanged(self, changes, viewID=None, fromChanges=False):
        # print "VIEW CHANGED", viewID, fromChanges, viewID in self._lastQuery, changes
        if viewID in self._lastQuery:
            from twisted.internet import reactor
            reactor.callLater(0, self._query, None, self._lastQuery[viewID])

    @defer.inlineCallbacks
    def _query(self, pillow, query):
        if not self._doQuery:
            return

        rows, cnt = yield self.updateQuery(query, getCount=True)

        if not query.get('dataView') == True:
            ids = []
            for row in rows:
                # ignore our documents in views
                if 'id' in row and row['id'] in ('credentials', 'WallabyApp2'): continue
                ids.append(row['id'])

            from documentIDQueryResult import DocumentIDQueryResult
            self._throw(AbstractQuery.Out.Result, DocumentIDQueryResult(self, query, ids, self._roomName, count=cnt))
        else:
            values = []
            for row in rows:
                # ignore our documents in views
                if 'id' in row and row['id'] in ('credentials', 'WallabyApp2'): continue
                values.append(row)


            from valueQueryResult import ValueQueryResult
            self._throw(AbstractQuery.Out.Result, ValueQueryResult(self, query, values, self._roomName, count=cnt))
