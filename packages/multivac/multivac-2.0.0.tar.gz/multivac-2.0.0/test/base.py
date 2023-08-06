#! /usr/bin/env python
# -*- coding: utf-8 -*-

import random

class BaseTest(object):
    
    _session_maker = None
    
    def __init__(self):
        pass
    
    def randint(self, min=100000, max=999999):
        return random.randint(min, max)
    
    def setup(self):
        self.session = self._session_maker()
        return self
    
    def teardown(self):
        self.session.rollback()