from django import template
from cookie_law.models import CookieBar

register = template.Library()

@register.inclusion_tag('cookie_law/_base_include.html', takes_context=True)
def show_cookie_bar(context):
    request = context['request']
    try:
        bar = CookieBar.objects.get(use_this=True)
    except CookieBar.DoesNotExist:
        raise NotImplementedError('You must set a cookie bar to be shown in the admin.')

    return {'bar': bar, 'request': request}
