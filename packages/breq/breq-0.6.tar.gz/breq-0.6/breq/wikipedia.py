# coding: utf-8
from breq import Breq

class Wikipedia(Breq):

    def set_next(self):
        self.payload['rvcontinue'] = self.response_content['query-continue']['revisions']['rvcontinue']

    def is_last(self):
        if 'query-continue' in self.response_content:
            return False
        return True