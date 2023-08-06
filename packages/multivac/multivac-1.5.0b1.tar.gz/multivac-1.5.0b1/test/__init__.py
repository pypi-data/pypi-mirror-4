#! /usr/bin/env python
# -*- coding: utf-8 -*-

_multiprocess_shared_ = True

import os
import sys
import random
import logging

import base
import multivac

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.session import sessionmaker

from testconfig import config

log = logging.getLogger('nose')

def setup():
    # Retrieve database settings. Use in-memory sqlite by default.
    url  = config.get('database', {}).get('url', 'sqlite:///')
    echo = config.get('database', {}).get('echo', False) in ['1', 'y', 'yes', 't', 'true', True]
    
    engine = create_engine(url, echo=echo)
    base.BaseTest._session_maker = scoped_session(sessionmaker(bind=engine))
    multivac.init(base.BaseTest._session_maker)
    
    multivac.metadata.drop_all()
    multivac.metadata.create_all()

def teardown():
    #multivac.metadata.drop_all()
    pass
