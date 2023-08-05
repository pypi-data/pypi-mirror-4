from django import forms
from django.db import models
from django.core.urlresolvers import reverse
from django.contrib import admin

from avocado.concepts.admin import ConceptAdmin
from avocado.columns.models import Column, ColumnField

__all__ = ('ColumnAdmin',)

class ColumnFieldInline(admin.TabularInline):
    model = ColumnField


class ColumnAdmin(ConceptAdmin):
    inlines = (ColumnFieldInline,)
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'cols': 30, 'rows': 3}),
            'required': False}
    }

    def field_relations(self, obj):
        queryset = obj.fields.order_by('columnfield__order').only('id', 'name')
        urlize = lambda x: '<a href="%s">%s</a>' % (
            reverse('admin:avocado_field_change', args=(x.id,)),
            x.name
        )
        return '<br>'.join(map(urlize, queryset)) or None
    field_relations.short_description = 'Field Relations'
    field_relations.allow_tags = True


admin.site.register(Column, ColumnAdmin)
