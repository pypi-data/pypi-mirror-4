from urllib import urlencode
import urlparse


def replace_querystring(original_url, **replacement):
    url_components = urlparse.urlparse(original_url)
    query_strings = urlparse.parse_qs(url_components.query)

    for key, value in replacement.items():
        query_strings[key] = value

    new_url_components = url_components._replace(query=urlencode(query_strings, True))
    new_url = urlparse.urlunparse(new_url_components)

    return new_url

