# -*- coding: utf-8 -*-
from django.db import managers



class BasketLineManager(models.Manager):
    
    def grouped(self):
        pass
        # todo basket items grouped into quanities for displaying back to the 
        # the end user