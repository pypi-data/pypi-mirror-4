#! /usr/bin/env python
# -*- coding: utf-8 -*-

_multiprocess_can_split_ = True

from nose.tools import raises
from sqlalchemy.exc import IntegrityError
from . import BaseTest

from multivac import Project

class TestProjectBase(BaseTest):
    pass

class TestCreate(TestProjectBase):
    def test_empty(self, **kwargs):
        p = Project(**kwargs)
        assert isinstance(p, Project)
        print repr(p)
        print str(p)
        return p
    
    @raises(AttributeError)
    def test_id(self, **kwargs):
        if not 'id' in kwargs:
            kwargs['id'] = self.randint()
        
        p = Project(**kwargs)
        # The previous statement should have failed
        assert False
    
    def test_required(self, **kwargs):
        if not 'name' in kwargs:
            kwargs['name'] = 'name%s' % self.randint()
        p = Project(**kwargs)
        assert isinstance(p, Project)
        assert p.name == kwargs['name']
        print repr(p)
        print str(p)
        return p

class TestAdd(TestProjectBase):
    @raises(IntegrityError)
    def test_empty(self, **kwargs):
        p = TestCreate().test_empty(**kwargs)
        self.session.add(p)
        self.session.flush()
    
    def test_required(self, **kwargs):
        p = TestCreate().test_required(**kwargs)
        self.session.add(p)
        r = self.session.query(Project).filter_by(name=p.name).one()
        assert p is r
        assert p.name == r.name
        return p

class TestDuplicate(TestProjectBase):
    @raises(IntegrityError)
    def test_name(self):
        p = TestCreate().test_required()
        pp = TestCreate().test_required(name = p.name)
        self.session.add(p)
        self.session.add(pp)
        self.session.flush()

class TestUpdate(TestProjectBase):
    def test_name(self):
        p = TestCreate().test_required()
        self.session.add(p)
        self.session.flush()
        p.name = 'new%s' % p.name
        r = self.session.query(Project).filter_by(name=p.name).one()
        assert p is r
        assert p.name == r.name

class TestDelete(TestProjectBase):
    def test_delete(self):
        p = TestCreate().test_required()
        self.session.add(p)
        self.session.flush()
        self.session.delete(p)
        r = self.session.query(Project).filter_by(id=p.id).first()
        assert r is None

class TestTag(TestProjectBase):
    def test_create(self):
        p = TestCreate().test_required()
        value = str(self.randint())
        p.tag['t'] = value
        assert 't' in p.tag
        assert p.tag['t'] == value
    
    def test_add(self, **kwargs):
        p = TestCreate().test_required()
        self.session.add(p)
        value = str(self.randint())
        p.tag['t'] = value
        self.session.flush()
        assert 't' in p.tag
        assert p.tag['t'] == value
    
    def test_update(self):
        p = TestCreate().test_required()
        self.session.add(p)
        value = str(self.randint())
        newvalue = str(int(value) * 10)
        p.tag['t'] = value
        self.session.flush()
        assert 't' in p.tag
        assert p.tag['t'] == value
        p.tag['t'] = newvalue
        self.session.flush()
        assert p.tag['t'] == newvalue
    
    def test_delete(self):
        p = TestCreate().test_required()
        self.session.add(p)
        p.tag['t'] = str(self.randint())
        self.session.flush()
        assert 't' in p.tag
        del p.tag['t']
        self.session.flush()
        assert 't' not in p.tag

class TestProject(TestProjectBase):
    
    project = {}
    
    def setup(self):
        super(TestProject, self).setup()
        h = TestCreate()
        TestProject.project['p1'] = h.test_required(name='p1')
        TestProject.project['p2'] = h.test_required(name='p2')
        TestProject.project['p3'] = h.test_required(name='p3')
        TestProject.project['p4'] = h.test_required(name='p4')
        TestProject.project['p5'] = h.test_required(name='p5')
        TestProject.project['p1'].tag = {'t1' : 'p1t1', 't2' : None  , 't3' : 'p1t3', 't4' : None  , 't5' : 'p1t5'}
        TestProject.project['p2'].tag = {               't2' : 'p2t2', 't3' : None  , 't4' : 'p2t4', 't5' : None  }
        TestProject.project['p3'].tag = {                              't3' : 'p3t3', 't4' : None  , 't5' : 'p3t5'}
        TestProject.project['p4'].tag = {                                             't4' : 'p4t4', 't5' : None  }
        TestProject.project['p5'].tag = {                                                            't5' : 'p5t5'}
        
        self.session.add_all(TestProject.project.itervalues())
        
        return TestProject.project

class TestQuery(TestProject):
    def test_name(self):
        r = self.session.query(Project).filter_by(name='p2').one()
        assert self.project['p2'] is r
        assert self.project['p2'].name == r.name
    
    def test_tag_true(self):
        r = Project.query_tags(self.session, tags={'t2': True}).all()
        assert len(r) == 2
        assert self.project['p1'] in r
        assert self.project['p2'] in r
    
    def test_tag_none(self):
        r = Project.query_tags(self.session, tags={'t4': None}).all()
        assert len(r) == 2
        assert self.project['p1'] in r
        assert self.project['p3'] in r
    
    def test_tag_value(self):
        r = Project.query_tags(self.session, tags={'t5': 'p3t5'}).filter_by(name='p3').all()
        assert len(r) == 1
        assert self.project['p3'] in r
