from django.conf.urls.defaults import patterns, url
from .views import allow_cookies

urlpatterns = patterns('',
    url(r'^allow_cookies/', allow_cookies, name='set_allow_cookies'),
)
