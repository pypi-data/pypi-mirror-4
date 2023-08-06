# -*- coding: utf-8 -*-
from django.dispatch import Signal

"""sent when a request for a products total is requested"""
request_total_for_product = Signal(providing_args=['item'])

"""Sent when a product is removed from basket
basket item is the item that was added"""
pre_remove_from_basket = Signal(providing_args=['basketitem'])
post_remove_from_basket = Signal(providing_args=['basketitem'])

"""sent when a product is added to the basket
basket item is the item that was removed.
    
    .. Note:: that pre_add_to_basket passes the item and quantity and not the 
    basketitem because at the time of sending, it has not yet been
    incorporated into a basketitem
    
receivers can return a dict with {
        'item' : modified_item,
        'quantity' : modified_quantity
}
"""
pre_add_to_basket = Signal(providing_args=['item', 'quantity'])
post_add_to_basket = Signal(providing_args=['basketitem'])

"""Sent when the basket is either now not empty, or now empty, basketitem
is the item that was added/removed"""
basket_is_now_not_empty = Signal()
basket_is_now_empty = Signal()