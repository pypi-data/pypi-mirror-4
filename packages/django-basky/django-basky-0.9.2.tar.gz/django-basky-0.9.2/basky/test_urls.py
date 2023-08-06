from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    '',
    (r'^basket', include('basky.urls', namespace='basky')),
    (r'^$', include('basky.urls')),
)
