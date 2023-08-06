#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import optparse

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import multivac
import base
import test_element

def parse_args(argv):
    parser = optparse.OptionParser(usage="Usage: %prog [-u URL]")
    parser.add_option("-u", "--url", dest="url",
                      default="sqlite:///",
                      help="database connection URL [default: %default].")
    
    (options, args) = parser.parse_args(argv)
    
    return (options, args)

if __name__ == "__main__" :
    (options, args) = parse_args(sys.argv)
    
    engine = create_engine(options.url, echo=True)
    
    _session_maker = scoped_session(sessionmaker(bind=engine))
    multivac.init(_session_maker)
    
    base.BaseTest._session_maker = _session_maker
    multivac.metadata.drop_all()
    multivac.metadata.create_all()
    
    te = test_element.TestElement()
    te.setup()
    
    session = te.session
    session.flush()
    
    for line in te.__doc__.splitlines():
        print line[:73]