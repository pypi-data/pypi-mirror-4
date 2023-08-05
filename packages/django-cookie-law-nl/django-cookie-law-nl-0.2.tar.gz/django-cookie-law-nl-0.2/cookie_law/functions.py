from django.utils.translation import ugettext as _

from .models import LANGUAGE_CHOICES, CookieBar


def create_default_cookie_bars():
    """
        Create a default cookie bar for each defined language
    """
    for language in LANGUAGE_CHOICES:
        cookiebar, created = CookieBar.objects.get_or_create(
            language=language[0],
            defaults={
                'button_title': _("Allow cookies"),
                'text': _("This site uses cookies."),
                'use_this': True,
                }
        )
