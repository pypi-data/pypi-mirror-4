import datetime

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect

from .models import CookieUser


@csrf_protect
def allow_cookies(request):
    """
        Uses the request.META headers 'REMOTE_ADDR' and 'HTTP_USER_AGENT' to log a user as having accepted
        the use of cookies by this site.
        Sets a cookie, 'allow_cookies', that expires in 10 years with the value of 1.
    """
    if not request.method == 'POST':
        return HttpResponse(status=405)

    # Log the user as having agreed to the cookie policy
    remote_ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')
    CookieUser(
        address=remote_ip,
        agent=request.META['HTTP_USER_AGENT']).save()

    expires_at = datetime.datetime.now() + datetime.timedelta(weeks=520)
    response = HttpResponse(status=200)
    response.set_cookie('allow_cookies', value='1', expires=expires_at)

    return response

@csrf_protect
def hide_cookie_bar(request):
    """
        Sets a cookie that expires in 1 week.
    """
    if not request.method == 'POST':
        return HttpResponse(status=405)

    expires_at = datetime.datetime.now() + datetime.timedelta(weeks=1)
    response = HttpResponse(status=200)
    response.set_cookie('hide_cookie_bar', value='1', expires=expires_at)

    return response
