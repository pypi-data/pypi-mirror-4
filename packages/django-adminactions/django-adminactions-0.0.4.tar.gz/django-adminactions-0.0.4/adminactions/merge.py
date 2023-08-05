# -*- coding: utf-8 -*-
from django.contrib import messages
from django.contrib.admin import helpers
from django.forms import forms, modelform_factory
from django.shortcuts import render_to_response
from django.template import RequestContext

from django.utils.translation import gettext as _
from adminactions.forms import GenericActionForm


class MergeForm(GenericActionForm):
    action = forms.CharField(label='', required=True, initial='', widget=forms.HiddenInput())


def merge(modeladmin, request, queryset):
    """
    Merge two model instances. Move all foreign keys.

    """
#    if queryset.count() <> 2:
#        messages.error(request, _('Please select exactly 2 records'))
#        return

    first, second = queryset.all()

    # Allows to specified a custom Form in the ModelAdmin
    merge_form_class = getattr(modeladmin, 'merge_form', MergeForm)
    MForm = modelform_factory(modeladmin.model, form=merge_form_class)

    if 'apply' in request.POST:
        form = MForm(request.POST)
        if form.is_valid():
            pass
    else:
        initial = {'_selected_action': request.POST.getlist(helpers.ACTION_CHECKBOX_NAME),
                   'action': 'merge'}

        form = MForm(initial=initial)

    adminForm = helpers.AdminForm(form, modeladmin.get_fieldsets(request), {}, [], model_admin=modeladmin)
    tpl = 'adminactions/merge.html'
    ctx = {'adminform': adminForm,}
    return render_to_response(tpl, RequestContext(request, ctx))
