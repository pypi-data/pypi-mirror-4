# -*- coding: utf-8 -*-
from django import template
from django.contrib.contenttypes.models import ContentType
from basky.config import BasketRegistry
from basky.forms import BasketForm
from django.conf import settings

register = template.Library()


@register.inclusion_tag('basky/_basket.html')
def render_basket(basket):
    return {
        'basket': basket,
        'MEDIA_URL' : settings.MEDIA_URL
    }

@register.inclusion_tag('basky/_basket_form.html')
def basketform(instance):
    config = BasketRegistry.get(instance)
    form = config.form(instance=instance)
    return {
        'form': form
    }
