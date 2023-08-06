#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, scoped_session, sessionmaker, \
                           aliased, joinedload, contains_eager
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String


engine = create_engine('sqlite:///')
Base = declarative_base(engine)

class Node(Base):
    __tablename__ = 'node'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    parent_id = Column(Integer, ForeignKey(id))
    
    parent    = relationship('Node', remote_side=id)
    ancestors = relationship('Node', remote_side=id, uselist=True, viewonly=True, lazy="joined")
    
    def __repr__(self):
        return "Node(id=%s, name=%s, parent_id=%s)" % (
            repr(self.id),
            repr(self.name),
            repr(self.parent_id),
        )

Base.metadata.create_all()

session = scoped_session(sessionmaker(bind=engine))()

n1 = Node(name='n1')
n2 = Node(name='n2')
n3 = Node(name='n3')
n4 = Node(name='n4')
n5 = Node(name='n5')
session.add_all([n1, n2, n3, n4, n5])
session.flush()
n2.parent_id = n1.id
n3.parent_id = n1.id
n4.parent_id = n2.id
n5.parent_id = n2.id
session.commit()
print """
Added some nodes
              [n1]
               |
          /----^----\\
         [n2]      [n3]
          |
     /----^----\\
    [n4]      [n5]
"""
print "*** identity_map has the 5 Node instances"
print ">>> print session.identity_map"
print "    ", session.identity_map
print
print "*** expunging all. Now it is empty"
print ">>> session.expunge_all()"
print ">>> print session.identity_map"
session.expunge_all()
print "    ", session.identity_map
print
print "*** loading n2:"
print ">>> n2 = session.query(Node).filter_by(name='n2').one()"
n2 = session.query(Node).filter_by(name='n2').one()
print
print "*** n2 is %s" % n2
print
print "*** identity_map has n2 instance"
print ">>> print session.identity_map"
print "    ", session.identity_map
print
print "*** Asking about n2.parent. It is NOT in the identity_map, so it will go to the DB."
print ">>> print n2.parent"
print "    ", n2.parent
print
print "*** identity_map has n1 and n2 instance"
print ">>> print session.identity_map"
print "    ", session.identity_map
print
print "=== EXPUNGING EVERYTHING AND TRYING A JOINED LOAD ==="
print ">>> session.expunge_all()"
session.expunge_all()
print
print "*** Now identity_map is empty"
print ">>> print session.identity_map"
print "    ", session.identity_map
print
print "*** querying n2 WITH its parent in a joinedload"
print ">>> n2 = session.query(Node).filter_by(name='n2').options(joinedload('parent')).one()"
n2 = session.query(Node).filter_by(name='n2').options(joinedload('parent')).one()
print
print "*** n2 is %s" % n2
print
print "*** identity_map has n1 and n2 instance"
print ">>> print session.identity_map"
print "    ", session.identity_map
print
print "*** Asking about n2.parent. It is ALREADY in the identity_map, so it will NOT go to the DB."
print ">>> print n2.parent"
print "    ", n2.parent
print
print "=== EXPUNGING EVERYTHING AND TRYING A CONTAINS_EAGER ==="
print ">>> session.expunge_all()"
session.expunge_all()
print
print "*** Now identity_map is empty"
print ">>> print session.identity_map"
print "    ", session.identity_map
print
print "*** querying n2 WITH its parent in a joinedload"
print "*** Parent = aliased(Node)"
print "*** n2 = session.query(Node).filter_by(name='n2').join(Parent, Node.parent_id==Parent.id).options(contains_eager('parent', alias=Parent)).one()"
Parent = aliased(Node)
n2 = session.query(Node).filter_by(name='n2').join(Parent, Node.parent_id==Parent.id).options(contains_eager('parent', alias=Parent)).one()
print
print "*** n2 = %s" % n2
print
print "*** identity_map has n1 and n2 instance"
print "    ", session.identity_map
print
print "*** Asking about n2.parent. It is ALREADY in the identity_map, so it will NOT go to the DB."
p = n2.parent
print
print "*** n2.parent = %s " % n2.parent
print
print "=== EXPUNGING EVERYTHING AND TRYING ANCESTORS ==="
session.expunge_all()
print "*** Now identity_map is empty"
print "    ", session.identity_map
print
print "*** loading n2:"
print ">>> n2 = session.query(Node).filter_by(name='n2').one()"
n2 = session.query(Node).filter_by(name='n2').one()
print
print "*** n2 is %s" % n2
print
print "*** identity_map has n2 instance"
print ">>> print session.identity_map"
print "    ", session.identity_map
print
print "*** Asking about n2.ancestors. It is lazy=NOLOAD, so it will stay empty."
print ">>> print n2.ancestors"
print "    ", n2.ancestors
print
print "=== EXPUNGING EVERYTHING AND TRYING ANCESTORS WITH A JOINED LOAD ==="
print ">>> session.expunge_all()"
session.expunge_all()
print
print "*** Now identity_map is empty"
print ">>> print session.identity_map"
print "    ", session.identity_map
print
print "*** querying n2 WITH its ancestors in a joinedload"
print ">>> n2 = session.query(Node).filter_by(name='n2').options(joinedload('ancestors')).one()"
n2 = session.query(Node).filter_by(name='n2').options(joinedload('ancestors')).one()
print
print "*** n2 is %s" % n2
print
print "*** identity_map has n1 and n2 instance"
print ">>> print session.identity_map"
print "    ", session.identity_map
print
print "*** Asking about n2.ancestors. It is ALREADY loaded."
print ">>> print n2.ancestors"
print "    ", n2.ancestors
print
print "=== EXPUNGING EVERYTHING AND TRYING ANCESTORS ON A PREVIOUSLY LOADED WITH A JOINED LOAD ==="
print ">>> session.expunge_all()"
session.expunge_all()
print
print "*** Now identity_map is empty"
print ">>> print session.identity_map"
print "    ", session.identity_map
print
print "*** querying n2 WITHOUT its ancestors"
print ">>> n2 = session.query(Node).filter_by(name='n2').one()"
n2 = session.query(Node).filter_by(name='n2').one()
print
print "*** n2 is %s" % n2
print
print "*** identity_map has n1 instance"
print ">>> print session.identity_map"
print "    ", session.identity_map
print
print "*** Asking about n2.ancestors. It is empty."
print ">>> print n2.ancestors"
print "    ", n2.ancestors
print
print "*** Load again n2, now with ancestors using joinedload"
print ">>> n2 = session.query(Node).filter_by(name='n2').options(joinedload('ancestors')).one()"
n2 = session.query(Node).filter_by(name='n2').options(joinedload('ancestors')).one()
print
print "*** Query returns TWO instances, n2 and its 'ancestor'"
print
print "*** identity_map ONLY has n1 instance. The parent is NOT saved."
print ">>> print session.identity_map"
print "    ", session.identity_map
print
print "*** Asking about n2.ancestors. It is empty, ALTHOUGH we asked to be loaded with a joinedload."
print ">>> print n2.ancestors"
print "    ", n2.ancestors




