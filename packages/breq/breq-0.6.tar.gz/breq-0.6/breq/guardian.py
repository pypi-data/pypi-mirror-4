# coding: utf-8
from breq import Breq

class Guardian(Breq):

    def set_next(self):
        self.payload['page'] = self.response_content['response']['currentPage'] + 1

    def is_last(self):
        if self.response_content['response']['currentPage'] == self.response_content['response']['pages']:
            return True
        return False