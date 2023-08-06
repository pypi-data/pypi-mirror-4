from requests import get


PING_URL = "http://developers.facebook.com/tools/lint/?format=json&url=%s"


def ping(url):
    return get(PING_URL % url)


def is_facebookexternalhit(request):
    return request.META.get('HTTP_USER_AGENT', '').startswith(
        'facebookexternalhit')
