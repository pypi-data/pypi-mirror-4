from django.utils.encoding import smart_unicode, force_unicode
from django.utils.translation import ugettext_lazy as _
from django.utils.text import capfirst
from django.utils import formats
from django.core import validators
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models.fields import BLANK_CHOICE_DASH
from django import forms

from decimal import Decimal
import datetime
import copy

from dockit.schema.serializer import PRIMITIVE_PROCESSOR
from dockit.schema.exceptions import DotPathNotFound
from dockit.schema.common import DotPathList, DotPathDict, DotPathSet, UnSet
from dockit.forms.fields import HiddenSchemaField, HiddenListField, HiddenDictField, SchemaChoiceField, PrimitiveListField, SchemaMultipleChoiceField

class NOT_PROVIDED:
    pass

class BaseField(object):
    form_field_class = forms.CharField
    form_field_choices_class = forms.ChoiceField
    form_widget_class = None

    default_validators = [] # Default set of validators
    default_error_messages = {
        'invalid_choice': _(u'Value %r is not a valid choice.'),
        'null': _(u'This field cannot be null.'),
        'blank': _(u'This field cannot be blank.'),
        'unique': _(u'%(model_name)s with this %(field_label)s '
                    u'already exists.'),
    }

    creation_counter = 0
    auto_creation_counter = -1

    def __init__(self, verbose_name=None, name=None, blank=False, null=False,
                 default=NOT_PROVIDED, editable=True,
                 serialize=True, choices=None, help_text='',
                 validators=[],
                 db_index=False, unique=False,
                #db_index=False,  db_column=None, primary_key=False, max_length=None
                #db_tablespace=None,
                #unique_for_date=None, unique_for_month=None, unique_for_year=None,
                 error_messages=None, auto_created=False):
        self.verbose_name = verbose_name
        self.name = name
        self.blank = blank
        self.null = null
        self.default = default
        self.editable = editable
        self.serialize = serialize,
        self.choices = choices
        self.help_text = help_text
        self.validators = validators
        self.db_index = db_index

        self.validators = self.default_validators + validators

        messages = {}
        for c in reversed(self.__class__.__mro__):
            messages.update(getattr(c, 'default_error_messages', {}))
        messages.update(error_messages or {})
        self.error_messages = messages

        #TODO support the following:
        self.rel = None
        self.flatchoices = None
        self.unique = unique

        # Adjust the appropriate creation counter, and save our local copy.
        if auto_created:
            self.creation_counter = BaseField.auto_creation_counter
            BaseField.auto_creation_counter -= 1
        else:
            self.creation_counter = BaseField.creation_counter
            BaseField.creation_counter += 1

    def contribute_to_class(self, cls, name):
        self.name = name
        if not self.verbose_name:
            self.verbose_name = name.replace('_', ' ')
        cls._meta.fields[name] = self
        setattr(cls, name, self)

    def has_default(self):
        "Returns a boolean of whether this field has a default value."
        return self.default is not NOT_PROVIDED

    def get_default(self):
        "Returns the default value for this field."
        if self.has_default():
            if callable(self.default):
                return self.default()
            return force_unicode(self.default, strings_only=True)
        if not self.blank or self.null:
            return None
        return ""

    def get_choices(self, include_blank=True, blank_choice=BLANK_CHOICE_DASH):
        """Returns choices with a default blank choices included, for use
        as SelectField choices for this field."""
        first_choice = include_blank and blank_choice or []
        if self.choices:
            choices = self.choices
            if callable(choices):
                choices = choices()
            return first_choice + list(choices)
        return first_choice
        #rel_model = self.rel.to
        #if hasattr(self.rel, 'get_related_field'):
        #    lst = [(getattr(x, self.rel.get_related_field().attname), smart_unicode(x)) for x in rel_model._default_manager.complex_filter(self.rel.limit_choices_to)]
        #else:
        #lst = [(x._get_pk_val(), smart_unicode(x)) for x in rel_model._default_manager.complex_filter(self.rel.limit_choices_to)]
        #return first_choice + lst

    def get_choices_default(self):
        return self.get_choices()

    def to_primitive(self, val):
        """
        Takes a python object and returns an object that is [json] serializable
        """
        return val

    def to_portable_primitive(self, val):
        return self.to_primitive(val)

    def to_python(self, val, parent=None):
        return val

    def normalize_portable_primitives(self, val, parent=None):
        return val

    def get_form_field_class(self):
        if self.choices:
            return self.form_field_choices_class
        else:
            return self.form_field_class

    def formfield(self, **kwargs):
        "Returns a django.forms.Field instance for this database Field."
        default = self.get_form_field_class()
        form_class = kwargs.pop('form_class', default)
        defaults = self.formfield_kwargs(**kwargs)
        return form_class(**defaults)

    def formfield_kwargs(self, **kwargs):
        defaults = {'required': not self.blank,
                    'label': capfirst(self.verbose_name),
                    'help_text': self.help_text,
                    'widget':self.form_widget_class,}
        if self.has_default():
            defaults['initial'] = self.get_default()

        for key, value in defaults.items():
            if value is None:
                del defaults[key]

        if self.choices:
            # Fields with choices get special treatment.
            include_blank = self.blank or not (self.has_default() or 'initial' in kwargs)
            defaults['choices'] = self.get_choices(include_blank=include_blank)
            #defaults['coerce'] = self.to_python
            #if self.null:
            #    defaults['empty_value'] = None
            # Many of the subclass-specific formfield arguments (min_value,
            # max_value) don't apply for choice fields, so be sure to only pass
            # the values that TypedChoiceField will understand.
            for k in kwargs.keys():
                if k not in ('empty_value', 'choices', 'required',#'coerce',
                             'widget', 'label', 'initial', 'help_text',
                             'error_messages', 'show_hidden_initial'):
                    del kwargs[k]
        defaults.update(kwargs)
        return defaults

    def traverse_dot_path(self, traverser):
        traverser.end(field=self)

    def is_instance(self, value):
        return False

    def set_value(self, parent, attr, value):
        raise DotPathNotFound

    def __deepcopy__(self, memodict):
        obj = copy.copy(self)
        memodict[id(self)] = obj
        return obj

    def _get_val_from_obj(self, obj):
        if self.name in obj._python_data:
            return obj._python_data[self.name]
        if self.name in obj._primitive_data:
            raw_val = obj._primitive_data[self.name]
            val = self.to_python(raw_val, parent=obj)
            obj._python_data[self.name] = val
            return val
        val = self.get_default()
        if self.has_default():
            obj._python_data[self.name] = val
        return val

    def value_to_string(self, obj):
        val = self._get_val_from_obj(obj)
        return self.to_primitive(val)

    @property
    def attname(self):
        return self.name

    def run_validators(self, value):
        if value in validators.EMPTY_VALUES:
            return

        errors = []
        for v in self.validators:
            try:
                v(value)
            except ValidationError, e:
                if hasattr(e, 'code') and e.code in self.error_messages:
                    message = self.error_messages[e.code]
                    if e.params:
                        message = message % e.params
                    errors.append(message)
                else:
                    errors.extend(e.messages)
        if errors:
            raise ValidationError(errors)

    def validate(self, value, obj):
        """
        Validates value and throws ValidationError. Subclasses should override
        this to provide validation logic.
        """
        if not self.editable:
            # Skip validation for non-editable fields.
            return
        if self.choices and value:

            for option_key, option_value in self.choices:
                if isinstance(option_value, (list, tuple)):
                    # This is an optgroup, so look inside the group for
                    # options.
                    for optgroup_key, optgroup_value in option_value:
                        if value == optgroup_key:
                            return
                elif value == option_key:
                    return
            msg = self.error_messages['invalid_choice'] % value
            raise ValidationError(msg)

        if value is None and not self.null:
            raise ValidationError(self.error_messages['null'])

        if not self.blank and value in validators.EMPTY_VALUES:
            raise ValidationError(self.error_messages['blank'])

    def clean(self, value, obj):
        """
        The correct value is returned if no error is raised.
        """
        self.validate(value, obj)
        self.run_validators(value)
        return value

class BaseTypedField(BaseField):
    coerce_function = None

    def to_primitive(self, val):
        if isinstance(self.coerce_function, type) and isinstance(val, self.coerce_function):
            return val
        if val is None:
            return val
        return self.coerce_function(val)

    def is_instance(self, val):
        if isinstance(self.coerce_function, type) and isinstance(val, self.coerce_function):
            return True
        if val is None:
            return True
        return False

class CharField(BaseTypedField):
    coerce_function = unicode
    data_type = 'char'

class TextField(BaseTypedField):
    coerce_function = unicode
    form_widget_class = forms.Textarea
    data_type = 'text'

class IntegerField(BaseTypedField):
    coerce_function = int
    form_field_class = forms.IntegerField
    data_type = 'int'

class BigIntegerField(BaseTypedField):
    coerce_function = long
    form_field_class = forms.IntegerField
    data_type = 'long'

class BooleanField(BaseTypedField):
    coerce_function = bool
    form_field_class = forms.BooleanField
    data_type = 'bool'

    def __init__(self, *args, **kwargs):
        super(BooleanField, self).__init__(*args, **kwargs)
        self.blank = True

class DateField(BaseField):
    form_field_class = forms.DateField
    data_type = 'date'

    def __init__(self, *args, **kwargs):
        self.input_formats = kwargs.pop('input_formats', list())
        super(DateField, self).__init__(*args, **kwargs)

    def to_python(self, value, parent=None):
        """
        Validates that the input can be converted to a date. Returns a Python
        datetime.date object.
        """
        if value is None:
            return None
        if isinstance(value, datetime.datetime):
            return value.date()
        if isinstance(value, datetime.date):
            return value
        for format in self.input_formats or formats.get_format('DATE_INPUT_FORMATS'):
            try:
                return datetime.datetime.strptime(value, format).date()
            except ValueError:
                continue
        return datetime.datetime.strptime(value).date()

class DateTimeField(BaseField):
    form_field_class = forms.DateTimeField
    data_type = 'datetime'

    def __init__(self, *args, **kwargs):
        self.input_formats = kwargs.pop('input_formats', list())
        super(DateTimeField, self).__init__(*args, **kwargs)

    def to_python(self, value, parent=None):
        """
        Validates that the input can be converted to a date. Returns a Python
        datetime.date object.
        """
        if value is None:
            return None
        if isinstance(value, datetime.datetime):
            return value
        if isinstance(value, datetime.date):
            return value
        for format in self.input_formats or formats.get_format('DATE_INPUT_FORMATS'):
            try:
                return datetime.datetime.strptime(value, format)
            except ValueError:
                continue
        return datetime.datetime.strptime(value)

class DecimalField(BaseField):
    form_field_class = forms.DecimalField
    data_type = 'decimal'

    def __init__(self, *args, **kwargs):
        self.max_digits = kwargs.pop('max_digits', None)
        self.decimal_places = kwargs.pop('decimal_places', None)
        super(DecimalField, self).__init__(*args, **kwargs)

    def to_primitive(self, val):
        return str(val)

    def to_python(self, val, parent=None):
        if val is None:
            return None
        return Decimal(val)

class EmailField(CharField):
    form_field_class = forms.EmailField
    pass #TODO validate

#TODO filefield? this will be passed off to the backend

class FloatField(BaseTypedField):
    coerce_function = float
    form_field_class = forms.FloatField
    data_type = 'float'

#TODO imagefield

class IPAddressField(CharField):
    form_field_class = forms.IPAddressField
    #TODO validate

#class GenericIPAddressField(TextField):
#    form_field_class = forms.GenericIPAddressField
#    #TODO validate

#TODO NullBooleanField

class PositiveIntegerField(IntegerField):
    form_field_class = forms.IntegerField
    #TODO validate

#TODO PositiveSmallIntegerField

class SlugField(CharField):
    form_field_class = forms.SlugField

#TODO SmallIntegerField

class TimeField(BaseTypedField):
    coerce_function = datetime.time
    form_field_class = forms.TimeField
    data_type = 'time'

#TODO URLField
#TODO XMLField

class SchemaTypeField(CharField):
    form_widget_class = forms.HiddenInput

    def __init__(self, schemas, *args, **kwargs):
        self.schemas = schemas
        super(SchemaTypeField, self).__init__(*args, **kwargs)

    def get_choices(self, include_blank=True, blank_choice=BLANK_CHOICE_DASH):
        """Returns choices with a default blank choices included, for use
        as SelectField choices for this field."""
        first_choice = include_blank and blank_choice or []
        if self.schemas:
            return first_choice + list(zip(self.schemas.keys(), self.schemas.keys()))
            #TODO allow schema to have a display label, perhaps verbose name?
        return first_choice

    def get_schema_choices(self):
        return self.get_choices()

class SchemaField(BaseField):
    form_field_class = HiddenSchemaField

    def __init__(self, schema, *args, **kwargs):
        from dockit.schema import Schema
        assert issubclass(schema, Schema), '%s does not subclass Schema' % repr(schema)
        self.schema = schema
        super(SchemaField, self).__init__(*args, **kwargs)

    def to_primitive(self, val):
        return self.schema.to_primitive(val)

    def to_python(self, val, parent=None):
        if val is None:
            return None
        if not isinstance(val, dict):
            raise ValidationError('Invalid schema instance')
        return self.schema.to_python(val, parent)

    def to_portable_primitive(self, val):
        if val is None:
            return None
        if self.is_instance(val):
            return val.to_portable_primitive(val)
        assert isinstance(val, dict)
        return val

    def normalize_portable_primitives(self, val, parent=None):
        if val is not None and isinstance(val, dict):
            entry = self.to_python(val, parent)
            entry.normalize_portable_primitives()
            return self.to_primitive(entry)
        return val

    def is_instance(self, val):
        if val is None:
            return True
        return isinstance(val, self.schema)

    def get_schema_choices(self):
        field_name = self.schema._meta.typed_field
        return self.schema._meta.fields[field_name].schemas.items()

    def traverse_dot_path(self, traverser):
        if traverser.remaining_paths:
            name = traverser.next_part
            value = traverser.current_value
            next_value = field = None
            schema = self.schema

            if value:
                try:
                    next_value = value[name]
                except KeyError:
                    pass
                schema = type(value)

            if name in schema._meta.fields:
                field = schema._meta.fields[name]

            traverser.next(field=field, value=next_value)
        else:
            traverser.end(field=self)

    def set_value(self, parent, attr, value):
        if value is UnSet:
            del parent[attr]
        else:
            parent[attr] = value

class GenericSchemaField(BaseField): #meant to be sublcassed
    def __init__(self, field_name='_type', **kwargs):
        self.type_field_name = field_name
        super(GenericSchemaField, self).__init__(**kwargs)

    def lookup_schema(self, key):
        raise NotImplementedError

    def get_schema_type(self, val):
        return val._meta.schema_key

    def get_schema_choices(self):
        raise NotImplementedError

    def set_schema_type(self, val):
        val[self.type_field_name] = self.get_schema_type(val)

    def to_primitive(self, val):
        if hasattr(val, 'to_primitive'):
            self.set_schema_type(val)
            return val.to_primitive(val)
        return val

    def to_python(self, val, parent=None):
        if hasattr(val, 'to_python'):
            return val.to_python(val, parent)
        if not self.is_instance(val):
            key = val[self.type_field_name]
            schema_cls = self.lookup_schema(key)
            return schema_cls(_primitive_data=val)
        return val

    def is_instance(self, val):
        if val is None:
            return True
        from dockit.schema.schema import Schema
        return isinstance(val, Schema)

    def traverse_dot_path(self, traverser):
        #CONSIDER if there is a value then return an exacto schema field
        if traverser.remaining_paths:
            name = traverser.next_part
            value = traverser.current_value
            next_value = field = None

            if value:
                try:
                    next_value = value[name]
                except KeyError:
                    pass

                if hasattr(value, '_meta') and hasattr(value._meta, 'fields') and name in value._meta.fields:
                    field = value._meta.fields[name]

            traverser.next(field=field, value=next_value)
        else:
            if traverser.current_value:
                traverser.end(field=SchemaField(schema=type(traverser.current_value)))
            else:
                traverser.end(field=self)

    def set_value(self, parent, attr, value):
        if value is UnSet:
            del parent[attr]
        else:
            parent[attr] = value

class TypedSchemaField(GenericSchemaField):
    def __init__(self, schemas, field_name='_type', **kwargs):
        self.schemas = schemas
        super(TypedSchemaField, self).__init__(field_name, **kwargs)

    def lookup_schema(self, key):
        return self.schemas[key]

    def get_schema_type(self, val):
        return val._meta.schema_key

    def get_schema_choices(self):
        return self.schemas.items()

    #TODO what about a widget?

#TODO need a more comprehensive form field and widget solution for these
class ListField(BaseField):
    form_field_class = HiddenListField

    def __init__(self, subfield=None, *args, **kwargs):
        self.subfield = subfield
        kwargs.setdefault('default', list)
        super(ListField, self).__init__(*args, **kwargs)

    def get_form_field_class(self):
        if not hasattr(self.subfield, 'schema'):
            return PrimitiveListField
        else:
            return self.form_field_class

    def formfield_kwargs(self, **kwargs):
        kwargs = super(ListField, self).formfield_kwargs(**kwargs)
        if not hasattr(self.subfield, 'schema'):
            kwargs['subfield'] = self.subfield.formfield()
        return kwargs

    def to_primitive(self, val):
        if self.subfield:
            ret = list()
            if val is None:
                return ret
            for item in val:
                ret.append(self.subfield.to_primitive(item))
            #run data through the primitive processor
            return PRIMITIVE_PROCESSOR.to_primitive(ret)
        return PRIMITIVE_PROCESSOR.to_primitive(val)

    def to_portable_primitive(self, val):
        if self.subfield:
            ret = list()
            if val is None:
                return ret
            for item in val:
                ret.append(self.subfield.to_portable_primitive(item))
            #run data through the primitive processor
            return PRIMITIVE_PROCESSOR.to_primitive(ret)
        return PRIMITIVE_PROCESSOR.to_primitive(val)

    def to_python(self, val, parent=None):
        if self.subfield:
            ret = DotPathList()
            if val is None:
                return ret
            #TODO pass in parent
            for item in val:
                if not self.subfield.is_instance(item):
                    try:
                        item = self.subfield.to_python(item)
                    except ObjectDoesNotExist:
                        continue
                ret.append(item)
            #run data through the primitive processor
            return PRIMITIVE_PROCESSOR.to_python(ret)
        return PRIMITIVE_PROCESSOR.to_python(val)

    def normalize_portable_primitives(self, val, parent=None):
        ret = list()
        for entry in val:
            if self.subfield:
                ret.append(self.subfield.normalize_portable_primitive(entry))
            else:
                ret.append(entry)
        return ret

    def is_instance(self, val):
        if val is None:
            return True
        if not isinstance(val, DotPathList):
            return False
        if self.subfield:
            for item in val:
                if not self.subfield.is_instance(item):
                    return False
        return True

    def traverse_dot_path(self, traverser):
        if traverser.remaining_paths:
            new_value = None
            value = traverser.current_value
            name = traverser.next_part
            if value and name != '*':
                try:
                    new_value = value[int(name)]
                except ValueError:
                    raise DotPathNotFound(u"Invalid index given, must be an integer (%s)" % name)
                except IndexError:
                    pass
            elif value and name == '*':
                new_value = value #requested a list of values
            traverser.next(field=self.subfield, value=new_value)
        else:
            traverser.end(field=self)

    def set_value(self, parent, attr, value):
        index = int(attr)
        if value is UnSet:
            parent.pop(index)
        else:
            if self.subfield and not self.subfield.is_instance(value):
                value = self.subfield.to_python(value)
            if index == len(parent):
                parent.append(value)
            else:
                parent[index] = value

class SetField(ListField):
    form_field_choices_class = forms.MultipleChoiceField

    #returns a MultipleChoiceField if there is a set of choices
    def get_form_field_class(self):
        if self.choices:
            return self.form_field_choices_class
        return ListField.get_form_field_class(self)

    def formfield_kwargs(self, **kwargs):
        if self.choices:
            return BaseField.formfield_kwargs(self, **kwargs)
        else:
            return ListField.formfield_kwargs(self, **kwargs)

    def to_python(self, val, parent=None):
        if self.subfield:
            ret = DotPathSet()
            if val is None:
                return ret
            #TODO pass in parent
            for item in val:
                if not self.subfield.is_instance(item):
                    try:
                        item = self.subfield.to_python(item)
                    except ObjectDoesNotExist:
                        continue
                ret.add(item)
            #run data through the primitive processor
            return PRIMITIVE_PROCESSOR.to_python(ret)
        return PRIMITIVE_PROCESSOR.to_python(val)

    def is_instance(self, val):
        if val is None:
            return True
        if not isinstance(val, DotPathSet):
            return False
        if self.subfield:
            for item in val:
                if not self.subfield.is_instance(item):
                    return False
        return True

class DictField(BaseField):
    form_field_class = HiddenDictField

    def __init__(self, key_subfield=None, value_subfield=None, **kwargs):
        self.key_subfield = key_subfield
        self.value_subfield = value_subfield
        super(DictField, self).__init__(**kwargs)

    def to_primitive(self, val):
        ret = dict()
        if val is None:
            return ret
        for key, value in val.iteritems():
            if hasattr(value, 'to_primitive'):
                value = type(value).to_primitive(value)
            if hasattr(key, 'to_primitive'):
                key = type(key).to_primitive(key)
            ret[key] = value
        #TODO run data through the primitive processor
        ret = PRIMITIVE_PROCESSOR.to_primitive(ret)
        return ret

    def to_portable_primitive(self, val):
        ret = dict()
        if val is None:
            return ret
        for key, value in val.iteritems():
            if hasattr(value, 'to_portable_primitive'):
                value = type(value).to_portable_primitive(value)
            if hasattr(key, 'to_portable_primitive'):
                key = type(key).to_portable_primitive(key)
            ret[key] = value
        #TODO run data through the primitive processor
        ret = PRIMITIVE_PROCESSOR.to_primitive(ret)
        return ret

    def to_python(self, val, parent=None):
        ret = DotPathDict()
        if val is None:
            return ret
        for key, value in val.iteritems():
            if self.value_subfield:
                if not self.value_subfield.is_instance(value):
                    value = self.value_subfield.to_python(value)
            if self.key_subfield:
                if not self.key_subfield.is_instance(key):
                    key = self.key_subfield.to_python(key)
            ret[key] = value
        #TODO run data through the primitive processor
        ret = PRIMITIVE_PROCESSOR.to_python(ret)
        return ret

    def normalize_portable_primitives(self, val, parent=None):
        ret = dict()
        if val is None:
            return ret
        for key, value in val.iteritems():
            if self.value_subfield:
                value = self.value_subfield.normalize_portable_primitives(value)
            if self.key_subfield:
                key = self.key_subfield.normalize_portable_primitives(key)
            ret[key] = value
        return ret

    def is_instance(self, val):
        if val is None:
            return True
        if not isinstance(val, DotPathDict):
            return False
        if self.value_subfield:
            for item in val.itervalues():
                if not self.value_subfield.is_instance(item):
                    return False
        if self.key_subfield:
            for item in val.iterkeys():
                if not self.key_subfield.is_instance(item):
                    return False
        return True

    def traverse_dot_path(self, traverser):
        if traverser.remaining_paths:
            value = traverser.current_value
            name = traverser.next_part
            new_value = None
            if value and name != '*':
                try:
                    new_value = value[name]
                except KeyError:
                    pass
                if new_value and not hasattr(new_value, 'traverse_dot_path'):
                    from dockit.schema.common import GenericDotPathObject
                    new_value = GenericDotPathObject(new_value)
            traverser.next(field=self.value_subfield, value=new_value)
        else:
            traverser.end(field=self)

    def set_value(self, parent, attr, value):
        if value is UnSet:
            del parent[attr]
        else:
            if self.value_subfield and not self.value_subfield.is_instance(value):
                value = self.value_subfield.to_python(value)
            parent[attr] = value

class ReferenceField(BaseField):
    form_field_class = SchemaChoiceField
    data_type = 'char'

    def __init__(self, document, *args, **kwargs):
        if document == 'self':
            self.self_reference = True
            document = None
        else:
            self.self_reference = False
            assert hasattr(document, 'objects')
            assert hasattr(document, 'get_id')
        self.document = document
        super(ReferenceField, self).__init__(*args, **kwargs)

    @property
    def _meta(self):
        return self.document._meta

    def contribute_to_class(self, cls, name):
        super(ReferenceField, self).contribute_to_class(cls, name)
        if self.self_reference:
            self.document = cls

    def is_instance(self, val):
        if val is None:
            return True
        return isinstance(val, self.document)

    def to_primitive(self, val):
        if isinstance(val, basestring): #CONSIDER, should this happen?
            return val
        if val is None:
            return val
        return val.get_id()

    def to_portable_primitive(self, val):
        if isinstance(val, basestring): #CONSIDER, should this happen?
            return val
        if val is None:
            return val
        return val.natural_key

    def to_python(self, val, parent=None):
        if self.self_reference:
            if val is None:
                return val
            document = type(parent)
            if isinstance(val, document):
                return val
        else:
            if self.is_instance(val):
                return val
            document = self.document
        try:
            if isinstance(val, dict):
                return document.objects.get_by_natural_key(**val)
            return document.objects.get(pk=val)
        except ObjectDoesNotExist:
            if self.null:
                return None
            raise

    def normalize_portable_primitives(self, val, parent=None):
        if isinstance(val, dict):
            try:
                obj = self.to_python(val, parent)
            except ObjectDoesNotExist:
                return val #TODO should this be null instead?
            else:
                return obj.pk
        return val

    def formfield_kwargs(self, **kwargs):
        kwargs = BaseField.formfield_kwargs(self, **kwargs)
        kwargs.setdefault('queryset', self.document.objects.all())
        return kwargs

    def traverse_dot_path(self, traverser):
        if traverser.remaining_paths:
            name = traverser.next_part
            value = traverser.current_value
            next_value = field = None

            if value:
                try:
                    next_value = value[name]
                except KeyError:
                    pass
            if name in self.document._meta.fields:
                field = self.document._meta.fields[name]

            traverser.next(field=field, value=next_value)
        else:
            traverser.end(field=self)

    def set_value(self, parent, attr, value):
        parent[attr] = value

class DocumentSetField(SetField):
    form_field_choices_class = SchemaMultipleChoiceField

    def __init__(self, document, *args, **kwargs):
        #a set is never null, if it is passed in it is meant for our subfield
        subfield = ReferenceField(document, null=kwargs.pop('null', True))
        kwargs['subfield'] = subfield
        super(DocumentSetField, self).__init__(*args, **kwargs)
        #self.choices = True
        self.document = document
        self.queryset = document.objects.all()

    def get_choices(self, include_blank=True, blank_choice=BLANK_CHOICE_DASH):
        choices = list(include_blank and blank_choice or [])
        lst = [(x.pk, smart_unicode(x)) for x in self.queryset]
        return choices + lst

    def formfield_kwargs(self, **kwargs):
        kwargs = BaseField.formfield_kwargs(self, **kwargs)
        kwargs.setdefault('queryset', self.queryset)
        return kwargs

    def get_form_field_class(self):
        return self.form_field_choices_class

class ModelReferenceField(BaseField):
    form_field_class = forms.ModelChoiceField
    form_field_choices_class = forms.ModelChoiceField
    data_type = 'char'

    def __init__(self, model, *args, **kwargs):
        self.model = model
        super(ModelReferenceField, self).__init__(*args, **kwargs)

    def is_instance(self, val):
        if val is None:
            return True
        return isinstance(val, self.model)

    def to_primitive(self, val):
        if val is None:
            return None
        return val.pk

    def to_portable_primitive(self, val):
        if val is None:
            return None
        if hasattr(val, 'natural_key'):
            return val.natural_key()
        return val.pk

    def to_python(self, val, parent=None):
        if val is None:
            return None
        try:
            if isinstance(val, (tuple, list)):
                if hasattr(self.model.objects, 'get_by_natural_key'):
                    return self.model.objects.get_by_natural_key(*val)
            return self.model.objects.get(pk=val)
        except ObjectDoesNotExist:
            if self.null:
                return None
            raise

    def normalize_portable_primitives(self, val, parent=None):
        if isinstance(val, (tuple, list)):
            try:
                obj = self.to_python(val, parent)
            except ObjectDoesNotExist:
                return val #TODO should this be null instead?
            else:
                return obj.pk
        return val

    def formfield_kwargs(self, **kwargs):
        kwargs = BaseField.formfield_kwargs(self, **kwargs)
        kwargs.setdefault('queryset', self.model.objects)
        return kwargs

class ModelSetField(SetField):
    form_field_choices_class = forms.ModelMultipleChoiceField

    def __init__(self, model, *args, **kwargs):
        #a set is never null, if it is passed in it is meant for our subfield
        subfield = ModelReferenceField(model, null=kwargs.pop('null', True))
        kwargs['subfield'] = subfield
        super(ModelSetField, self).__init__(*args, **kwargs)
        #self.choices = True
        self.model = model
        self.queryset = model.objects.all()

    def get_form_field_class(self):
        return self.form_field_choices_class

    def formfield_kwargs(self, **kwargs):
        kwargs = BaseField.formfield_kwargs(self, **kwargs)
        kwargs.setdefault('queryset', self.model.objects)
        return kwargs

    def get_choices(self, include_blank=True, blank_choice=BLANK_CHOICE_DASH):
        choices = list(include_blank and blank_choice or [])
        lst = [(x._get_pk_val(), smart_unicode(x)) for x in self.queryset]
        return choices + lst

