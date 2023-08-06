from pymongo import Connection
try:
    from bson.objectid import ObjectId
except ImportError:
    from pymongo.objectid import ObjectId

from dockit.backends.base import BaseDocumentStorage, BaseIndexStorage
from dockit.backends.queryset import BaseDocumentQuery

class ValuesResultClass(dict):
    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            if key == 'pk':
                return dict.__getitem__(self, '_id')
            raise

class DocumentQuery(BaseDocumentQuery):
    def __init__(self, query_index, backend=None):
        super(DocumentQuery, self).__init__(query_index, backend)
        assert isinstance(self.backend, MongoIndexStorage), str(type(self.backend))
    
    def _build_params(self, include_indexes=False):
        params =  dict()
        for op in self.query_index.inclusions:
            indexer = self._get_indexer_for_operation(self.document, op)
            #i think this is horribly wrong
            params.update(indexer.filter())
        for op in self.query_index.exclusions:
            indexer = self._get_indexer_for_operation(self.document, op)
            params.update(indexer.filter())
        if include_indexes:
            for op in self.query_index.indexes:
                indexer = self._get_indexer_for_operation(self.document, op)
                params.update(indexer.filter())
        return params
    
    @property
    def collection(self):
        return self.document._meta.get_backend().get_collection(self.document._meta.collection)
    
    @property
    def queryset(self):
        params = self._build_params()
        if params:
            try:
                return self.collection.find(params)
            except TypeError:
                #why is it pymongo wants tuples for some and dictionaries for others?
                return self.collection.find(params.items())
        return self.collection.find()
    
    def wrap(self, entry):
        entry['_id'] = unicode(entry['_id'])
        return self.document.to_python(entry)
    
    def delete(self):
        params = self._build_params()
        if params:
            return self.collection.remove(params)
        return self.collection.remove()
    
    def get_from_filter_operations(self, filter_operations):
        params = self._build_params()
        for op in filter_operations:
            indexer = self._get_indexer_for_operation(self.document, op)
            params.update(indexer.filter())
        try:
            ret = self.collection.find_one(params)
        except TypeError:
            #why is it pymongo wants tuples for some and dictionaries for others?
            ret = self.collection.find_one(params.items())
        if ret is None:
            raise self.document.DoesNotExist
        return self.wrap(ret)
    
    def values(self, *limit_to, **kwargs):
        params = self._build_params(include_indexes=True)
        fields = limit_to or None
        if params:
            return self.collection.find(params, fields=fields, as_class=ValuesResultClass)
        return self.collection.find(fields=fields, as_class=ValuesResultClass)
    
    def __len__(self):
        return self.queryset.count()
    
    def __nonzero__(self):
        return bool(self.queryset)
    
    def __getitem__(self, val):
        if isinstance(val, slice):
            results = list()
            #TODO i don't think mongo supports passing a slice
            for entry in self.queryset[val]:
                results.append(self.wrap(entry))
            return results
        else:
            return self.wrap(self.queryset[val])

class MongoStorageMixin(object):
    def __init__(self, username=None, password=None, host=None, port=None, db=None, **kwargs):
        self.connection = Connection(kwargs.get('HOST', host), kwargs.get('PORT', port))
        self.db = self.connection[kwargs.get('DB', db)]
        if username:
            self.db.authenticate(kwargs.get('USER', username), kwargs.get('PASSWORD', password))
    
    def get_collection(self, collection):
        return self.db[collection]

class MongoIndexStorage(BaseIndexStorage, MongoStorageMixin):
    name = "mongodb"
    _indexers = dict() #TODO this should be automatic
    
    def register_index(self, query_index):
        query = self.get_query(query_index)
        params = query._build_params(include_indexes=True)
        for key in params.keys(): #TODO this is a hack
            params[key] = 1
        if params:
            collection = query_index.document._meta.collection
            try:
                self.get_collection(collection).ensure_index(params, background=True)
            except TypeError:
                self.get_collection(collection).ensure_index(params.items(), background=True)
    
    def destroy_index(self, query_index):
        pass #TODO
    
    def get_query(self, query_index):
        return DocumentQuery(query_index, backend=self)
    
    def on_save(self, doc_class, collection, data, doc_id):
        #CONSIDER supporting standalone mongo indexes
        pass #no operation needed
    
    def on_delete(self, doc_class, collection, doc_id):
        pass #no operation needed

class MongoDocumentStorage(BaseDocumentStorage, MongoStorageMixin):
    name = "mongodb"
    
    def save(self, doc_class, collection, data):
        id_field = self.get_id_field_name()
        if data.get(id_field, False) is None:
            del data[id_field]
        elif id_field in data:
            data[id_field] = ObjectId(data[id_field])
        self.get_collection(collection).save(data, safe=True)
        data[id_field] = unicode(data[id_field])
    
    def get(self, doc_class, collection, doc_id):
        data = self.get_collection(collection).find_one({'_id':ObjectId(doc_id)})
        if data is None:
            raise doc_class.DoesNotExist
        id_field = self.get_id_field_name()
        data[id_field] = unicode(data[id_field])
        return data
    
    def delete(self, doc_class, collection, doc_id):
        return self.get_collection(collection).remove(ObjectId(doc_id), safe=True)
    
    def get_id_field_name(self):
        return '_id'
    
    def get_query(self, query_index):
        return DocumentQuery(query_index)

