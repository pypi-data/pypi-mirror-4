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

import os
import sys

import sqlalchemy

from sqlalchemy import (Column, MetaData, Table, Index,
                        ForeignKeyConstraint, PrimaryKeyConstraint, UniqueConstraint,
                        Boolean, Integer, String, Text,
                        engine_from_config, func, event)
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import mapper, relationship, scoped_session, sessionmaker
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import literal

try:
    import json
except: # pragma: no cover
    import simplejson as json

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
    
    tables['project'] = Table('project', metadata,
        Column('id',   Integer,    nullable=False),
        Column('name', String(20), nullable=False),
        PrimaryKeyConstraint('id'),
        UniqueConstraint('name'),
    )
    
    tables['tag_element'] = Table('tag_element', metadata,
        Column('tag',        String(20), nullable=False),
        Column('element_id', Integer,    nullable=False),
        Column('value',      Text(),     nullable=True),
        PrimaryKeyConstraint('element_id', 'tag'),
        ForeignKeyConstraint(['element_id'], ['element.id'], ondelete='CASCADE'),
    )
    
    tables['tag_project'] = Table('tag_project', metadata,
        Column('tag',        String(20), nullable=False),
        Column('project_id', Integer,    nullable=False),
        Column('value',      Text(),     nullable=True),
        PrimaryKeyConstraint('project_id', 'tag'),
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
        'element'     : Element,
        'project'     : Project,
        'tag_element' : TagElement,
        'tag_project' : TagProject,
    }
    mapping.update(kwargs.get('extra_mapping', dict()))
    
    assert issubclass(mapping['element'],     Element)
    assert issubclass(mapping['project'],     Project)
    assert issubclass(mapping['tag_element'], TagElement)
    assert issubclass(mapping['tag_project'], TagProject)
    
    properties = {}
    properties['element'] = {
        '_id'           : tables['element'].c.id,
        '_parent_id'    : tables['element'].c.parent_id,
        '_project_id'   : tables['element'].c.project_id,
        '_status'       : tables['element'].c.status,
        # FIXME: Add project_id to parent and children properties when #1401 is fixed
        '_children'     : relationship(mapping['element'],     back_populates='_parent',   collection_class=set,
                                       primaryjoin = tables['element'].c.parent_id == tables['element'].c.id,
                                       cascade='all', passive_deletes=True),
        '_parent'       : relationship(mapping['element'],     back_populates='_children', collection_class=set,
                                       primaryjoin = tables['element'].c.parent_id == tables['element'].c.id,
                                       remote_side = [ tables['element'].c.id ]),
        '_project'      : relationship(mapping['project'],     back_populates='elements',  collection_class=set),
        '_tag'          : relationship(mapping['tag_element'], collection_class=attribute_mapped_collection('tag'),
                                       cascade='all, delete-orphan', passive_deletes=True),
    }
    properties['project'] = {
        '_id'      : tables['project'].c.id,
        'elements' : relationship(mapping['element'],     back_populates='_project', collection_class=set,
                                  primaryjoin = tables['element'].c.project_id == tables['project'].c.id,
                                  cascade='all', passive_deletes=True),
        '_tag'     : relationship(mapping['tag_project'], collection_class=attribute_mapped_collection('tag'),
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
    Element.tag = association_proxy('_tag', 'value', creator=lambda tag, value: mapping['tag_element'](tag=tag, value=value))
    Project.tag = association_proxy('_tag', 'value', creator=lambda tag, value: mapping['tag_project'](tag=tag, value=value))


def setup_events(session_maker, **kwargs):
    """
    Define the events of the model.
    """
    mapping = {
        'element'     : Element,
        'project'     : Project,
        'tag_element' : TagElement,
        'tag_project' : TagProject,
    }
    mapping.update(kwargs.get('extra_mapping', dict()))
    
    event.listen(mapping['element']._children, 'append', mapping['element']._children_added)
    event.listen(mapping['element']._children, 'remove', mapping['element']._children_removed)
    event.listen(session_maker, 'before_flush', _session_before_flush)

def _session_before_flush(session, flush_context, instances):
    """
    Ensure that when an Element instance is deleted, the children collection of
    its parent is notified to update and cascade the status change.
    """
    for instance in session.deleted:
        if isinstance(instance, Element):
            if instance.parent:
                instance.parent.children.remove(instance)

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
    
    @classmethod
    def query_tags(cls, session, tags={}):
        """
        Overriden query method to apply tag-based custom filtering, on top of
        common equality filter.
        
        @param session: The database session in which to execute the query
        @type session: Session
        @param tags: Tag names and values to apply as a filter
        @type tags: dict
        @return: A query selecting Element instances, filtered by tags
        @rtype: Query<L{Element}>
        """
        
        q = session.query(cls)
        if tags:
            crit = literal(False)
            for tag, value in tags.iteritems():
                if value == True: 
                    crit |= (tables['tag_element'].c.tag == tag)
                elif value == None or value != False :
                    crit |= (tables['tag_element'].c.tag == tag) & (tables['tag_element'].c.value == value)
            q = q.join(tables['tag_element']) \
                 .group_by(*[c for c in tables['element'].columns]) \
                 .having(func.count(tables['element'].c.id) == len(tags)) \
                 .filter(crit)
        return q.from_self()
    
    def __repr__(self):
        """
        Returns a printable representation of this instance.
        
        @return: A descriptive string containing most of this instance fields
        @rtype: str
        """
        return u"<Element %s: name '%s', parent_id '%s', project_id '%s', status '%s', forced_status '%s'>" % (self.id, self.name, self.parent_id, self.project_id, self.status, self.forced_status)
    
    def __str__(self):
        """
        Coerces this instance to a string.
        
        @return: The name field
        @rtype: str
        """
        return str(self.name)


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
    
    @classmethod
    def query_tags(cls, session, tags={}):
        """
        Overriden query method to apply tag-based custom filtering, on top of
        common equality filter.
        
        @param session: The database session in which to execute the query
        @type session: Session
        @param tags: Tag names and values to apply as a filter
        @type tags: dict
        @return: A query selecting Project instances, filtered by tags
        @rtype: Query<L{Project}>
        """
        q = session.query(cls)
        if tags:
            crit = literal(False)
            for tag, value in tags.iteritems():
                if value == True: 
                    crit |= (tables['tag_project'].c.tag == tag)
                elif value == None or value != False :
                    crit |= (tables['tag_project'].c.tag == tag) & (tables['tag_project'].c.value == value)
            q = q.join(tables['tag_project']) \
                 .group_by(*[c for c in tables['project'].columns]) \
                 .having(func.count(tables['project'].c.id) == len(tags)) \
                 .filter(crit)
        return q.from_self()
    
    def __repr__(self):
        """
        Returns a printable representation of this instance.
        
        @return: A descriptive string containing most of this instance fields
        @rtype: str
        """
        return u"<Project %s: name '%s'>" % (self.id, self.name)
    
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
        Ensures that the «tag» field is specified.
        
        @param args: Optional arguments to the constructor
        @type args: tuple
        @param kwargs: Optional keyword arguments to the constructor
        @type kwargs: dict
        """
        assert 'tag' in kwargs
        assert kwargs['tag'] is not None
        super(TagElement, self).__init__(*args, **kwargs)


class TagProject(ORM_Base):
    """
    Mapping class for the table «tagproject».
    """
    
    def __init__(self, *args, **kwargs):
        """
        Constructor for TagProject instances.
        Ensures that the «tag» field is specified.
        
        @param args: Optional arguments to the constructor
        @type args: tuple
        @param kwargs: Optional keyword arguments to the constructor
        @type kwargs: dict
        """
        assert 'tag' in kwargs
        assert kwargs['tag'] is not None
        super(TagProject, self).__init__(*args, **kwargs)


# TODOS:
#  - Reevaluate status cascading method. CTE? Triggers?

if __name__ == '__main__': # pragma: no cover
    
    config = json.load(open(os.path.dirname(__file__) + '/config.json', 'r'))
    # Create and configure engine and session
    engine = engine_from_config(config)
    session_maker = scoped_session(sessionmaker(bind=engine, twophase=config['session.twophase']))
    
    class EElement(Element):
        pass
    
    class PProject(Project):
        pass
    
    class TTagProject(TagProject):
        pass
    
    class TTagElement(TagElement):
        pass
    
    init(session_maker, extra_mapping={
        'element'     : EElement,
        'project'     : PProject,
        'tag_project' : TTagProject,
        'tag_element' : TTagElement,
    })
    
    session = session_maker()
    
    metadata.drop_all()
    metadata.create_all()
    
    p1 = PProject()
    p1.name = 'p1'
    
    p2 = PProject(name='p2')
    
    p2.tag['t1'] = 't1'
    p2.tag['t1'] = 'p2t1'
    
    p3 = PProject(name='p3')
    
    e1 = EElement(name='e1', status='50_DONE', forced_status=False, project=p1)
    
    e2 = EElement()
    e2.name = 'e2'
    e2.status = '30_PENDING'
    e2.forced_status = True
    e2.parent = e1
    e2.project = p1
    
    e2.tag['t2'] = 't2'
    e2.tag['t2'] = 'e2t2'

    e3 = EElement(name='e3', status='05_ERROR', forced_status=False, project=p1)
    
    session.add(p1)
    session.commit()
    
    e1.children.remove(e2)
    e2.children.add(e1)
    
    p1.elements.remove(e3)
    p2.elements.add(e3)
    
    session.commit()
    
    print session.query(PProject).filter_by(name='p1').one()
    print session.query(EElement).filter_by(name='e1').one()
