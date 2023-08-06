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
        self.response = None

    def __iter__(self):
        return self

    def next(self):
        if self.last or (self.max_requests and self.request_count >= self.max_requests):
            raise StopIteration

        try:
            response = requests.get(self.request_uri, params=self.payload)
        except Exception, err:
            print('HTTP request exception: %s\n%r' % self.request_uri, err)
            return

        if not response.ok:
            print('HTTP request not ok: %s' % response.url)
            return

        self.request_count += 1
        self.response = response
        self.response_content = json.loads(response.content)

        if self.is_last():
            self.last = True
        else:
            self.set_next()
            if self.timeout:
                time.sleep(self.timeout)

        return self.response_content