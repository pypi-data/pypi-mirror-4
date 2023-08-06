# coding: utf-8
from breq import Breq

class Github(Breq):

    def set_next(self):
        if 'next' in self.response.links:
            self.request_uri = self.response.links['next']['url']

    def is_last(self):
        if 'last' in self.response.links:
            return False
        return True