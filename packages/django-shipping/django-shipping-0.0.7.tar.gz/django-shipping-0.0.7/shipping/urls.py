from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('shipping.views',

    url(r'countries.json$', 'countries', name='shipping-countries'),
    url(r'countries/(?P<country_code>.+)\.json$', 'states', name='shipping-states'),

    url(r'estimation/?$', 'estimation', name='shipping-estimation'),
)
