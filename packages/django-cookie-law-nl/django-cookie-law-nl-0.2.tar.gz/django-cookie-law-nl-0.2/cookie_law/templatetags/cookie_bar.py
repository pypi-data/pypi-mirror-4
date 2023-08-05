from django import template

from cookie_law.models import CookieBar
from cookie_law.functions import create_default_cookie_bars


register = template.Library()

@register.inclusion_tag('cookie_law/_base_include.html', takes_context=True)
def show_cookie_bar(context):
    """
        Passes the cookie bar and the request to the template.
        Checks for multilingual sites by checking for request.LANGUAGE_CODE.
        If the language code is not found, a default Dutch cookie bar is used.
    """
    request = context['request']

    try:
        language_code = request.LANGUAGE_CODE
    except AttributeError:
        language_code = None

    if language_code:
        # Create default multilingual cookie bars if needed
        create_default_cookie_bars()

        # Get the right cookie bar for the language code
        bar = CookieBar.objects.filter(language=language_code).get(use_this=True)
    else:
        # Get or create the default dutch cookie bar
        bar, created = CookieBar.objects.get_or_create(
            language='nl',
            defaults={
                'button_title': "Sta toe",
                'text': "Deze site gebruikt cookies.",
                'use_this': True,
                }
        )

    return {'bar': bar, 'request': request}