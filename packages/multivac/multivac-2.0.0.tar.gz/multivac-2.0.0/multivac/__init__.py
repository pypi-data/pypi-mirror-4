#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
MultiVAC generic framework for building tree-based status applications.

This modules provides an implementation of a generic framework, called
MultiVAC, for use in building applications working with trees of elements, in
which the status of a node derives from the status of the leaves.

Two classes are defined, one for each table in the relational model
L{Element},  L{Project}. Also, two additional classes are defined for the
association relationships between the former: L{TagElement} and L{TagProject}.
"""

from version import *

import os
import sys
import warnings

from sqlalchemy import inspect
from sqlalchemy.engine import create_engine, Engine
from sqlalchemy.events import event
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import mapper, relationship, scoped_session, sessionmaker
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import object_session
from sqlalchemy.orm.util import identity_key
from sqlalchemy.schema import Column, MetaData, Table
from sqlalchemy.schema import ForeignKeyConstraint, Index, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.sql import functions
from sqlalchemy.sql.expression import literal, literal_column
from sqlalchemy.types import Boolean, DateTime, Integer, String, Text

#: Metadata object for this model
metadata = MetaData()
#: Name-indexed dict containing the definition of every table
tables = {}
#: Name-indexed dict containing the mapper of every table
mappers = {}

def init(session_maker, **kwargs):
    """
    Initialize the db connection, set up the tables and map the classes.
    
    @param session_maker: Session generator to bind to the model
    @type session_maker: sqlalchemy.orm.session.Session factory
    @param kwargs: Additional settings for the mapper
    @type kwargs: dict
    """
    
    # Bind engine
    metadata.bind = session_maker.bind
    # Setup model
    setup_tables()
    setup_mappers(**kwargs)
    setup_events(session_maker, **kwargs)

def setup_tables():
    """
    Define the tables, columns, keys and constraints of the DB.
    """
    
    global tables
    
    tables['element'] =  Table('element', metadata,
        Column('id',            Integer,     nullable=False),
        Column('forced_status', Boolean,     nullable=False, default=False),
        Column('name',          String(120), nullable=False),
        Column('parent_id',     Integer,     nullable=True),
        Column('project_id',    Integer,     nullable=False),
        Column('status',        String(20),  nullable=False),
        PrimaryKeyConstraint('id'),
        ForeignKeyConstraint(['project_id'],              ['project.id'],                       ondelete='CASCADE'),
        ForeignKeyConstraint(['project_id', 'parent_id'], ['element.project_id', 'element.id'], ondelete='CASCADE'),
        UniqueConstraint('project_id', 'parent_id', 'name'),
        UniqueConstraint('project_id', 'id')
    )
    Index('element_uk_root', tables['element'].c.project_id, tables['element'].c.name,
        postgresql_where=tables['element'].c.parent_id == None, unique=True
    )
    
    tables['status_history'] =  Table('status_history', metadata,
        Column('id',            Integer,     nullable=False),
        Column('element_id',    Integer,     nullable=False),
        Column('timestamp',     DateTime,    nullable=False, default=functions.now()),
        Column('status',        String(20),  nullable=False),
        PrimaryKeyConstraint('id'),
        ForeignKeyConstraint(['element_id'], ['element.id'], ondelete='CASCADE'),
    )
    Index('status_history_ik_order', tables['status_history'].c.element_id, tables['status_history'].c.timestamp)
    
    tables['project'] = Table('project', metadata,
        Column('id',   Integer,    nullable=False),
        Column('name', String(20), nullable=False),
        PrimaryKeyConstraint('id'),
        UniqueConstraint('name'),
    )
    
    tables['tag_element'] = Table('tag_element', metadata,
        Column('name',       String(20), nullable=False),
        Column('element_id', Integer,    nullable=False),
        Column('value',      Text(),     nullable=True),
        PrimaryKeyConstraint('element_id', 'name'),
        ForeignKeyConstraint(['element_id'], ['element.id'], ondelete='CASCADE'),
    )
    
    tables['tag_project'] = Table('tag_project', metadata,
        Column('name',       String(20), nullable=False),
        Column('project_id', Integer,    nullable=False),
        Column('value',      Text(),     nullable=True),
        PrimaryKeyConstraint('project_id', 'name'),
        ForeignKeyConstraint(['project_id'], ['project.id'], ondelete='CASCADE'),
    )

def setup_mappers(**kwargs):
    """
    Define the mapping between tables and classes, and the relationships that link them.
    
    @kwarg extra_mapping: Mapping between database tables and classes
    @type extra_mapping: dict
    @kwarg extra_properties: Dictionary of additional properties for a table
    @type extra_properties: dict
    @kwarg extra_extensions: Dictionary of additional extensions for a table
    @type extra_extensions: dict
    @kwarg extra_kwargs: Dictionary of additional arguments for a mapper
    @type extra_kwargs: dict
    """
    
    global mappers
    
    mapping = {
        'element'        : Element,
        'status_history' : StatusHistory,
        'project'        : Project,
        'tag_element'    : TagElement,
        'tag_project'    : TagProject,
    }
    mapping.update(kwargs.get('extra_mapping', dict()))
    
    assert issubclass(mapping['element'],        Element)
    assert issubclass(mapping['status_history'], StatusHistory)
    assert issubclass(mapping['project'],        Project)
    assert issubclass(mapping['tag_element'],    TagElement)
    assert issubclass(mapping['tag_project'],    TagProject)
    
    properties = {}
    properties['element'] = {
        '_id'            : tables['element'].c.id,
        '_parent_id'     : tables['element'].c.parent_id,
        '_project_id'    : tables['element'].c.project_id,
        '_status'        : tables['element'].c.status,
        '_children'      : relationship(mapping['element'],     back_populates='_parent',   collection_class=set,
                                        primaryjoin = tables['element'].c.parent_id == tables['element'].c.id,
                                        cascade='all', passive_deletes=True),
        '_parent'        : relationship(mapping['element'],     back_populates='_children', collection_class=set,
                                        primaryjoin = tables['element'].c.parent_id == tables['element'].c.id,
                                        remote_side = [ tables['element'].c.id ]),
        '_project'       : relationship(mapping['project'],     back_populates='elements',  collection_class=set),
        'status_history' : relationship(mapping['status_history'], back_populates='_element',
                                        order_by=tables['status_history'].c.id, viewonly=True),
        'tags'           : relationship(mapping['tag_element'], collection_class=attribute_mapped_collection('name'),
                                        cascade='all, delete-orphan', passive_deletes=True),
    }
    properties['status_history'] = {
        '_id'         : tables['status_history'].c.id,
        '_element_id' : tables['status_history'].c.element_id,
        '_timestamp'  : tables['status_history'].c.timestamp,
        '_status'     : tables['status_history'].c.status,
        '_element'     : relationship(mapping['element'], back_populates='status_history'),
    }
    properties['project'] = {
        '_id'      : tables['project'].c.id,
        'elements' : relationship(mapping['element'],     back_populates='_project', collection_class=set,
                                  primaryjoin = tables['element'].c.project_id == tables['project'].c.id,
                                  cascade='all', passive_deletes=True),
        'tags'     : relationship(mapping['tag_project'], collection_class=attribute_mapped_collection('name'),
                                  cascade='all, delete-orphan', passive_deletes=True),
    }
    properties['tag_element'] = {}
    properties['tag_project'] = {}
    
    extra_properties = kwargs.get('extra_properties', dict())
    for entity in mapping.iterkeys():
        properties[entity].update(extra_properties.get(entity, dict()))
    
    extensions = {}
    extensions.update(kwargs.get('extra_extensions', dict()))
    
    options = {}
    options.update(kwargs.get('extra_kwargs', dict()))
    
    for name, cls in mapping.iteritems():
        mappers[name] = mapper(cls, tables[name],
                               properties=properties.get(name, None),
                               extension=extensions.get(name, None),
                               **options.get(name, {}))
    
    """
    Association proxy to access its tags and retrieve their corresponding value.
    Example: instance.tag['name'] = 'value'
    """
    Element.tag = association_proxy('tags', 'value', creator=lambda name, value: mapping['tag_element'](name=name, value=value))
    Project.tag = association_proxy('tags', 'value', creator=lambda name, value: mapping['tag_project'](name=name, value=value))

def setup_events(session_maker, **kwargs):
    """
    Define the events of the model.
    """
    mapping = {
        'element'        : Element,
        'status_history' : StatusHistory,
        'project'        : Project,
        'tag_element'    : TagElement,
        'tag_project'    : TagProject,
    }
    mapping.update(kwargs.get('extra_mapping', dict()))
    
    event.listen(mapping['element']._children, 'append', mapping['element']._children_added)
    event.listen(mapping['element']._children, 'remove', mapping['element']._children_removed)
    event.listen(session_maker, 'before_flush', _session_before_flush)
    event.listen(Engine, "begin", _sqlite_begin)

def _sqlite_begin(conn):
    if conn.engine.name == 'sqlite':
        # Foreign keys are NOT enabled by default... WTF!
        conn.execute("PRAGMA foreign_keys = ON")
        # Force a single active transaction on a sqlite database.
        # This is needed to emulate FOR UPDATE locks :(
        conn.execute("BEGIN EXCLUSIVE")

def _session_before_flush(session, flush_context, instances):
    """
    Ensure that when an Element instance is deleted, the children collection of
    its parent is notified to update and cascade the status change.
    """
    for instance in session.deleted:
        if isinstance(instance, Element):
            if instance.parent:
                instance.parent.children.remove(instance)
    
    for instance in session.new:
        if isinstance(instance, Element):
            session.add(StatusHistory(
                _element = instance,
                _status  = instance.status
            ))
    
    for instance in session.dirty:
        if isinstance(instance, Element):
            if inspect(instance).attrs['_status'].history[2]:
                session.add(StatusHistory(
                    _element = instance,
                    _status  = instance.status
                ))

class CTENotSupported(UserWarning):
    """
    User-defined exception to warn the user when calling a method
    that uses Common Table Expressions (CTE) to perform its work.
    In most cases, there is an alternative slow path of code.
    """
    pass

class ORM_Base(object):
    """
    Base class for mapping the tables.
    """
    
    def __init__(self, *args, **kwargs):
        """
        Base contructor for all mapped entities.
        Set the value of attributes based on keyword arguments.
        
        @param args: Optional arguments to the constructor
        @type args: tuple
        @param kwargs: Optional keyword arguments to the constructor
        @type kwargs: dict
        """
        for name, value in kwargs.iteritems():
            setattr(self, name, value)

class Element(ORM_Base):
    """
    Mapping class for the table «element».
    """
    
    @hybrid_property
    def id(self):
        """
        Read only accessor to prevent setting this field.
        
        @return: Surrogate primary key
        @rtype: int
        """
        return self._id
    
    @hybrid_property
    def children(self):
        """
        The collection of child Elements of this instance.
        
        @return: This instance collection of children Elements
        @rtype: set<L{Element}>
        """
        return self._children
    
    @hybrid_property
    def parent_id(self):
        """
        Read only accessor to prevent setting this field.
        
        @return: Foreign key for the parent L{Element} relationship
        @rtype: int
        """
        return self._parent_id
    
    @hybrid_property
    def parent(self):
        """
        The parent Element of this instance.
        
        @return: The parent Element
        @rtype: L{Element}
        """
        return self._parent
    
    @parent.setter
    def parent(self, parent):
        """
        Setter for the related parent Element of this instance.
        Ensures project coherence between itself and the parent, and proper
        children collection initialization. Also cascades status changes.
        
        @param parent: The parent Element to be assigned
        @type parent: L{Element}
        """
        # Avoid infinite recursion
        if self.parent == parent:
            return
        assert parent == None or isinstance(parent, Element)
        # Check project coherence (parent - self)
        if self.parent != None and parent != None:
            assert parent.project == self.project
        # Ensure children initialization and check for existence. DO NOT REMOVE
        if parent != None:
            assert parent.children != None
        # Assign new parent
        self._parent = parent 
        if self.parent != None:
            self.project = parent.project
            # Cascade status changes only if it has a parent
            if self.status and not self.parent.forced_status:
                self._cascade_status()
    
    @hybrid_property
    def project_id(self):
        """
        Read only accessor to prevent setting this field.
        
        @return: Foreign key for the parent L{Project} relationship
        @rtype: int
        """
        return self._project_id
    
    @hybrid_property
    def project(self):
        """
        The related Project of this instance.
        
        @return: The related Project
        @rtype: L{Project}
        """
        return self._project
    
    @project.setter
    def project(self, project):
        """
        Setter for the related Project of this instance.
        Prevents a second assignation. 
        
        @param project: The Project to be assigned
        @type project: L{Project}
        """
        # Avoid infinite recursion
        if self.project == project:
            return
        assert isinstance(project, Project)
        # Avoid second assignation
        if self.project == None:
            self._project = project
        else:
            raise AttributeError('This attribute cannot be modified once it has been assigned.')
    
    @hybrid_property
    def status(self):
        """
        The status of this instance
        
        @return: status
        @rtype: str
        """
        return self._status
    
    @status.setter
    def status(self, status):
        """
        Setter for the status of this instance.
        Ensures the cascade of a status change.
        
        @param status: The status to be assigned
        @type status: str
        """
        # Avoid infinite recursion
        if self.status == status:
            return
        else:
            self._status = status
        # Cascade status changes
        if self.parent and not self.parent.forced_status:
            self._cascade_status()
    
    def __init__(self, *args, **kwargs):
        """
        Constructor for Element instances.
        Ensures that the «forced_status» field is assigned first to cascade
        status properly.
        
        @param args: Optional arguments to the constructor
        @type args: tuple
        @param kwargs: Optional keyword arguments to the constructor
        @type kwargs: dict
        """
        # Assign first force_status field
        if 'forced_status' in kwargs:
            setattr(self, 'forced_status', kwargs['forced_status'])
            del kwargs['forced_status']
        # Assign the rest of the fields
        super(Element, self).__init__(*args, **kwargs)
    
    @classmethod
    def _children_added(cls, parent, child, initiator):
        """
        Listener to be executed when an element has to be added to a
        children collection.
        Check the added child status and update the parent's one.
        
        @param parent: The Element that has a new child added
        @type parent: L{Element}
        @param child: The Element being added as a child
        @type child: L{Element}
        """
        if not child.status or parent.forced_status:
            return
        if parent.status > child.status:
            parent.status = child.status
        elif (parent.status < child.status) and (len(parent.children) == 1):
            parent.status = child.status
    
    @classmethod
    def _children_removed(cls, parent, child, initiator):
        """
        Listener to be executed when an element has to be removed from a
        children collection.
        Check the removed child status and update the parent's one.
        
        @param parent: The Element that has a child removed
        @type parent: L{Element}
        @param child: The Element being removed as a child
        @type child: L{Element}
        """
        
        if not child.status or parent.forced_status:
            return
        new_children = parent.children.difference([child])
        if parent.status == child.status and new_children:
            new_status = min([c.status for c in new_children])
            if parent.status != new_status:
                parent.status = new_status
    
    def _cascade_status(self):
        """
        Propagate its status to its parent, in a recursive manner.
        """
        if self.parent.status > self.status:
            self.parent.status = self.status
        elif self.parent.status < self.status:
            new_status = min([c.status for c in self.parent.children])
            if self.parent.status != new_status:
                self.parent.status = new_status 
    
    @property
    def ancestors(self):
        """
        Retrieve all the ancestors of this node.
        If the node has no parents, return an empty list.
        Else, start retrieving them from the identity map and, when not there,
        fetch the rest from the database using a CTE.
        
        @return: A list of all the ancestors of this node, ordered by proximity.
        @rtype: list<L{Element}>
        """
        cls = self.__class__
        session = object_session(self)
        # Must flush to get the parent_id from the database
        session.flush()
        if self._parent_id is None:
            # End of the recursion. This Element has no parent.
            return []
        else:
            # Best case available: retrieve the parent from the identity map
            key = identity_key(cls, self._parent_id)
            parent = session.identity_map.get(key, None)
            if parent:
                # Parent found in identity map, recurse and return.
                parents = [parent]
                parents.extend(parent.ancestors)
                return parents
            # Parent NOT found in identity map. Must use CTE
            if session.bind.name != 'postgresql':
                # If not using PostgreSQL, warn the user and use the non-optimized method.
                warnings.warn('CTE are only supported on PostgreSQL. Using slower technique for "ancestor" method.', CTENotSupported)
                parents = [self.parent]
                parents.extend(self.parent.ancestors)
                return parents
            # Use a CTE to retrieve ALL ancestors
            l0 = literal_column('0').label('level')
            q_base = session.query(cls, l0).filter_by(
                         id = self._parent_id
                     ).cte(recursive = True)
            l1 = literal_column('level + 1').label('level')
            q_rec = session.query(cls, l1).filter(
                        q_base.c.parent_id == cls.id
                    )
            q_cte = q_base.union_all(q_rec)
            return session.query(cls).select_from(q_cte).order_by(q_cte.c.level)
    
    def __repr__(self):
        """
        Returns a printable representation of this instance.
        
        @return: A descriptive string containing most of this instance fields
        @rtype: str
        """
        return u"%s(id=%s, name=%s, parent_id=%s, project_id=%s, status=%s, forced_status=%s)" % (
            self.__class__.__name__,
            repr(self.id),
            repr(self.name),
            repr(self.parent_id),
            repr(self.project_id),
            repr(self.status),
            repr(self.forced_status),
        )
    
    def __str__(self):
        """
        Coerces this instance to a string.
        
        @return: The name field
        @rtype: str
        """
        return str(self.name)

class StatusHistory(ORM_Base):
    """
    Mapping class for the table «status_history».
    """
    
    @hybrid_property
    def id(self):
        """
        Read only accessor to prevent setting this field.
        
        @return: Surrogate primary key
        @rtype: int
        """
        return self._id
    
    @hybrid_property
    def element_id(self):
        """
        Read only accessor to prevent setting this field.
        
        @return: Surrogate primary key
        @rtype: int
        """
        return self._element_id
    
    @hybrid_property
    def element(self):
        """
        The related Element of this instance.
        
        @return: The related Element
        @rtype: L{Element}
        """
        return self._element
    
    @hybrid_property
    def timestamp(self):
        """
        Read only accessor to prevent setting this field.
        
        @return: The time this status was updated.
        @rtype: datetime
        """
        return self._timestamp
    
    @hybrid_property
    def status(self):
        """
        The status of this instance
        
        @return: status
        @rtype: str
        """
        return self._status
    
    def __repr__(self):
        """
        Returns a printable representation of this instance.
        
        @return: A descriptive string containing most of this instance fields
        @rtype: str
        """
        return u"%s(element_id=%s, timestamp=%s, status=%s)" % (
            self.__class__.__name__,
            repr(self.element_id),
            repr(self.timestamp),
            repr(self.status),
        )
    
    def __str__(self):
        """
        Coerces this instance to a string.
        
        @return: The status field
        @rtype: str
        """
        return str(self.status)

class Project(ORM_Base):
    """
    Mapping class for the table «project».
    """
    
    @hybrid_property
    def id(self):
        """
        Read only accessor to prevent setting this field.
        
        @return: Surrogate primary key
        @rtype: int
        """
        return self._id
    
    def __repr__(self):
        """
        Returns a printable representation of this instance.
        
        @return: A descriptive string containing most of this instance fields
        @rtype: str
        """
        return u"%s(id=%s, name=%s)" % (
            self.__class__.__name__,
            repr(self.id),
            repr(self.name),
        )
    
    def __str__(self):
        """
        Coerces this instance to a string.
        
        @return: The name field
        @rtype: str
        """
        return str(self.name)

class TagElement(ORM_Base):
    """
    Mapping class for the table «tagelement».
    """
    
    def __init__(self, *args, **kwargs):
        """
        Constructor for TagElement instances.
        Ensures that the «name» field is specified.
        
        @param args: Optional arguments to the constructor
        @type args: tuple
        @param kwargs: Optional keyword arguments to the constructor
        @type kwargs: dict
        """
        assert 'name' in kwargs
        assert kwargs['name'] is not None
        super(TagElement, self).__init__(*args, **kwargs)
    
    def __repr__(self):
        """
        Returns a printable representation of this instance.
        
        @return: A descriptive string containing most of this instance fields
        @rtype: str
        """
        return u"%s(element_id=%s, name=%s, value=%s)" % (
            self.__class__.__name__,
            repr(self.element_id),
            repr(self.name),
            repr(self.value),
        )
    
    def __str__(self):
        """
        Coerces this instance to a string.
        
        @return: The name and value fields
        @rtype: str
        """
        return str(dict(self.name, self.value))

class TagProject(ORM_Base):
    """
    Mapping class for the table «tagproject».
    """
    
    def __init__(self, *args, **kwargs):
        """
        Constructor for TagProject instances.
        Ensures that the «name» field is specified.
        
        @param args: Optional arguments to the constructor
        @type args: tuple
        @param kwargs: Optional keyword arguments to the constructor
        @type kwargs: dict
        """
        assert 'name' in kwargs
        assert kwargs['name'] is not None
        super(TagProject, self).__init__(*args, **kwargs)
    
    def __repr__(self):
        """
        Returns a printable representation of this instance.
        
        @return: A descriptive string containing most of this instance fields
        @rtype: str
        """
        return u"%s(project_id=%s, name=%s, value=%s)" % (
            self.__class__.__name__,
            repr(self.project_id),
            repr(self.name),
            repr(self.value),
        )
    
    def __str__(self):
        """
        Coerces this instance to a string.
        
        @return: The name and value fields
        @rtype: str
        """
        return str(dict(self.name, self.value))
