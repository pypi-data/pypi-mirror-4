import datetime

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _


# Import the languages from the settings
LANGUAGE_CHOICES = settings.LANGUAGES

class CookieUser(models.Model):
    """
        Stores the IP adress and user agent of the computer that accepted the cookies,
        and the date on which it did.
    """
    address = models.CharField(_('IP Adres'), max_length=39)
    agent = models.CharField(_('User agent'), max_length=250)
    date = models.DateTimeField(_('Date'), default=datetime.datetime.now)

    class Meta:
        verbose_name = _('cookie user')
        verbose_name_plural = _('cookie users')

    def __unicode__(self):
        return self.address


class CookieBar(models.Model):
    """
        Stores the cookie bar.
    """
    title = models.CharField(_('Optional title for the displayed text'), max_length=50, blank=True, null=True)
    link = models.URLField(_('Link to cookie policy page'), max_length=255, blank=True, null=True)
    link_name = models.CharField(
        _('The display name of the link. I.e. "cookie-policy"'),
        max_length=100,
        blank=True,
        null=True,
    )
    button_title = models.CharField(_('The title of the allow cookie button'), max_length=50)
    text = models.TextField(_('Text displayed in the cookie bar'))
    use_this = models.BooleanField(_('This Cookie Bar is displayed'), default=False)
    close = models.BooleanField(_('Show a close (dismiss) button for this cookie bar'), default=False)
    language = models.CharField(
        _('Which Language is this cookie bar for?'),
        choices=LANGUAGE_CHOICES,
        blank=True,
        null=True,
        db_index=True,
        max_length=8,
    )

    def __unicode__(self):
        return u'%s' % self.button_title

    class Meta:
        unique_together = (
            ('use_this', 'language'),
            )
