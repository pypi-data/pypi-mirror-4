from django.conf.urls.defaults import patterns, url
from .views import allow_cookies, hide_cookie_bar

urlpatterns = patterns('',
    url(r'^allow_cookies/', allow_cookies, name='set_allow_cookies'),
    url(r'^hide_cookie_bar/', hide_cookie_bar, name='hide_cookie_bar'),
)
