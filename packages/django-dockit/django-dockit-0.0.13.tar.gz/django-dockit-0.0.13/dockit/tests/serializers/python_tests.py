from dockit.core.serializers.python import Serializer, Deserializer

from django.utils import unittest
from django.contrib.contenttypes.models import ContentType

from dockit.tests.serializers.common import ParentDocument, ChildDocument, ChildSchema


class PythonSerializerTestCase(unittest.TestCase):
    def setUp(self):
        self.serializer = Serializer()
        #self.deserializer = Deserializer()

    def test_serialize(self):
        child = ChildDocument(charfield='bar')
        child.save()
        parent = ParentDocument(title='foo', subdocument=child, subschema=ChildSchema(ct=ContentType.objects.all()[0]))
        assert parent.natural_key
        assert '@natural_key' in parent._primitive_data
        data = parent.to_portable_primitive(parent)
        self.assertTrue(isinstance(data['subschema']['ct'], tuple), str(data))
        self.assertTrue(isinstance(data['subdocument'], dict), "Did not give a natural key: %s" % data['subdocument'])
        self.assertTrue('@natural_key' in data, str(data))
        result = self.serializer.serialize([child, parent])
        self.assertEqual(len(result), 2)
        entry = result[1]
        self.assertTrue('fields' in entry)
        self.assertEqual(len(entry['fields']), 3, str(entry))
        del data['@natural_key']
        del data['@natural_key_hash']
        self.assertEqual(entry['fields'], data)

    def test_deserialize(self):
        payload = [{'natural_key': {'charfield': 'bar'}, 'collection': ChildDocument._meta.collection, 'fields': {'charfield': u'bar'}},
                   {'natural_key': {'uuid': 'DEADBEEF'}, 'collection': ParentDocument._meta.collection, 'fields': {'subdocument': {'charfield': 'bar'}, 'title': u'foo'}}]
        objects = list(Deserializer(payload))
        self.assertEqual(len(objects), 2)
        obj = objects[1]
        #assert False, str(obj.object.to_primitive(obj.object))
        self.assertEqual(obj.object['title'], 'foo')

        saved_objects = list()
        for obj in objects:
            saved_obj = obj.save()
            self.assertTrue('@natural_key_hash' in saved_obj._primitive_data)
            self.assertTrue(saved_obj.pk)
            saved_objects.append(saved_obj)

        for obj in saved_objects:
            obj.normalize_portable_primitives()
            obj.save()

        #assert False, saved_objects[0]._primitive_data['@natural_key_hash'] #-5545305821442551595
        self.assertEqual(saved_objects[1].subdocument, saved_objects[0])

        subdoc = saved_objects[1]._primitive_data['subdocument']
        self.assertEqual(subdoc, saved_objects[0].pk)

