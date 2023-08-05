from django import template

from cookie_law.models import CookieBar

register = template.Library()

@register.inclusion_tag('cookie_law/_base_include.html', takes_context=True)
def show_cookie_bar(context):
    """
        Passes the cookie bar and the request to the template.
        Creates a default cookie bar if one hasn't been created yet.
    """
    request = context['request']
    try:
        bar = CookieBar.objects.get(use_this=True)
    except CookieBar.DoesNotExist:
        bar = CookieBar(
            link='http://nl.wikipedia.org/wiki/Cookie_(internet)',
            link_name='cookies',
            button_title='Akkoord',
            text='Deze site gebruikt',
        )

    return {'bar': bar, 'request': request}