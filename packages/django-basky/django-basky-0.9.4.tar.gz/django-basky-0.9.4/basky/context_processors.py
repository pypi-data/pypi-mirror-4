# -*- coding: utf-8 -*-
from django.conf import settings
from basky import settings as basky_settings


def basket(request):
    basket_name = getattr(
        settings,
        'BASKY_SESSION_KEY_NAME',
        basky_settings.BASKY_SESSION_KEY_NAME)
    try:
        basket = request.session[basket_name]
    except KeyError:
        basket = None
    return {basket_name: basket}