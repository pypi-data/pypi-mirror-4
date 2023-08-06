from django.conf import settings
"""
define the name that will be used to access the basket from the session.
"""
BASKY_SESSION_KEY_NAME = getattr(
    settings,
    'BASKY_SESSION_KEY_NAME',
    'basket')
"""
Defines a maximum amount of items that a basket can hold. The default is
a resonably large number.
"""
# TODO - test this BASKY_MAX_ITEMS
# TODO - make default a decimal and test it
BASKY_MAX_ITEMS = getattr(
    settings,
    'BASKY_MAX_ITEMS',
    9999999)

"""
If set to True the basket will only allow a quantity of one on each item
and will not add another product to the basket if it already exists.
"""
# TODO - test this BASKY_SINGLE_QUANTITY
BASKY_SINGLE_QUANTITY = getattr(
    settings,
    'BASKY_SINGLE_QUANTITY', False)

"""Prefix for the cache"""
BASKY_CACHE_PREFIX = getattr(
    settings,
    'BASKY_CACHE_PREFIX',
    'BASKY')

BASKY_TEST_FIXTURES = getattr(
    settings,
    'BASKY_TEST_FIXTURES',
    [])

BASKY_TEST_MODELS = getattr(
    settings,
    'BASKY_TEST_MODELS',
    False)
