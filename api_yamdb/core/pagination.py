from urllib import parse

import requests
from django.utils.encoding import force_str
from rest_framework.pagination import LimitOffsetPagination


def replace_query_param(url, key, val):
    (scheme, netloc, path, query, fragment) = parse.urlsplit(force_str(url))
    scheme = "http"
    netloc = requests.request(
        'GET', 'http://ip.jsontest.com/'
    ).json().get('ip')
    query_dict = parse.parse_qs(query, keep_blank_values=True)
    query_dict[force_str(key)] = [force_str(val)]
    query = parse.urlencode(sorted(list(query_dict.items())), doseq=True)
    return parse.urlunsplit((scheme, netloc, path, query, fragment))


def remove_query_param(url, key):
    (scheme, netloc, path, query, fragment) = parse.urlsplit(force_str(url))
    scheme = "http"
    netloc = requests.request(
        'GET', 'http://ip.jsontest.com/'
    ).json().get('ip')
    query_dict = parse.parse_qs(query, keep_blank_values=True)
    query_dict.pop(key, None)
    query = parse.urlencode(sorted(list(query_dict.items())), doseq=True)
    return parse.urlunsplit((scheme, netloc, path, query, fragment))


class CustomPagination(LimitOffsetPagination):

    def get_next_link(self):
        if self.offset + self.limit >= self.count:
            return None

        url = self.request.build_absolute_uri()
        url = replace_query_param(url, self.limit_query_param, self.limit)

        offset = self.offset + self.limit
        return replace_query_param(url, self.offset_query_param, offset)

    def get_previous_link(self):
        if self.offset <= 0:
            return None

        url = self.request.build_absolute_uri()
        url = replace_query_param(url, self.limit_query_param, self.limit)

        if self.offset - self.limit <= 0:
            return remove_query_param(url, self.offset_query_param)

        offset = self.offset - self.limit
        return replace_query_param(url, self.offset_query_param, offset)
