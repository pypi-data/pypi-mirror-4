import json
from urllib import urlencode

from httplib2 import Http


def make_query_string(libs):
    """Make the query string needed to ask for the binaries for all of `libs`.

    :param libs: An iterable of names of libraries.
    :return: the query string needed to request that libdep-service return
        the binaries for the libraries in `libs`
    """
    query_string = ''
    query_params = [('libs', lib) for lib in libs]
    if query_params:
        query_string = '?' + urlencode(query_params)
    return query_string


def make_url(base, libs):
    """Make the url for a get_binaries_for_libraries query.

    :param base: the base url of the instance the request
        should be directed to (e.g. https://libdep-service.ubuntu.com/)
    :param libs: an iterable of names of libraries to include in the query
    :return: the url to request.
    """
    query_string = make_query_string(libs)
    return base + '/v1/get_binaries_for_libraries' + query_string


ALIASES = {
    'production': 'https://libdep-service.ubuntu.com/',
    'staging': 'https://libdep-service.staging.ubuntu.com/',
}


def lookup_alias(alias):
    """Convert an alias for a well-known instance in to a base url.

    :param alias: The alias to use. See `ALIASES` for the supported
        aliases.
    :return: the base URL for the instance corresponding to `alias`.
    :raises ValueError: if the alias isn't known.
    """
    if alias in ALIASES:
        return ALIASES[alias]
    raise ValueError("Unknown alias: {}".format(alias))


class Client(object):
    """A client to talk to libdep-service."""

    def __init__(self, base_url):
        """Create a `Client`.

        :param base_url: the base URL that the client should talk to.
        """
        self.base_url = base_url

    def get_binaries_for_libraries(self, libs):
        """Get the binary packages that contain `libs`.

        :param libs: an iterable of library names.
        :return: a dict mapping library name to a list of package names that
            contain that library. If there were no packages found for a
            library then it will be absent from the dict.
        """
        request_url = make_url(self.base_url, libs)
        h = Http()
        resp, content = h.request(request_url)
        return json.loads(content)

    @classmethod
    def from_alias(cls, alias):
        """Create a `Client` from an alias of a well-known instance.

        :param alias: The alias to use. See `ALIASES` for the supported
            aliases.
        :return: an instance of `Client` configured to use the specified
            well-known instance.
        :raises ValueError: if the alias isn't known.
        """
        return cls(lookup_alias(alias))
