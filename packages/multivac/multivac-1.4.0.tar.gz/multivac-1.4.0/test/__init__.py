#! /usr/bin/env python
# -*- coding: utf-8 -*-

_multiprocess_shared_ = True

import os
import sys
import random
import logging
import multivac

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.session import sessionmaker

engine = create_engine('sqlite:///', echo=True)
session_maker = scoped_session(sessionmaker(bind=engine))
multivac.init(session_maker)

log = logging.getLogger('nose')

class BaseTest(object):
    
    def __init__(self):
        pass
    
    def randint(self, min=100000, max=999999):
        return random.randint(min, max)
    
    def setup(self):
        log.info("* * * * * * BaseTest.setup")
        self.session = session_maker()
        return self
    
    def teardown(self):
        log.info("* * * * * * BaseTest.teardown")
        self.session.rollback()

def setup():
    log.info("* * * * * * __init__.setup")
    
    multivac.metadata.drop_all()
    multivac.metadata.create_all()

def teardown():
    log.info("* * * * * * __init__.teardown")
    #multivac.metadata.drop_all()
    pass