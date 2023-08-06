# coding: utf-8
from breq import Breq

class Guardian(Breq):

    def set_next(self, response):
        self.payload['page'] = response['response']['currentPage'] + 1

    def is_last(self, response):
        if response['response']['currentPage'] == response['response']['pages']:
            return True
        return False