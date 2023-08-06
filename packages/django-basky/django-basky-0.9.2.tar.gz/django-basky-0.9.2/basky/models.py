# -*- coding: utf-8 -*-
import hashlib
from decimal import Decimal
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.cache import cache
from django.db import models
from django.utils.encoding import smart_str
from basky import settings as basky_settings
from basky.signals import pre_remove_from_basket,\
    post_remove_from_basket,\
    pre_add_to_basket,\
    post_add_to_basket,\
    basket_is_now_not_empty,\
    basket_is_now_empty


class Basket(models.Model):
    # django model gubbins
    session_key = models.CharField(
        max_length=32,
        db_index=True)
    created = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True)
    last_modified = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True)

    def __unicode__(self):
        return u'Basket: %s' % self.session_key

    def _get_ctype(self, item):
        """return a content type for a given item"""
        return ContentType.objects.get(
            app_label=item._meta.app_label,
            model=item._meta.object_name.lower())

    def _delete_cache(self):
        """delete all of the caches"""
        # delete the cache keys
        cache.delete(self._cache_key('total_items'))
        cache.delete(self._cache_key('total_price'))
    
    def _cache_key(self, suffix=None):
        """returns the cache_key for a given basket"""
        prefix = getattr(settings,
                'BASKY_CACHE_PREFIX',
                basky_settings.BASKY_CACHE_PREFIX)
        if suffix is None:
            key = '%s_%s' % (prefix, self.pk)
        else:
            key = '%s_%s_%s' % (prefix, self.pk, suffix)
        
        return key


    def total_price(self):
        """return the total price for the items in the basket"""
        # get the key
        #key = self._cache_key('total_price')
        #cached_total_price = cache.get(key)
        # if there is cache return that
        #if cached_total_price != None:
        #    return cached_total_price
        #
        # todo : use an aggregate to get this information
        price = Decimal("0.00")
        for basketitem in self.basketitem_set.all():
            price += basketitem.quantity * basketitem.price
        # 
        # set the value
        #cache.set(key, price)
        return price

    def total_items(self):
        """return the total count for the items in the basket"""
        # get the key
        #key = self._cache_key('total_items')
        #cached_total_items = cache.get(key)
        # if there is cache return that
        #if cached_total_items != None:
        #    return cached_total_items
        # no cache, so get total items and set cache
        total_items = 0
        for basketitem in self.basketitem_set.all():
            total_items += basketitem.quantity
        # set the value
        #cache.set(key, total_items)
        return total_items

    def add(self, item, **kwargs):
        """
        Add an item to as basket. If quantity is not present in the kwargs
        then a quantity of 1 is assumed. Any negative quantities are 
        transformedi nto positive values.
        """
        # if the item is None then the content object has been removed
        # so loop over all the basket items and remove any who have
        # none as a contentobject
        if item is None:
            for basketitem in self.basketitem_set.all():
                if basketitem.content_object == None:
                    self.remove(basketitem)
            return
        # if quiet was in kwargs we won't send signals
        silent = kwargs.get('silent', False)
        # default return values in case of no signals
        pre_add_return_values = []
        # if quantity wasn't in kwargs, then assume 1
        quantity = kwargs.get('quantity', 1)
        # if quantity was negative, make it positive

        if quantity <= 0:
            quantity = 1
        # make sure it's an int
        try:
            quantity = int(quantity)
        except Exception:
            raise Exception('Quantity supplied (%s) couldn\'t be cast to integer' % 
                        quantity)
        # if price wasn't in the kwargs, then assume the items price
        price = kwargs.get('price', item.total)
        # if description wasn't in the kwargs, then assume the items name
        description = kwargs.get('description', item.name)
        description2 = kwargs.get('description', None)
        # get the options
        options = kwargs.get('options', None)
        if options is not None:
            options_hash = BasketItem.get_options_hash(options)
        else:
            options_hash = None
        # is locked
        locked = kwargs.get('locked', False)
        # are we appending or updating
        append = kwargs.get('append', True)
        # do not add could be in the pre_add signal return, assume False
        do_not_add = False
        # we need the contenttype to do anything
        ctype = self._get_ctype(item)
        # empty?
        basket_empty = True if self.total_items() == 0 else False
        # send the pre_remove_from_basket signal if not in silent mode
        if not silent:
            #
            #
            # make sure that none of the arguments are in the kwargs
            try:
                del(kwargs['quantity'])
            except KeyError:
                pass
            try:
                del(kwargs['item'])
            except KeyError:
                pass
            pre_add_return_values = pre_add_to_basket.send(
                sender=Basket,
                instance=self,
                item=item,
                quantity=quantity,
                **kwargs)
        # now loop over the returns
        for return_value in pre_add_return_values:
            # look for an description
            try:
                description = return_value[1]['description']
            except (TypeError, IndexError, KeyError):
                pass
            # look for an description2
            try:
                description2 = return_value[1]['description2']
            except (TypeError, IndexError, KeyError):
                pass
            # look for an price
            try:
                price = return_value[1]['price']
            except (TypeError, IndexError, KeyError):
                pass
            # now look for a quantity
            try:
                quantity = return_value[1]['quantity']
            except (TypeError, IndexError, KeyError):
                pass
            # now look for a locked
            try:
                locked = return_value[1]['locked']
            except (TypeError, IndexError, KeyError):
                pass
            # now look for a do_not_add
            try:
                do_not_add = return_value[1]['do_not_add']
            except (TypeError, IndexError, KeyError):
                pass
        # if do not add then return False
        if do_not_add:
            return False
        # add to basket - iterate over the quantity
        try:
            basketitem = self.basketitem_set.get(
                description = description,
                description2 = description2,
                locked = locked,
                content_type = ctype,
                object_id = item.pk,
                options_hash = options_hash)
            # already have the item in - basket just update the quantity
            if not append:
                basketitem.quantity = quantity
            else:
                basketitem.quantity += quantity
            # delete options that are not the same as the options in item
            try:
                for opt in options:
                    if opt.pk not in [o.pk for o in basketitem.options.all()]:
                        opt.delete()
            except TypeError:
                # options was none - ignore
                pass
            # save it
            basketitem.save()
        except BasketItem.DoesNotExist:
            basketitem = BasketItem()
            basketitem.content_type = ctype
            basketitem.object_id = item.pk
            basketitem.quantity = quantity
            basketitem.price = price
            basketitem.description = description
            basketitem.description2 = description2
            basketitem.locked = locked
            basketitem.basket = self
            if options_hash:
                basketitem.options_hash = options_hash
            # save it
            basketitem.save()
            if options and options_hash:
                for option in options:
                    option.save()
                    basketitem.options.add(option)
        # delete the cache keys
        self._delete_cache()
        # if not in silent send the post add signal
        if not silent:
            post_add_to_basket.send(
                sender=Basket,
                instance=self,
                basketitem=basketitem)
            # if was empty but now not send the basket_is_now_not_empty
            if basket_empty and self.total_items() > 0:
                basket_is_now_not_empty.send(sender=Basket,instance=self)
        # return the basket line we just added
        return basketitem

    def remove(self, basketitem, *args, **kwargs):
        """
        Removes an basketitem to from a basket.
            returns a the item that was deleted
        """
        # if quiet was in kwargs we won't send signals
        silent = kwargs.get('silent', False)
        # pre return incase of no return 
        pre_remove_return_values = []
        # do not remove is False by default
        do_not_remove = False
        # empty
        basket_empty = True if self.total_items() == 0 else False
        # send the pre signal
        if not silent:
            pre_remove_return_values = pre_remove_from_basket.send(
                sender=Basket,
                instance=self,
                basketitem=basketitem)
        # now loop over the returns
        for return_value in pre_remove_return_values:
            # now look for a do_not_add
            try:
                do_not_remove = return_value[1]['do_not_remove']
            except (TypeError, IndexError, KeyError):
                pass
        if do_not_remove:
            return False
        try:
            item = basketitem.content_object
            basketitem.options.all().delete()
            basketitem.delete()
        except BasketItem.DoesNotExist:
            pass
        # delete the cache
        self._delete_cache()
        # send the post signal
        if not silent:
            post_remove_from_basket.send(
                sender=Basket,
                instance=self,
                basketitem=basketitem)
            # if was empty but now not send the basket_is_now_not_empty
            if not basket_empty and self.total_items() == 0:
                basket_is_now_empty.send(sender=Basket,instance=self)
        # return the item
        return item
    
    def empty(self):
        """Empties the basket and destroys the cache"""
        for basketitem in self.basketitem_set.all():
            for option in basketitem.options.all():
                option.delete()
            basketitem.delete()
            self._delete_cache()


class BasketItem(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=1)
    content_object = generic.GenericForeignKey(
        'content_type',
        'object_id')
    description = models.CharField(
        blank=True,
        null=True,
        max_length=255)
    description2 = models.CharField(
        blank=True,
        null=True,
        max_length=255)
    price = models.DecimalField(
        decimal_places=2,
        max_digits=10)
    #
    # TODO: maybe priced options are needed as a foreignkey field?
    #
    options = models.ManyToManyField('BasketItemOption',
            null=True,
            blank=True)
    locked = models.BooleanField(default=False)
    hash = models.CharField(max_length=32)
    options_hash = models.CharField(max_length=32,
        blank=True,
        null=True)
    basket = models.ForeignKey(Basket)
    created = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True)

    @property
    def config(self):
        """ returns the config for an object"""
        #
        # TODO: clean this up and fix circular import
        #
        from basky.config import BasketRegistry
        cls = self.content_object.__class__
        key = '%s_%s' % (cls._meta.app_label, cls._meta.module_name)
        try:
            config = BasketRegistry._registry[key]
            return config
        except KeyError:
            pass

    @staticmethod
    def get_options_hash(options):
        if len(options) == 0:
            return None
        signature = ''
        for option in options:
            signature += '%s|%s;' % (
                option.content_type.pk,
                option.object_id)
        m  = hashlib.md5()
        m.update(signature)
        return m.hexdigest()

    @property
    def total(self):
        #
        # TODO: maybe cycle through the options
        # here to get the priced options?
        #
        return self.price * self.quantity

    def __unicode__(self):
        return self.description

    def save(self, *args, **kwargs):
        # base64 encode to prevent unicode errors
        m  = hashlib.md5()
        m.update('%s' % self.content_type.pk)
        m.update('%s' % self.object_id)
        m.update('%s' % self.price)
        m.update('%s' % smart_str(self.description))
        m.update('%s' % self.options_hash)
        self.hash = m.hexdigest()
        # now save it
        super(BasketItem, self).save(*args, **kwargs)


class BasketItemOption(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    hash = models.CharField(max_length=32)
    content_object = generic.GenericForeignKey(
        'content_type',
        'object_id')
    description = models.CharField(
        blank=True,
        null=True,
        max_length=255)

    @property
    def price(self):
        #
        # TODO: This is where priced options would be implemented
        #
        return Decimal("0.00")

    def __unicode__(self):
        return u'%s' % self.pk

    def save(self, *args, **kwargs):
        m  = hashlib.md5()
        m.update('%s' % self.content_type.pk)
        m.update('%s' % self.object_id)
        self.hash = m.hexdigest()
        # now save it
        super(BasketItemOption, self).save(*args, **kwargs)

"""
The models below are not intended for production use but are
for testing purposes - in order for the models to work you'll
need to set BASKY_TEST_MODELS  = True in your settings
"""

class TestComplexProduct(models.Model):
    title = models.CharField(
        max_length=255)
    price = models.DecimalField(
        decimal_places=2,
        max_digits=10)
    sizes = models.ManyToManyField(
        'TestComplexProductOption',
        limit_choices_to = {'group__exact': 'size' },
        related_name='size_options',
        blank=True,
        null=True)
    colours = models.ManyToManyField(
        'TestComplexProductOption',
        limit_choices_to = {'group__exact': 'colour' },
        related_name='colour_options',
        blank=True,
        null=True)
    description = models.TextField(
        blank=True,
        null=True)
    attribution = models.CharField(
        max_length=255,
        blank=True,
        null=True)

    class Meta:
        managed = basky_settings.BASKY_TEST_MODELS

    def __unicode__(self):
        return u'%s' % self.title

    @property
    def name(self):
        return self.title

    @property
    def total(self):
        return self.price


class TestComplexProductOption(models.Model):
    group = models.CharField(
        max_length=255)
    value = models.CharField(
        max_length=255)

    class Meta:
        managed = basky_settings.BASKY_TEST_MODELS

    def __unicode__(self):
        return u'%s' % self.value


class TestSimpleProduct(models.Model):
    title = models.CharField(
        max_length=255)
    price = models.DecimalField(
        decimal_places=2,
        max_digits=10)
    description = models.TextField(
        blank=True,
        null=True)
    attribution = models.CharField(
        max_length=255,
        blank=True,
        null=True)

    class Meta:
        managed = basky_settings.BASKY_TEST_MODELS

    def __unicode__(self):
        return u'%s' % self.title

    @property
    def name(self):
        return self.title

    @property
    def total(self):
        try:
            for simplediscount in self.simplediscount_set.all():
                self.price *= simplediscount.percentage
        except ValueError:
            pass
        return self.price


class SimpleDiscount(models.Model):
    title = models.CharField(max_length=255)
    simpleproducts = models.ManyToManyField(TestSimpleProduct)
    discount = models.PositiveSmallIntegerField()
    
    class Meta:
        managed = basky_settings.BASKY_TEST_MODELS

    def __unicode__(self):
        return u'%s' % self.title
    
    @property
    def percentage(self):
        percentage = Decimal(100 - self.discount)
        percentage = percentage / 100
        return percentage
