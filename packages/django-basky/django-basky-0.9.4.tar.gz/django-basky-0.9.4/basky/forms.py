# -*- coding: utf-8 -*-
from django import forms
from django.contrib.contenttypes.models import ContentType
from models import BasketItem
from exceptions import BasketFormException


class BasketForm(forms.Form):

    contenttype_pk = forms.IntegerField(
        widget=forms.HiddenInput())
    object_pk = forms.IntegerField(
        widget=forms.HiddenInput())
    options = forms.CharField(
        widget=forms.HiddenInput(),
        required=False)
    quantity = forms.IntegerField(
        required=False)
    
    def __init__(self, *args, **kwargs):
        # check for args[0]...
        try:
            post = args[0]
        except IndexError:
            post = None
        # ... or kwargs['item']...
        try:
            instance = kwargs.pop('instance')
        except KeyError:
            instance = None
        # ... if neither present raise BasketFormException
        if not (post or instance):
            msg = 'post data or kwargs[\'instance\'] not present'
            raise BasketFormException(msg)
        # ..now that we know we can continue: get the quantity
        if instance:
            try:
                quantity = kwargs.pop('quantity', 1)
            except KeyError:
                pass
            # get the options
            #
            # TODO - turn this into a 34|32,98|35345 string
            try:
                options = kwargs.pop('options')
            except KeyError:
                options = None
            # workout content type
            ctype = ContentType.objects.get(
                        app_label=instance._meta.app_label,
                        model=instance._meta.object_name.lower())
            # now populate the initial
            initial =  {
                    'contenttype_pk': ctype.pk,
                    'object_pk': instance.pk,
                    'quantity': quantity,
                    'options': options
                }
            # update the kwargs with our initial and let forms do the rest
            kwargs.update({'initial': initial})
            # call super.__init__
        super(BasketForm, self).__init__(*args, **kwargs)

    def save(self):
        ctype = ContentType.objects.get(
                pk=self.cleaned_data['contenttype_pk'])
        item = ctype.model_class().objects.get(
                pk=self.cleaned_data['object_pk'])
        return item
