from django.conf.urls import patterns, include, url

urlpatterns = patterns('monsieur.views',
    url(r'^$', 'home', name='home'),
    url(r'^json/(?P<granularity>[^/]+)/(?P<name>[^/]+)/?$', 'json'),
    url(r'^names/(?P<tag>[^/]+)/?$', 'names'),
    url(r'^attrs/(?P<prefix>[^/]+)/(?P<name>[^/]+)/?$', 'attrs'),
)
