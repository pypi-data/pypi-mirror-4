#! /usr/bin/env python
# -*- coding: utf-8 -*-

#_multiprocess_can_split_ = True

import os
import json
import random

import model

from sqlalchemy import engine_from_config
from sqlalchemy.orm import scoped_session, sessionmaker

import sys

try:
    # 2.7
    from unittest.case import SkipTest
except ImportError:
    # 2.6 and below
    class SkipTest(Exception):
        """
        Raise this exception to mark a test as skipped.
        """
    pass

config = json.load(open(os.path.dirname(__file__) + "/config.json", "r"))
engine = engine_from_config(config)
session_maker = scoped_session(sessionmaker(bind=engine, twophase=config['session.twophase']))

def randint():
    return random.randint(100000, 999999)

class BaseTest(object):
    
    def __init__(self):
        pass
    
    def setup(self):
        self.session = session_maker()
        return self
    
    def teardown(self):
        self.session.rollback()

class CustomElement(model.Element):
    pass

class CustomProject(model.Project):
    pass

class CustomTagElement(model.TagElement):
    pass

class CustomTagProject(model.TagProject):
    pass