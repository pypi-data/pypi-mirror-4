from pipetools import maybe, select_first, X, where, foreach, pipe, flatten

from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.models import User
from django.db.models import AutoField, TextField, CharField, SlugField, DateField, DateTimeField, ManyToManyField, ForeignKey, BooleanField


def filter_existing(field_name, title_=None):

    class ListFilterExisting(SimpleListFilter):
        title = title_ or field_name.replace('_', ' ').capitalize()
        parameter_name = field_name

        def lookups(self, request, model_admin):
            model = model_admin.model
            field = model._meta.get_field(field_name)
            if isinstance(field, ForeignKey):
                related = field.related.parent_model
                return (related.objects
                    .filter(id__in=model.objects.values(field_name))
                    > foreach((X.pk, unicode))
                    | tuple)
            else:
                # ???
                return ()

        def queryset(self, request, queryset):
            value = self.value()
            return value and queryset.filter(**{field_name: value})

    return ListFilterExisting
