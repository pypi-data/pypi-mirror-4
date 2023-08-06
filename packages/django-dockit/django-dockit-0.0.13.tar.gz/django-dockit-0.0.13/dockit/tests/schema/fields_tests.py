from dockit.schema import fields
from dockit.schema.common import DotPathList, DotPathSet, DotPathDict

from django.utils import unittest
from django.contrib.contenttypes.models import ContentType

import datetime
from decimal import Decimal

from common import SimpleSchema, SimpleDocument

class BaseFieldTestCase(unittest.TestCase):
    EXAMPLE_VALUES = []
    EXAMPLE_PRIMITIVE_VALUES = []
    EXAMPLE_PORTABLE_PRIMITIVE_VALUES = []
    NULL_VALUE = None
    field_class = fields.BaseField
    
    def get_example_values(self):
        return self.EXAMPLE_VALUES
    
    def get_example_primitive_values(self):
        return self.EXAMPLE_PRIMITIVE_VALUES
    
    def get_example_portable_primitive_values(self):
        return self.EXAMPLE_PORTABLE_PRIMITIVE_VALUES
    
    def get_field_kwargs(self):
        return {}
    
    def get_field(self, **kwargs):
        params = self.get_field_kwargs()
        params.update(kwargs)
        return self.field_class(**params)
    
    def compare_py_val_to_primitive(self, py_val, primitive):
        self.assertEqual(py_val, primitive)
    
    def compare_primitives(self, prim1, prim2):
        self.assertEqual(prim1, prim2)
    
    def compare_portable_primitives(self, prim1, prim2):
        return self.compare_primitives(prim1, prim2)
    
    def test_handles_null_value(self):
        field = self.get_field(null=True)
        val = field.to_python(None)
        self.assertEqual(val, self.NULL_VALUE)
    
    def test_to_python_to_primitive(self):
        field = self.get_field()
        
        for val in self.get_example_values():
            primitive = field.to_primitive(val)
            py_val = field.to_python(primitive)
            self.compare_py_val_to_primitive(py_val, val)
        
        for val in self.get_example_primitive_values():
            py_val = field.to_python(val)
            primitive = field.to_primitive(py_val)
            self.compare_primitives(val, primitive)
        
        for val in self.get_example_portable_primitive_values():
            py_val = field.normalize_portable_primitives(val)
            primitive = field.to_portable_primitive(py_val)
            self.compare_portable_primitives(val, primitive)
        
    def test_form_field(self):
        field = self.get_field()
        field.formfield()
    
    def test_get_choices(self):
        field = self.get_field()
        field.get_choices()
    
    def test_json_serializable(self):
        field = self.get_field()
        for val in self.get_example_values():
            primitive = field.to_primitive(val)
            #TODO attempt to serialize
    
    def test_traverse_dotpath(self):
        pass #TODO raise skipped test

class CharFieldTestCase(BaseFieldTestCase):
    EXAMPLE_VALUES = ["abc", u"def"] #TODO good unicode values
    EXAMPLE_PRIMITIVE_VALUES = EXAMPLE_VALUES
    EXAMPLE_PORTABLE_PRIMITIVE_VALUES = EXAMPLE_VALUES
    field_class = fields.CharField

class IntegerFieldTestCase(BaseFieldTestCase):
    EXAMPLE_VALUES = [1, 3243455]
    EXAMPLE_PRIMITIVE_VALUES = EXAMPLE_VALUES
    EXAMPLE_PORTABLE_PRIMITIVE_VALUES = EXAMPLE_VALUES
    field_class = fields.IntegerField

class BigIntegerFieldTestCase(BaseFieldTestCase):
    EXAMPLE_VALUES = [1, 3243455, 2**32+1]
    EXAMPLE_PRIMITIVE_VALUES = EXAMPLE_VALUES
    EXAMPLE_PORTABLE_PRIMITIVE_VALUES = EXAMPLE_VALUES
    field_class = fields.BigIntegerField

class BooleanFieldTestCase(BaseFieldTestCase):
    EXAMPLE_VALUES = [True, False]
    EXAMPLE_PRIMITIVE_VALUES = EXAMPLE_VALUES
    EXAMPLE_PORTABLE_PRIMITIVE_VALUES = EXAMPLE_VALUES
    field_class = fields.BooleanField

class DateFieldTestCase(BaseFieldTestCase):
    EXAMPLE_VALUES = [datetime.date(2001,1,1)]
    EXAMPLE_PRIMITIVE_VALUES = EXAMPLE_VALUES
    EXAMPLE_PORTABLE_PRIMITIVE_VALUES = EXAMPLE_VALUES
    field_class = fields.DateField

class DateTimeFieldTestCase(BaseFieldTestCase):
    EXAMPLE_VALUES = [datetime.datetime(2001,1,1)]
    EXAMPLE_PRIMITIVE_VALUES = EXAMPLE_VALUES
    EXAMPLE_PORTABLE_PRIMITIVE_VALUES = EXAMPLE_VALUES
    field_class = fields.DateTimeField

class DecimalFieldTestCase(BaseFieldTestCase):
    EXAMPLE_VALUES = [1, 2, Decimal('1.5')]
    EXAMPLE_PRIMITIVE_VALUES = EXAMPLE_VALUES
    EXAMPLE_PORTABLE_PRIMITIVE_VALUES = EXAMPLE_VALUES
    field_class = fields.DecimalField
    
    def compare_primitives(self, prim1, prim2):
        self.assertEqual(str(prim1), str(prim2))

class EmailFieldTestCase(BaseFieldTestCase):
    EXAMPLE_VALUES = ['z@z.com']
    EXAMPLE_PRIMITIVE_VALUES = EXAMPLE_VALUES
    EXAMPLE_PORTABLE_PRIMITIVE_VALUES = EXAMPLE_VALUES
    field_class = fields.EmailField

class IPAddressFieldTestCase(BaseFieldTestCase):
    EXAMPLE_VALUES = ['127.0.0.1']
    EXAMPLE_PRIMITIVE_VALUES = EXAMPLE_VALUES
    EXAMPLE_PORTABLE_PRIMITIVE_VALUES = EXAMPLE_VALUES
    field_class = fields.IPAddressField

class SlugFieldTestCase(BaseFieldTestCase):
    EXAMPLE_VALUES = ['slug']
    EXAMPLE_PRIMITIVE_VALUES = EXAMPLE_VALUES
    EXAMPLE_PORTABLE_PRIMITIVE_VALUES = EXAMPLE_VALUES
    field_class = fields.SlugField

class TimeFieldTestCase(BaseFieldTestCase):
    field_class = fields.TimeField

#begin complex field types

class SchemaTypeFieldTestCase(BaseFieldTestCase):
    field_class = fields.SchemaTypeField
    
    def get_field_kwargs(self):
        return {'schemas': dict()}

class SchemaFieldTestCase(BaseFieldTestCase):
    field_class = fields.SchemaField
    EXAMPLE_VALUES = [SimpleSchema(charfield='charmander')]
    EXAMPLE_PRIMITIVE_VALUES = [{'charfield':'charmander'}]
    NULL_VALUE = None
    
    def get_field_kwargs(self):
        return {'schema': SimpleSchema}

class TypedSchemaFieldTestCase(BaseFieldTestCase):
    field_class = fields.TypedSchemaField
    
    def get_field_kwargs(self):
        return {'schemas': dict()}

class ListFieldTestCase(BaseFieldTestCase):
    field_class = fields.ListField
    EXAMPLE_VALUES = [DotPathList([]), DotPathList(['a','b','c'])]
    EXAMPLE_PRIMITIVE_VALUES = [[], ['a','b','c']]
    NULL_VALUE = []
    
    def get_field_kwargs(self):
        return {'subfield': fields.CharField()}

class SetFieldTestCase(BaseFieldTestCase):
    field_class = fields.SetField
    EXAMPLE_VALUES = [DotPathSet([]), DotPathSet(['a','b','c'])]
    EXAMPLE_PRIMITIVE_VALUES = [[], ['a','b','c']]
    NULL_VALUE = set()
    
    def get_field_kwargs(self):
        return {'subfield': fields.CharField()}
    
    def compare_py_val_to_primitive(self, py_val, primitive):
        self.assertTrue(isinstance(py_val, DotPathSet))
        self.assertEqual(py_val, set(primitive))
    
    def compare_primitives(self, prim1, prim2):
        #order does not matter
        self.assertEqual(set(prim1), set(prim2))

class DictFieldTestCase(BaseFieldTestCase):
    field_class = fields.DictField
    EXAMPLE_VALUES = [DotPathDict({}), DotPathDict({'a':1})]
    EXAMPLE_PRIMITIVE_VALUES = [{}, {'a':1}]
    NULL_VALUE = dict()
    
    def get_field_kwargs(self):
        return {}

class ReferenceFieldTestCase(BaseFieldTestCase):
    field_class = fields.ReferenceField
    
    def get_field_kwargs(self):
        return {'document': SimpleDocument}

class DocumentSetFieldTestCase(BaseFieldTestCase):
    field_class = fields.DocumentSetField
    NULL_VALUE = set()
    
    def get_field_kwargs(self):
        return {'document': SimpleDocument}

class ModelReferenceFieldTestCase(BaseFieldTestCase):
    field_class = fields.ModelReferenceField
    
    def get_example_values(self):
        return [ContentType.objects.all()[0]]
    
    def get_example_primitive_values(self):
        return [ContentType.objects.all()[0].pk]
    
    def compare_py_val_to_primitive(self, py_val, primitive):
        self.assertTrue(isinstance(py_val, ContentType), "%s is not of type %s" % (type(py_val), ContentType))
        super(ModelReferenceFieldTestCase, self).compare_py_val_to_primitive(py_val, primitive)
    
    def get_field_kwargs(self):
        return {'model': ContentType}

class ModelSetFieldTestCase(BaseFieldTestCase):
    field_class = fields.ModelSetField
    NULL_VALUE = set()
    
    def get_example_values(self):
        return [set([ContentType.objects.all()[0]])]
    
    def get_example_primitive_values(self):
        return [[ContentType.objects.all()[0].pk]]
    
    def compare_py_val_to_primitive(self, py_val, primitive):
        if len(py_val):
            val = list(py_val)[0]
            self.assertTrue(isinstance(val, ContentType), "%s is not of type %s" % (type(val), ContentType))
        super(ModelSetFieldTestCase, self).compare_py_val_to_primitive(py_val, primitive)
    
    def get_field_kwargs(self):
        return {'model': ContentType}

