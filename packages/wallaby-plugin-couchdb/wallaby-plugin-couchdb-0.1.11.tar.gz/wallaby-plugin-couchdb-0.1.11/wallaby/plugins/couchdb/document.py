# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from uuid import uuid4
from wallaby.common.document import Document
from wallaby.common.pathHelper import PathHelper
from twisted.internet import defer
import copy

class CouchdbDocument(Document):
    def __init__(self, documentID=None, data=None, database=None):
        Document.__init__(self, documentID, data)
        self._database = database
        self._attachmentData = {}
        self._changedAttachments = []
        self._deletedAttachments = []
        self._getAttachmentDefers = {}
        self._conflicts = []

    def url(self):
        return self._database.url()+'/_utils/document.html?'+self._database.name()+'/'+self.documentID

    def resolve(self, mine=None, theirs=None):
        if not self.hasConflicts():
            return

        if mine == None and theirs == None:
            for c in self._conflicts:
                print "TRY TO DELETE", c
                self._database.delete(c)

        if mine != None:
            if self._database != None:
                for c in self._conflicts:
                    self._database.delete(c)


        elif theirs != None:
            if theirs < len(self._conflicts):
                c = self._conflicts[theirs]
                for k,v in c.items():
                    rev = self._data['_rev']
                    self._data = copy.deepcopy(c)
                    self._data['_rev'] = rev

                for c in self._conflicts:
                    self._database.delete(c)

    def hasConflicts(self):
        return self._data and '_conflicts' in self._data and len(self._data['_conflicts']) > 0

    def setConflicts(self, lst):
        self._conflicts = []
        for c in lst:
            if c != None and c[0] and c[1] != None: self._conflicts.append(c[1])

        return self._conflicts

    def loadConflicts(self):
        if not self.hasConflicts():
            d = defer.Deferred()
            d.callback(None)
            return d

        if len(self._conflicts) > 0:
            d = defer.Deferred()
            d.callback(self._conflicts)
            return d

        lst = []

        for rev in self._data['_conflicts']:
            d = self._database.get(self.documentID, rev=rev)
            lst.append(d)

        d = defer.DeferredList(lst)
        d.addCallback(self.setConflicts)
        return d

    def __deepcopy__(self, memo):
        doc = CouchdbDocument()
        doc.documentID = self.documentID
        doc.selection = self.selection
        doc._database = self._database
        doc._data = copy.deepcopy(self._data)
        doc._attachmentData = copy.deepcopy(self._attachmentData)
        doc._changedAttachments = copy.deepcopy(self._changedAttachments)
        doc._deletedAttachments = copy.deepcopy(self._deletedAttachments)
        return doc

    def clone(self):
        doc = CouchdbDocument()
        doc.documentID = self.documentID
        doc.selection = self.selection
        doc._database = self._database
        doc._data = copy.deepcopy(self._data)
        if '_attachments' in doc._data:
            del doc._data['_attachments']
        return doc

    def changes(self, doc):
        if doc and isinstance(doc, CouchdbDocument):
            changes = Set()

            for key in self._data:
                if key in doc._data:
                    if self._data[key] != doc._data[key]:
                        changes.append(key)
                else:
                    changes.append(key)

            for key in doc._data:
                if key in self._data:
                    if self._data[key] != doc._data[key]:
                        changes.append(key)
                else:
                    changes.append(key)

            return changes

    def rev(self):
        return self.get('_rev')

    def solveConflicts(self, document):
        if document and isinstance(document, CouchdbDocument):
            rev = document.get('_rev')
            if rev != None:
                self.set('_rev', rev) 

    def hasAttachment(self, name):
        if self._database and name not in self._deletedAttachments and '_attachments' in self._data and name in self._data['_attachments']:
            return True
        else:
            return False

    def deferredGetAttachment(self, name):
        get = False
        if name not in self._getAttachmentDefers:
            self._getAttachmentDefers[name] = [] 
            get = True

        from twisted.internet import reactor
        d = defer.Deferred()
        self._getAttachmentDefers[name].append(d)

        if get:
            reactor.callLater(0, self._getAttachment, name)

        return d

    @defer.inlineCallbacks
    def _getAttachment(self, name):
        from twisted.internet import reactor

        if self._database and name not in self._deletedAttachments and '_attachments' in self._data and name in self._data['_attachments'] and name not in self._attachmentData:
            self._attachmentData[name] = yield self._database.get_attachment(self._data, name)

        if name in self._attachmentData:
            for d in self._getAttachmentDefers[name]:
                reactor.callLater(0, d.callback, self._attachmentData[name])
        else:
            for d in self._getAttachmentDefers[name]:
                reactor.callLater(0, d.callback, None)

        del self._getAttachmentDefers[name]

    def setAttachment(self, name, attachment):
        self._attachmentData[name] = attachment
        self._changedAttachments.append(name)

    def deleteAttachment(self, name):
        if name in self._attachmentData:
            del self._attachmentData[name]
        self._deletedAttachments.append(name)
