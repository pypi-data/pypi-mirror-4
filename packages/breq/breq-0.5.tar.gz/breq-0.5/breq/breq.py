# coding: utf-8
# Python class to browse through API requests
import json
import requests
import time
from abc import ABCMeta, abstractmethod

class Breq(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def set_next(self, response):
        pass

    @abstractmethod
    def is_last(self, response):
        pass

    def __init__(self, request_uri, payload=None, max_requests=None, timeout=None):
        self.request_uri = request_uri
        self.max_requests = max_requests
        if payload is None:
            payload = {}
        self.payload = payload

        self.request_count = 0
        self.last = False
        self.timeout = timeout

    def __iter__(self):
        return self

    def next(self):
        if self.last or (self.max_requests and self.request_count >= self.max_requests):
            raise StopIteration

        try:
            resp = requests.get(self.request_uri, params=self.payload)
        except Exception, err:
            print('HTTP request exception: %s\n%r' % self.request_uri, err)
            return

        if not resp.ok:
            print('HTTP request not ok: %s' % resp.url)
            return

        self.request_count += 1

        response = json.loads(resp.content)
        if self.is_last(response):
            self.last = True
        else:
            self.set_next(response)
            if self.timeout:
                time.sleep(self.timeout)

        return response