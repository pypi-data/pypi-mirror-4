# coding: utf-8
from breq import Breq

class Wikipedia(Breq):

    def set_next(self, response):
        self.payload['rvcontinue'] = response['query-continue']['revisions']['rvcontinue']

    def is_last(self, response):
        if 'query-continue' in response:
            return False
        return True