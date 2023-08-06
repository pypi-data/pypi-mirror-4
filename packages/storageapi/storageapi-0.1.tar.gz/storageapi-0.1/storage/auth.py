#!/usr/bin/env python

# This file is part of StorageAPI, by Luke Granger-Brown
# and is licensed under the MIT license, under the terms listed within
# LICENSE which is included with the source of this package

from requests.auth import AuthBase


class QueryAuth(AuthBase):
    def __init__(self, key):
        self.key = key

    def add_key(self, url):
        url += '&' if '?' in url else '?'
        url += 'key=%s' % (self.key,)
        return url

    def __call__(self, r):
        r.url = self.add_key(r.url)
        return r
