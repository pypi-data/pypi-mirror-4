from django.contrib import admin

from .models import CookieUser, CookieBar


admin.site.register(CookieUser)
admin.site.register(CookieBar)
