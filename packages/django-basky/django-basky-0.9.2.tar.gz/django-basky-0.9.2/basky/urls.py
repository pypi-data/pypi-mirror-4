from django.conf.urls import include, patterns, url

urlpatterns = patterns('',
    # experimental ajax view
    url(r'/remove/(?P<basketitem_pk>\d+)',
        'basky.views.remove',
         name='remove'),
    url(r'/update/',
        'basky.views.update',
        name='update'),
    url(r'.html',
        'basky.views.basket',
        name='basket'),
)
