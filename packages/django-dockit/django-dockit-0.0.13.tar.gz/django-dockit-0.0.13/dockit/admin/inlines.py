from documentadmin import SchemaAdmin

from django import forms
from django.contrib.admin.util import flatten_fieldsets
from django.utils.functional import curry

from dockit.forms.formsets import BaseInlineFormSet, inlinedocumentformset_factory

class InlineSchemaAdmin(SchemaAdmin):
    schema = None
    formset = BaseInlineFormSet
    extra = 1
    max_num = None
    template = None
    verbose_name = None
    verbose_name_plural = None
    can_delete = True

    def __init__(self, model, admin_site, schema=None, documentadmin=None, dotpath=None, **kwargs):
        super(InlineSchemaAdmin, self).__init__(model, admin_site, schema or self.schema, documentadmin)
        self.model = self.schema
        self.opts = self.schema._meta
        self.dotpath = dotpath
        if self.verbose_name is None:
            self.verbose_name = self.opts.verbose_name
        if self.verbose_name_plural is None:
            #admin display hack, this or I copy the whole template
            field_name = self.dotpath
            if field_name.endswith('.*'):
                field_name = field_name[:-2]
            if '.' in field_name:
                field_name = field_name.rsplit('.',1)[-1]
            self.verbose_name_plural = field_name
        for key, value in kwargs.iteritems():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise TypeError("Unrecognized option: %s" % key)

    def _media(self):
        from django.conf import settings
        js = ['js/jquery.min.js', 'js/jquery.init.js', 'js/inlines.min.js']
        if self.prepopulated_fields:
            js.append('js/urlify.js')
            js.append('js/prepopulate.min.js')
        if self.filter_vertical or self.filter_horizontal:
            js.extend(['js/SelectBox.js' , 'js/SelectFilter2.js'])
        media = forms.Media(js=['%s%s' % (getattr(settings, 'ADMIN_MEDIA_PREFIX', 'admin'), url) for url in js])
        media.add_js(['%sadmin/js/primitivelist.js' % settings.STATIC_URL])
        media.add_css({'all': ['%sadmin/css/primitivelist.css' % settings.STATIC_URL]})
        return media
    media = property(_media)
    '''
    def formfield_for_field(self, *args, **kwargs):
        ret = super(InlineSchemaAdmin, self).formfield_for_field(*args, **kwargs)
        assert False
        return ret
    '''
    def get_formset(self, request, view, obj=None, **kwargs):
        """Returns a BaseInlineFormSet class for use in admin add/change views."""
        if self.declared_fieldsets:
            fields = flatten_fieldsets(self.declared_fieldsets)
        else:
            fields = None
        if self.exclude is None:
            exclude = []
        else:
            exclude = list(self.exclude)
        exclude.extend(kwargs.get("exclude", []))
        exclude.extend(self.get_readonly_fields(request, obj))
        # if exclude is an empty list we use None, since that's the actual
        # default
        exclude = exclude or None
        defaults = {
            "form": self.get_form_class(request, obj), #TODO this needs meta
            "formset": self.formset,
            "fields": fields,
            "exclude": exclude,
            "formfield_callback": curry(self.formfield_for_field, request=request, view=view), #view=None
            "extra": self.extra,
            "max_num": self.max_num,
            "can_delete": self.can_delete,
            "schema": self.schema,
        }
        defaults.update(kwargs)
        return inlinedocumentformset_factory(self.model, self.dotpath, **defaults)
    
    def get_excludes(self):
        return list(self.exclude)
    
    def formfield_for_jsonfield(self, prop, field, view, **kwargs):
        request = kwargs.pop('request', None)
        from fields import DotPathField
        field = DotPathField
        kwargs['dotpath'] = self.dotpath
        kwargs['params'] = request.GET.copy()
        if view.next_dotpath(): #???
            kwargs['required'] = False
        return field(**kwargs)

class StackedInline(InlineSchemaAdmin):
    template = 'admin/edit_inline/stacked.html'

class TabularInline(InlineSchemaAdmin):
    template = 'admin/edit_inline/tabular.html'

