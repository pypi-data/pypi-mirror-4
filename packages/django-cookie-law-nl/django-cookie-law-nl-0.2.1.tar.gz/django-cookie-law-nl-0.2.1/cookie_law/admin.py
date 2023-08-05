from django.contrib import admin

from .models import CookieUser, CookieBar


class CookieBarAdmin(admin.ModelAdmin):
    list_display = ['button_title', 'language', 'use_this', 'close',]
    list_editable = ['use_this', 'close',]


admin.site.register(CookieUser)
admin.site.register(CookieBar, CookieBarAdmin)
