import datetime

from django.utils.translation import ugettext_lazy as _
from django.db import models


class CookieUser(models.Model):
    """
        Stores the IP adress and user agent of the computer that accepted the cookies.
    """
    address = models.CharField(_('IP Adres'), max_length=39)
    agent = models.CharField(_('User agent'), max_length=250)
    date = models.DateTimeField(_('Datum'), default=datetime.datetime.now)

    class Meta:
        verbose_name = _('cookie gebruiker')
        verbose_name = _('cookie gebruikers')

    def __unicode__(self):
        return self.address


class CookieBar(models.Model):
    """
        Stores the text and the link used in the cookie bar.
    """
    link = models.URLField(_('Link to cookie policy page'), max_length=255)
    link_name = models.CharField(_('The display name of the link. I.e. "cookie-policy"'), max_length=100)
    button_title = models.CharField(_('The title of the allow cookie button'), max_length=50)
    text = models.TextField(_('Text displayed in the cookie bar'))
    use_this = models.BooleanField(_('This Cookie Bar is displayed'), unique=True, default=False)

    def __unicode__(self):
        return self.link
