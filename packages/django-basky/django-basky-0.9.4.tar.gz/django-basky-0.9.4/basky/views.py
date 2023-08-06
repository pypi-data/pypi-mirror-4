# -*- coding: utf-8 -*-
import re
from copy import deepcopy
from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from basky import settings as basky_settings
from basky import ajax
from basky.models import BasketItem
from basky.config import BasketConfig, BasketRegistry

QUANTITY_RE = re.compile('quantity_[\w]{32}')


def remove(request, basketitem_pk):
    """experimental ajax view"""
    #
    #
    # ajax only
    if not request.is_ajax():
        return HttpResponseRedirect(reverse('basky:basket'))
    #
    #
    # get the basket
    basket_name = getattr(settings,
        'BASKY_SESSION_KEY_NAME',
        basky_settings.BASKY_SESSION_KEY_NAME)
    basket = request.session[basket_name]
    #
    #
    # get the basket item
    try:
        basketitem = BasketItem.objects.get(pk=basketitem_pk)
    except BasketItem.DoesNotExist:
        response = {
            'success': False,
            'error': 'basketitem does not exist'}
        return ajax.json_response(response)
    #
    #
    # now remove it from the basket
    basket.remove(basketitem)
    response = {'success': True}
    #
    #
    # return the response
    return ajax.json_response(response)


def update(request):
    # next
    url = request.POST.get('next') or reverse('basky:basket')
    # our basketitems
    basketitems = request.session['basket'].basketitem_set.all()
    # get the basket name
    basket_name = getattr(settings,
        'BASKY_SESSION_KEY_NAME',
        basky_settings.BASKY_SESSION_KEY_NAME)
    basket = request.session[basket_name]
    if request.POST:
        for key, quantity in request.POST.items():
            if QUANTITY_RE.match(key):
                # turn quantity into an int
                try:
                    quantity = int(quantity)
                except ValueError:
                    continue
                hash = key.replace('quantity_', '')
                items = basketitems.filter(hash=hash)
                try:
                    # get the first basketitem
                    basketitem = items[0]
                    # now update the quantity if > 0
                    if quantity > 0:
                        basket.add(
                            basketitem.content_object,
                            quantity=quantity,
                            append=False,
                            request=request,
                            options=basketitem.options.all())
                    else:
                        basket.remove(basketitem)
                except IndexError:
                    pass
        # removes
        for pk in request.POST.getlist('remove'):
            try:
                basketitem = basket.basketitem_set.get(pk=pk)
                basket.remove(basketitem)
            except BasketItem.DoesNotExist:
                pass
        #
        # add some feedback
        messages.success(
            request,
            'Your basket has been updated')
    return HttpResponseRedirect(url)


def basket(request, **kwargs):
    # get the template
    template_name = kwargs.get('template_name', 'basky/basket.html')
    if request.method == 'POST':
        # get the instance for the form
        try:
            contenttype_pk = request.POST['contenttype_pk']
            object_pk = request.POST['object_pk']
            contenttype = ContentType.objects.get(pk=contenttype_pk)
            instance = contenttype.get_object_for_this_type(pk=object_pk)
            config = BasketRegistry.get(instance)
        except Exception, e:
            raise Http404('contenttype_pk/object_id in post are incorrect')
        # now get the form for the instance
        form = config.form(request.POST, instance=instance)
        # now process as normal
        if form.is_valid():
            item = form.save()
            # get the basket name
            basket_name = getattr(settings,
                'BASKY_SESSION_KEY_NAME',
                basky_settings.BASKY_SESSION_KEY_NAME)
            # now add it to the basket
            basket = request.session[basket_name]
            # prep the options if the form has an options method
            try:
                options = form.options()
            except AttributeError:
                options = None
            # now process 
            basketitem = basket.add(
                item,
                quantity=form.cleaned_data['quantity'],
                request=request,
                options=options)
            # wrap up
            if basketitem:
                messages.success(request, 'Basket Updated')
            url = kwargs.get('next') or \
                    request.POST.get('next') or \
                    reverse('basky:basket')
            return HttpResponseRedirect(url)

    return render_to_response(template_name, {},
        context_instance=RequestContext(request))
