from django.http import HttpResponse, HttpRequest
from django.shortcuts import get_list_or_404, get_object_or_404

from webapp.models import User


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def RedirectResponse(url):
    return HttpResponse("<meta http-equiv=\"refresh\" content=\"0; url={}\" />".format(url))

def get_list(klass, *args, **kwargs):
    try:
        return get_list_or_404(klass, *args, **kwargs)
    except:
        return []

def pass_auth(request: HttpRequest):
    if "sid" not in request.GET:
        raise

    sid = request.GET["sid"]
    user = get_object_or_404(User, id=sid)
    ip = get_client_ip(request)
    if user.login_ip != ip:
        raise

    return user