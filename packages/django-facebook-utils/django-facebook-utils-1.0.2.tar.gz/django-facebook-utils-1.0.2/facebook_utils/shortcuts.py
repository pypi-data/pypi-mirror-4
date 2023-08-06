from .utils import (
    ping as _ping,
    is_facebookexternalhit,
)


__all__ = (
    'ping_facebook',
    'is_facebookexternalhit',
)


def ping_facebook(url):
    try:
        _ping(url)
    except:
        return False
    return True
