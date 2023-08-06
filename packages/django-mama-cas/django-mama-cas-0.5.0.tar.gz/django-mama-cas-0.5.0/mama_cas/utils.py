import re
import urllib
import urlparse

from django.conf import settings


def add_query_params(url, params):
    """
    Inject additional query parameters into an existing URL. If
    parameters already exist with the same name, they will be
    overwritten. Return the modified URL as a string.
    """
    # Ignore additional parameters with empty values
    params = dict([(k, v) for k, v in params.items() if v])
    parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(parts[4]))
    query.update(params)
    parts[4] = urllib.urlencode(query)
    return urlparse.urlunparse(parts)


def is_scheme_https(url):
    """
    Test the scheme of the parameter URL to see if it is HTTPS. If
    it is HTTPS return True, otherwise return False.
    """
    return 'https' == urlparse.urlparse(url).scheme


def clean_service_url(url):
    """
    Return only the scheme, hostname and (optional) port components
    of the parameter URL.
    """
    parts = urlparse.urlparse(url)
    return urlparse.urlunparse((parts.scheme, parts.netloc, '', '', '', ''))


def is_valid_service_url(url):
    """
    Check the provided URL against the configured list of valid service
    URLs. If the service URL matches at least one valid service, return
    ``True``, otherwise return ``False``. If no valid service URLs are
    configured, return ``True``.
    """
    valid_services = map(re.compile,
                         getattr(settings, 'MAMA_CAS_VALID_SERVICES', ()))
    if len(valid_services) == 0:
        return True
    for service in valid_services:
        if service.match(url):
            return True
    return False
