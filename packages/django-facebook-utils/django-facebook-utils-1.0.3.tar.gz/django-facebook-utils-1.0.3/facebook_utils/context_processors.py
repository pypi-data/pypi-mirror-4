from .utils import is_facebookexternalhit


def facebookexternalhit(request):
    return {
        'facebookexternalhit': is_facebookexternalhit(request),
    }
