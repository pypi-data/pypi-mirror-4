from django.conf import settings
from basky.models import Basket
from basky import settings as basky_settings

class BasketInSessionMiddleware(object):
    
    def process_request(self, request):
        basket_name = getattr(settings,
                        'BASKY_SESSION_KEY_NAME',
                        basky_settings.BASKY_SESSION_KEY_NAME)
        try:
            b = request.session[basket_name]
        except KeyError:
            b = Basket()
            request.session[basket_name] = b
        # ordering of this is important: save basket, then save session
        b.session_key = request.session.session_key
        # if session key is none
        if b.session_key is None:
            request.session.save()
            b.session_key = request.session.session_key
        # save basket
        b.save()
        # set it back to the session
        request.session[basket_name] = b
        # save session
        request.session.save()

class ForceCCBasketMiddleware(object):
    """if other baskets exist this middleware will clobber the current
    request.session[basket_name] into a basky instance
    
    This middleware MUST come before the BasketInSessionMiddleware to have any
    useful effect
    """
    
    def process_request(self, request):
        basket_name = getattr(settings,
                        'BASKY_SESSION_KEY_NAME',
                        basky_settings.BASKY_SESSION_KEY_NAME)
        try:
            b = request.session[basket_name]
            if not isinstance(b, Basket):
                del(request.session[basket_name])
                request.session.save()
                b = Basket()
                b.session_key = request.session.session_key
                b.save()
                request.session[basket_name] = b
                request.session.save()
        except KeyError:
            pass
            
