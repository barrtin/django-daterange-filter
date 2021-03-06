# -*- coding: utf-8 -*-


'''
Has the filter that allows to filter by a date range.

'''
from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AdminDateWidget
from django.db import models
from django.utils.translation import ugettext as _


class DateRangeForm(forms.Form):

    def __init__(self, request=None, *args, **kwargs):
        field_name = kwargs.pop('field_name')
        super(DateRangeForm, self).__init__(*args, **kwargs)

        self.fields['%s__gte' % field_name] = forms.DateField(
            label='', widget=AdminDateWidget(
                attrs={'placeholder': _('From date')}), localize=True,
            required=False)

        self.fields['%s__lte' % field_name] = forms.DateField(
            label='', widget=AdminDateWidget(
                attrs={'placeholder': _('To date')}), localize=True,
            required=False)

        for field in request.GET.keys():
            if field not in self.fields:
                self.fields[field] = forms.Field()
                self.fields[field].widget = forms.HiddenInput()
                self.fields[field].required = False


class DateRangeFilter(admin.filters.FieldListFilter):
    template = 'daterange_filter/filter.html'

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg_since = '%s__gte' % field_path
        self.lookup_kwarg_upto = '%s__lte' % field_path
        super(DateRangeFilter, self).__init__(
            field, request, params, model, model_admin, field_path)
        self.form = self.get_form(request)

    def choices(self, cl):
        return []

    def expected_parameters(self):
        return [self.lookup_kwarg_since, self.lookup_kwarg_upto]

    def get_form(self, request):
        return DateRangeForm(data=request.GET,
                            field_name=self.field_path,
                            request=request)

    def queryset(self, request, queryset):
        if self.form.is_valid():
            # get no null params
            filter_fields = self.lookup_kwarg_upto, self.lookup_kwarg_since
            filter_params = dict([key, val] for key, val in self.form.cleaned_data.items() if val and key in filter_fields)
            return queryset.filter(**filter_params)
        else:
            return queryset


# register the filter
admin.filters.FieldListFilter.register(
    lambda f: isinstance(f, models.DateField), DateRangeFilter)
