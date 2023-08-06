from django.utils import simplejson
from django.core.serializers.json import DjangoJSONEncoder

from dockit.backends.base import BaseDocumentStorage, BaseIndexStorage
from dockit.backends.queryset import BaseDocumentQuery
from dockit.backends import get_index_router, dynamic_import

from dockit.backends.djangodocument.models import DocumentStore, RegisteredIndex, RegisteredIndexDocument
from dockit.backends.djangodocument.utils import db_table_exists

class DocumentQuery(BaseDocumentQuery):
    def __init__(self, query_index, queryset, backend=None):
        super(DocumentQuery, self).__init__(query_index, backend)
        self.queryset = queryset
        assert isinstance(self.backend, ModelIndexStorage), str(type(self.backend))
    
    def wrap(self, entry):
        data = simplejson.loads(entry.data)
        data['_pk'] = entry.pk
        return self.document.to_python(data)
    
    def delete(self):
        return self.queryset.delete()
    
    def get_from_filter_operations(self, filter_operations):
        queryset = self.queryset
        for op in filter_operations:
            indexer = self._get_indexer_for_operation(self.document, op)
            queryset = queryset.filter(indexer.filter())
        try:
            return self.wrap(queryset.get())
        except self.queryset.model.DoesNotExist:
            raise self.document.DoesNotExist(str(queryset.query))
    
    def values(self, *limit_to, **kwargs):
        queryset = self.queryset
        limit_to = set(limit_to)
        values_args = list()
        if 'pk' in limit_to:
            queryset = queryset.extra(select={'pk':'id'})
            values_args.append('pk')
        return queryset.values(*values_args)
    
    def __len__(self):
        return self.queryset.count()
    
    def __nonzero__(self):
        return bool(self.queryset)
    
    def __getitem__(self, val):
        if isinstance(val, slice):
            results = list()
            for entry in self.queryset[val]:
                results.append(self.wrap(entry))
            return results
        else:
            return self.wrap(self.queryset[val])

class IndexedDocumentQuery(DocumentQuery):
    def wrap(self, entry):
        data = simplejson.loads(entry.data)
        data['_pk'] = entry.doc_id
        return self.document.to_python(data)
    
    def values(self, *limit_to, **kwargs):
        queryset = self.queryset
        limit_to = set(limit_to)
        values_args = list()
        for op in self.query_index.indexes:
            if limit_to and op.key not in limit_to:
                continue
            indexer = self._get_indexer_for_operation(self.document, op)
            response = indexer.values()
            if 'values' in response:
                values_args.extend(response['values'])
            if 'filters' in response:
                queryset = queryset.filter(**response['filters'])
            if 'extra' in response:
                queryset = queryset.extra(**response['extra'])
            if limit_to:
                limit_to.remove(op.key)
                if not limit_to:
                    break
        if 'pk' in limit_to:
            queryset = queryset.extra(select={'pk':'doc_id'})
            values_args.append('pk')
        return queryset.values(*values_args)

class ModelIndexStorage(BaseIndexStorage):
    thread_safe = True #we use the django orm which takes care of thread safety for us
    name = "djangomodel"
    _indexers = dict() #TODO this should be automatic
    
    def __init__(self, INDEX_TASKS='dockit.backends.djangodocument.tasks.IndexTasks'):
        self._tables_exist = False
        self.indexes = dict()
        self.pending_indexes = set()
        self.index_tasks = dynamic_import(INDEX_TASKS)()
        from dockit.backends.djangodocument import indexers
    
    def _register_pending_indexes(self):
        if not self.pending_indexes:
            return
        if not db_table_exists(RegisteredIndex._meta.db_table):
            return
        
        router = get_index_router()
        while self.pending_indexes:
            queryset = self.pending_indexes.pop()
            
            document = queryset.document
            collection = queryset.document._meta.collection
            key = queryset.global_hash()
            
            #only register if the queryset is still active
            if (collection in router.registered_querysets and
                key in router.registered_querysets[collection]):
                self.index_tasks.register_index(queryset)
    
    def register_index(self, query_index):
        if self._tables_exist or db_table_exists(RegisteredIndex._meta.db_table): #if the table doesn't exists then we are likely syncing the db
            self._tables_exist = True
            self.index_tasks.register_index(query_index)
            self._register_pending_indexes()
        else:
            self.pending_indexes.add(query_index)
    
    def destroy_index(self, query_index):
        if self._tables_exist or db_table_exists(RegisteredIndex._meta.db_table): #if the table doesn't exists then we are likely syncing the db
            self._tables_exist = True
            self.index_tasks.destroy_index(query_index)
        else:
            self.pending_indexes.remove(query_index)
    
    def reindex(self, query_index):
        self.index_tasks.reindex(query_index)
    
    def get_query(self, query_index):
        #lookup the appropriate query index
        self._register_pending_indexes()
        match = get_index_router().get_effective_queryset(query_index)
        query_index = match['queryset']
        document = query_index.document
        queryset = RegisteredIndexDocument.objects.filter(index__collection=document._meta.collection, index__query_hash=query_index.global_hash())
        for op in match['inclusions']:
            indexer = self._get_indexer_for_operation(document, op)
            queryset = queryset.filter(indexer.filter())
        for op in match['exclusions']:
            indexer = self._get_indexer_for_operation(document, op)
            queryset = queryset.exclude(indexer.filter())
        return IndexedDocumentQuery(query_index, queryset, backend=self)
    
    def on_save(self, doc_class, collection, doc_id, data):
        self._register_pending_indexes()
        self.index_tasks.on_save(collection, doc_id, data)
        #RegisteredIndex.objects.on_save(collection, doc_id, data)
    
    def on_delete(self, doc_class, collection, doc_id):
        self._register_pending_indexes()
        self.index_tasks.on_delete(collection, doc_id)
        #RegisteredIndex.objects.on_delete(collection, doc_id)

class ModelDocumentStorage(BaseDocumentStorage):
    thread_safe = True #we use the django orm which takes care of thread safety for us
    name = "djangomodel"
    
    def get_id_field_name(self):
        return '_pk'
    
    def save(self, doc_class, collection, data):
        doc_id = self.get_id(data)
        encoded_data = simplejson.dumps(data, cls=DjangoJSONEncoder)
        document = DocumentStore(collection=collection, data=encoded_data)
        if doc_id is not None:
            document.pk = doc_id
        #CONSIDER this does not look before we save
        document.save()
        data[self.get_id_field_name()] = document.pk
    
    def get(self, doc_class, collection, doc_id):
        try:
            document = DocumentStore.objects.get(collection=collection, pk=doc_id)
        except DocumentStore.DoesNotExist:
            raise doc_class.DoesNotExist
        data = simplejson.loads(document.data)
        data[self.get_id_field_name()] = document.pk
        return data
    
    def delete(self, doc_class, collection, doc_id):
        return DocumentStore.objects.filter(collection=collection, pk=doc_id).delete()
    
    def get_query(self, query_index):
        document = query_index.document
        queryset = DocumentStore.objects.filter(collection=query_index.document._meta.collection)
        for op in query_index.inclusions:
            assert op.key == 'pk'
            queryset = queryset.filter(pk=op.value)
        for op in query_index.exclusions:
            assert op.key == 'pk'
            queryset = queryset.exclude(pk=op.value)
        return DocumentQuery(query_index, queryset)

