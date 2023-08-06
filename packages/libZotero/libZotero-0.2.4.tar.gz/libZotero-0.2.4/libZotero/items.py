import logging
from item import *
from zotero import getKey, responseIsError, updateObjectsFromWriteResponse


class Items(object):
    def __init__(self):
        self.itemObjects = {}
        self.itemsVersion = 0
        self.owningLibrary = None

    def __len__(self):
        return len(self.itemObjects)

    def __getitem__(self, itemKey):
        if itemKey in self.itemObjects:
            return self.itemObjects[itemKey]
        else:
            raise KeyError

    def __setitem__(self, itemKey, item):
        self.itemObjects[itemKey] = item

    def __delitem__(self, itemKey):
        del self.itemObjects[itemKey]

    def __iter__(self):
        return self.itemObjects.__iter__()

    def __reversed__(self):
        ritems = Items()
        ritems.itemObjects = self.itemObjects.reversed()
        return ritems

    def __contains__(self, itemKey):
        return itemKey in self.itemObjects

    def getItem(self, itemKey):
        if itemKey in self.itemObjects:
            return self.itemObjects[itemKey]
        else:
            return None

    def addItem(self, item):
        itemKey = item.itemKey
        self.itemObjects[itemKey] = item
        return item

    def addItemsFromFeed(self, feed):
        addedItems = []
        for entry in feed.entries:
            item = Item(entry)
            self.addItem(item)
            addedItems.append(item)
        return addedItems

    def replaceItem(self, item):
        itemKey = item.itemKey
        self.itemObjects[itemKey] = item

    def writeItem(self, item):
        written = self.writeItems([item])
        return written[0]

    def writeItems(self, items):
        writeItems = []

        for item in items:
            itemKey = item.get('itemKey')
            if itemKey == '':
                newItemKey = getKey()
                item.set('itemKey', newItemKey)
                item.set('itemVersion', 0)
            writeItems.append(item)

            #add separate note items if this item has any
            itemNotes = item.get('notes')
            if itemNotes and len(itemNotes) > 0:
                for note in itemNotes:
                    note.set('parentItem', item.get('itemKey'))
                    note.set('itemKey', getKey())
                    note.set('itemVersion', 0)
                    writeItems.append(note)

        aparams = {'target': 'items', 'content': 'json'}
        reqUrl = self.owningLibrary.apiRequestString(aparams)

        chunks = [writeItems[i:i + 50] for i in range(0, len(writeItems), 50)]
        for chunk in chunks:
            writeArray = []
            for item in chunk:
                writeArray.append(item.writeApiObject())
            requestData = json.dumps({'items': writeArray})

            writeResponse = self.owningLibrary._request(reqUrl, 'POST', requestData, {'Content-Type': 'application/json'})
            if responseIsError(writeResponse):
                logging.info('writeItems Error')
                logging.info(writeResponse.status_code)
                #entire request failed but we get no per-item write failure messages
                #so update all items with writeFailure manually
                for item in chunk:
                    item.writeFailure = {'code': writeResponse.status_code, 'message': writeResponse.text}
            else:
                updateObjectsFromWriteResponse(chunk, writeResponse)
        return writeItems

    def deleteItem(self, item):
        """Permanently delete an existing item."""
        aparams = {'target': 'item', 'itemKey': item.itemKey}
        reqUrl = self.owningLibrary.apiRequestString(aparams)
        response = self.owningLibrary_request(reqUrl, 'DELETE', None, {'If-Unmodified-Since-Version': item.get('itemVersion')})
        return response

    def deleteItems(self, items, version=None):
        """Permanently delete up to 50 existing items."""
        if len(items) > 50:
            raise "Cannot delete more than 50 items at once."
        itemKeys = []
        latestItemVersion = 0
        for item in items:
            itemKeys.append(item.get('itemKey'))
            v = item.get('itemVersion')
            if v > latestItemVersion:
                latestItemVersion = v

        if version == None:
            if self.itemsVersion != 0:
                version = self.itemsVersion
            else:
                version = latestItemVersion

        itemKeyString = ",".join(itemKeys)
        aparams = {'target': 'items', 'itemKey': itemKeyString}
        reqUrl = self.owningLibrary.apiRequestString(aparams)
        response = self.owningLibrary._request(reqUrl, 'DELETE', None, {'If-Unmodified-Since-Version': version})
        return response

    def trashItem(self, item):
        item.trashItem()
        return item.save()

    def trashItems(self, items):
        for item in items:
            item.trashItem()
        return self.writeItems(items)
