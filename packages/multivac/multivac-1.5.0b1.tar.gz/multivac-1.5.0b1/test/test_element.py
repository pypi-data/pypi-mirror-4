#! /usr/bin/env python
# -*- coding: utf-8 -*-

_multiprocess_can_split_ = True

import warnings

from nose.tools import raises
from nose.exc import SkipTest
from sqlalchemy.exc import IntegrityError, UnboundExecutionError
from test_project import TestProject

import multivac

from multivac import Element
from multivac import Project

class TestElementBase(TestProject):
    pass

class TestCreate(TestElementBase):
    def test_empty(self, **kwargs):
        e = Element(**kwargs)
        assert isinstance(e, Element)
        print repr(e)
        print str(e)
        return e
    
    def test_id(self, **kwargs):
        @raises(AttributeError)
        def check_id(field):
            p = Element(**dict({field: self.randint()}))
            # The previous statement should have failed
            assert False
        
        yield check_id, 'id'
        yield check_id, 'parent_id'
        yield check_id, 'project_id'
    
    def test_required(self, **kwargs):
        if not 'name' in kwargs:
            kwargs['name'] = 'name%s' % self.randint()
        if not 'project' in kwargs:
            kwargs['project'] = self.project['p2']
        if not 'status' in kwargs:
            kwargs['status'] = '2_STATUS'
        e = Element(**kwargs)
        assert isinstance(e, Element)
        assert e.name == kwargs['name']
        assert e.project == kwargs['project']
        assert e.status == kwargs['status']
        print repr(e)
        print str(e)
        return e
    
    def test_all(self, **kwargs):
        if not 'forced_status' in kwargs:
            kwargs['forced_status'] = False
        if not 'name' in kwargs:
            kwargs['name'] = 'name%s' % self.randint()
        if not 'project' in kwargs:
            kwargs['project'] = self.project['p2']
        if not 'status' in kwargs:
            kwargs['status'] = '2_STATUS'
        e = Element(**kwargs)
        assert isinstance(e, Element)
        assert e.forced_status == kwargs['forced_status']
        assert e.name == kwargs['name']
        assert e.project == kwargs['project']
        assert e.status == kwargs['status']
        print repr(e)
        print str(e)
        return e

class TestAdd(TestElementBase):
    @raises(IntegrityError)
    def test_empty(self, **kwargs):
        e = TestCreate().test_empty(**kwargs)
        self.session.add(e)
        self.session.flush()
    
    def test_required(self, **kwargs):
        e = TestCreate().test_required(**kwargs)
        self.session.add(e)
        r = self.session.query(Element).filter_by(name=e.name, project=e.project, status=e.status).one()
        assert e is r
        assert e.name == r.name
        assert e.project == r.project
        assert e.status == r.status
        return e
    
    def test_all(self, **kwargs):
        e = TestCreate().test_all(**kwargs)
        self.session.add(e)
        r = self.session.query(Element).filter_by(forced_status=e.forced_status, name=e.name, project=e.project, status=e.status).one()
        assert e is r
        assert e.forced_status == r.forced_status
        assert e.name == r.name
        assert e.project == r.project
        assert e.status == r.status
        return e

class TestDuplicate(TestElementBase):
    @raises(IntegrityError)
    def test_root_name(self):
        # This test uses an additional partial key to work with root nodes.
        e = TestCreate().test_required()
        ee = TestCreate().test_required(project=e.project, name=e.name, parent=e.parent)
        self.session.add(e)
        self.session.add(ee)
        self.session.flush()
        
    @raises(IntegrityError)
    def test_name(self):
        # This test does not apply to root nodes.
        # The UNIQUE KEY does not enforce with NULL values
        r = TestCreate().test_required()
        e = TestCreate().test_required(parent=r)
        ee = TestCreate().test_required(project=e.project, name=e.name, parent=e.parent)
        self.session.add(e)
        self.session.add(ee)
        self.session.flush()

class TestUpdate(TestElementBase):
    def test_forced_status(self, **kwargs):
        e = TestCreate().test_all(**kwargs)
        self.session.add(e)
        e.forced_status = not e.forced_status
        self.session.flush()
        r = self.session.query(Element).filter_by(project=e.project, parent=e.parent, name=e.name).one()
        assert e is r
        assert e.forced_status == r.forced_status
    
    def test_name(self, **kwargs):
        e = TestCreate().test_required(**kwargs)
        self.session.add(e)
        self.session.flush()
        e.name = 'new%s' % e.name
        r = self.session.query(Element).filter_by(project=e.project, parent=e.parent, name=e.name).one()
        assert e is r
        assert e.name == r.name
    
    def test_parent(self, **kwargs):
        a = TestCreate().test_required()
        b = TestCreate().test_required()
        e = TestCreate().test_required(parent=a)
        self.session.add_all([a, b, e])
        self.session.flush()
        e.parent = b
        r = self.session.query(Element).filter_by(project=e.project, parent=e.parent, name=e.name).one()
        assert e is r
        assert e.parent == r.parent
    
    def test_project(self):
        e = TestCreate().test_required(project=self.project['p2'])
        self.session.add(e)
        self.session.flush()
        try:
            e.project = self.project['p3']
        except AttributeError as e:
            assert e.message == 'This attribute cannot be modified once it has been assigned.'
    
    def test_status(self, **kwargs):
        e = TestCreate().test_required(status='2_STATUS')
        self.session.add(e)
        self.session.flush()
        # Test re-assignation
        e.status = e.status
        e.status = '1_STATUS'
        r = self.session.query(Element).filter_by(project=e.project, parent=e.parent, name=e.name).one()
        assert e is r
        assert e.status == r.status

class TestDelete(TestElementBase):
    def test_delete(self):
        e = TestCreate().test_required()
        self.session.add(e)
        self.session.flush()
        self.session.delete(e)
        r = self.session.query(Element).filter_by(project=e.project, parent=e.parent, name=e.name).first()
        assert r is None

class TestRelationships(TestElementBase):
    def test_parent(self):
        r = TestCreate().test_required()
        e = TestCreate().test_required(parent=r)
        assert e in r.children
        assert e.project == r.project
    
    def test_project(self):
        e = TestCreate().test_required(project=self.project['p2'])
        assert e in e.project.elements
    
    def test_children_preload(self):
        # Ensure that the children collection is preloaded before triggering any event.
        # This is needed when an instance (C) selects as a parent a instance (P) with
        # its children collection not loaded. In that case, the backref fires, adds the C to
        # P.children collection, but as it is not loaded, the event code triggers a load
        # and fails.
        p = TestCreate().test_required(status='1_STATUS')
        self.session.add(p)
        self.session.flush()
        self.session.expire(p)
        c = TestCreate().test_required(status='2_STATUS')
        c.parent = p
        assert c.parent == p
        assert c in p.children
    
    def test_parent_load_on_delete(self):
        # Ensure that the parent children collection is updated when a children element
        # is deleted.
        e1 = TestCreate().test_required()
        e2 = TestCreate().test_required(status='2_STATUS', parent=e1)
        e3 = TestCreate().test_required(status='1_STATUS', parent=e1)
        self.session.add(e1)
        assert e1.children.issuperset(set([e2, e3]))
        assert e1.status == '1_STATUS'
        assert e2.status == '2_STATUS'
        assert e3.status == '1_STATUS'
        self.session.flush()
        self.session.expire(e1)
        self.session.delete(e3)
        self.session.flush()
        assert e1.status == '2_STATUS'

class TestTag(TestElementBase):
    def test_create(self):
        e = TestCreate().test_required()
        value = str(self.randint())
        e.tag['t'] = value
        assert 't' in e.tag
        assert e.tag['t'] == value
    
    def test_add(self, **kwargs):
        e = TestCreate().test_required()
        self.session.add(e)
        value = str(self.randint())
        e.tag['t'] = value
        self.session.flush()
        assert 't' in e.tag
        assert e.tag['t'] == value
    
    def test_update(self):
        e = TestCreate().test_required()
        self.session.add(e)
        value = str(self.randint())
        newvalue = str(int(value) * 10)
        e.tag['t'] = value
        self.session.flush()
        assert 't' in e.tag
        assert e.tag['t'] == value
        e.tag['t'] = newvalue
        self.session.flush()
        assert e.tag['t'] == newvalue
    
    def test_delete(self):
        e = TestCreate().test_required()
        self.session.add(e)
        e.tag['t'] = str(self.randint())
        self.session.flush()
        assert 't' in e.tag
        del e.tag['t']
        self.session.flush()
        assert 't' not in e.tag

class TestElement(TestElementBase):
    u"""
       Tree representation of all elements classified by project
       
                         [p1]                                            │                   [p2]                                            │                   [p3]                                    │                   [p4]                                    │                   [p5]                                  
                                                                         │                                                                   │                                                           │                                                           │                                                         
        ┌────────────┐           ┌────────────┐                          │  ┌────────────┐           ┌────────────┐                          │  ┌────────────┐           ┌────────────┐                  │  ┌────────────┐           ┌────────────┐                  │  ┌────────────┐           ┌────────────┐                
        │ e1104 (4)  │           │ e1202 (2)  │                          │  │ e2104 (4)  │           │ e2202 (2)  │                          │  │ e3104 (4)  │           │ e3202 (3)  │                  │  │ e4104 (4)  │           │ e4202 (4)  │                  │  │ e5104 (5)  │           │ e5202 (5)  │                
        └────────────┘           └────────────┘                          │  └────────────┘           └────────────┘                          │  └────────────┘           └────────────┘                  │  └────────────┘           └────────────┘                  │  └────────────┘           └────────────┘                
                                /              \                         │                          /              \                         │                          /              \                 │                          /              \                 │                          /              \               
                               /                \                        │                         /                \                        │                         /                \                │                         /                \                │                         /                \              
                 ┌────────────┐                  ┌────────────┐          │           ┌────────────┐                  ┌────────────┐          │           ┌────────────┐                  ┌────────────┐  │           ┌────────────┐                  ┌────────────┐  │           ┌────────────┐                  ┌────────────┐
                 │ e1322 (2)  │                  │ e1423 (3F) │          │           │ e2322 (2)  │                  │ e2423 (3F) │          │           │ e3322 (3)  │                  │ e3423 (3F) │  │           │ e4322 (4)  │                  │ e4423 (4F) │  │           │ e5322 (5)  │                  │ e5423 (5F) │
                 └────────────┘                  └────────────┘          │           └────────────┘                  └────────────┘          │           └────────────┘                  └────────────┘  │           └────────────┘                  └────────────┘  │           └────────────┘                  └────────────┘
                  /          \                    /          \           │            /          \                    /          \           │            /          \                         |         │            /          \                                   │                 |                                       
                 /            \                  /            \          │           /            \                  /            \          │           /            \                        |         │           /            \                                  │                 |                                       
        ┌────────────┐   ┌───────────┐   ┌────────────┐   ┌───────────┐  │  ┌────────────┐   ┌───────────┐   ┌────────────┐   ┌───────────┐  │  ┌────────────┐   ┌───────────┐           ┌────────────┐  │  ┌────────────┐   ┌───────────┐                           │           ┌────────────┐                                
        │ e1533 (3F) │   │ e1632 (2) │   │ e1745 (5)  │   │ e1843 (3) │  │  │ e2533 (3F) │   │ e2632 (2) │   │ e2745 (5)  │   │ e2843 (3) │  │  │ e3533 (3F) │   │ e3632 (3) │           │ e3745 (5)  │  │  │ e4533 (4F) │   │ e4632 (4) │                           │           │ e5533 (5F) │                                
        └────────────┘   └───────────┘   └────────────┘   └───────────┘  │  └────────────┘   └───────────┘   └────────────┘   └───────────┘  │  └────────────┘   └───────────┘           └────────────┘  │  └────────────┘   └───────────┘                           │           └────────────┘                                
              |       
              |       
        ┌────────────┐
        │ e1953 (3)  │
        └────────────┘
    """
    element = {}
    
    def setup(self):
        super(TestElement, self).setup()
        h = TestCreate()
        TestElement.element['e1104'] = h.test_required(project=self.project['p1'], parent=None,                  status='4_STATUS', forced_status=False, name='e1104')
        TestElement.element['e1202'] = h.test_required(project=self.project['p1'], parent=None,                  status='2_STATUS', forced_status=False, name='e1202')
        TestElement.element['e1322'] = h.test_required(project=self.project['p1'], parent=self.element['e1202'], status='2_STATUS', forced_status=False, name='e1322')
        TestElement.element['e1423'] = h.test_required(project=self.project['p1'], parent=self.element['e1202'], status='3_STATUS', forced_status=True,  name='e1423')
        TestElement.element['e1533'] = h.test_required(project=self.project['p1'], parent=self.element['e1322'], status='3_STATUS', forced_status=True,  name='e1533')
        TestElement.element['e1632'] = h.test_required(project=self.project['p1'], parent=self.element['e1322'], status='2_STATUS', forced_status=False, name='e1632')
        TestElement.element['e1745'] = h.test_required(project=self.project['p1'], parent=self.element['e1423'], status='5_STATUS', forced_status=False, name='e1745')
        TestElement.element['e1843'] = h.test_required(project=self.project['p1'], parent=self.element['e1423'], status='3_STATUS', forced_status=False, name='e1843')
        TestElement.element['e1953'] = h.test_required(project=self.project['p1'], parent=self.element['e1533'], status='3_STATUS', forced_status=False, name='e1953')
        TestElement.element['e2104'] = h.test_required(project=self.project['p2'], parent=None,                  status='4_STATUS', forced_status=False, name='e2104')
        TestElement.element['e2202'] = h.test_required(project=self.project['p2'], parent=None,                  status='2_STATUS', forced_status=False, name='e2202')
        TestElement.element['e2322'] = h.test_required(project=self.project['p2'], parent=self.element['e2202'], status='2_STATUS', forced_status=False, name='e2322')
        TestElement.element['e2423'] = h.test_required(project=self.project['p2'], parent=self.element['e2202'], status='3_STATUS', forced_status=True,  name='e2423')
        TestElement.element['e2533'] = h.test_required(project=self.project['p2'], parent=self.element['e2322'], status='3_STATUS', forced_status=True,  name='e2533')
        TestElement.element['e2632'] = h.test_required(project=self.project['p2'], parent=self.element['e2322'], status='2_STATUS', forced_status=False, name='e2632')
        TestElement.element['e2745'] = h.test_required(project=self.project['p2'], parent=self.element['e2423'], status='5_STATUS', forced_status=False, name='e2745')
        TestElement.element['e2843'] = h.test_required(project=self.project['p2'], parent=self.element['e2423'], status='3_STATUS', forced_status=False, name='e2843')
        TestElement.element['e3104'] = h.test_required(project=self.project['p3'], parent=None,                  status='4_STATUS', forced_status=False, name='e3104')
        TestElement.element['e3202'] = h.test_required(project=self.project['p3'], parent=None,                  status='3_STATUS', forced_status=False, name='e3202')
        TestElement.element['e3322'] = h.test_required(project=self.project['p3'], parent=self.element['e3202'], status='3_STATUS', forced_status=False, name='e3322')
        TestElement.element['e3423'] = h.test_required(project=self.project['p3'], parent=self.element['e3202'], status='3_STATUS', forced_status=True,  name='e3423')
        TestElement.element['e3533'] = h.test_required(project=self.project['p3'], parent=self.element['e3322'], status='3_STATUS', forced_status=True,  name='e3533')
        TestElement.element['e3632'] = h.test_required(project=self.project['p3'], parent=self.element['e3322'], status='3_STATUS', forced_status=False, name='e3632')
        TestElement.element['e3745'] = h.test_required(project=self.project['p3'], parent=self.element['e3423'], status='5_STATUS', forced_status=False, name='e3745')
        TestElement.element['e4104'] = h.test_required(project=self.project['p4'], parent=None,                  status='4_STATUS', forced_status=False, name='e4104')
        TestElement.element['e4202'] = h.test_required(project=self.project['p4'], parent=None,                  status='4_STATUS', forced_status=False, name='e4202')
        TestElement.element['e4322'] = h.test_required(project=self.project['p4'], parent=self.element['e4202'], status='4_STATUS', forced_status=False, name='e4322')
        TestElement.element['e4423'] = h.test_required(project=self.project['p4'], parent=self.element['e4202'], status='4_STATUS', forced_status=True,  name='e4423')
        TestElement.element['e4533'] = h.test_required(project=self.project['p4'], parent=self.element['e4322'], status='4_STATUS', forced_status=True,  name='e4533')
        TestElement.element['e4632'] = h.test_required(project=self.project['p4'], parent=self.element['e4322'], status='4_STATUS', forced_status=False, name='e4632')
        TestElement.element['e5104'] = h.test_required(project=self.project['p5'], parent=None,                  status='5_STATUS', forced_status=False, name='e5104')
        TestElement.element['e5202'] = h.test_required(project=self.project['p5'], parent=None,                  status='5_STATUS', forced_status=False, name='e5202')
        TestElement.element['e5322'] = h.test_required(project=self.project['p5'], parent=self.element['e5202'], status='5_STATUS', forced_status=False, name='e5322')
        TestElement.element['e5423'] = h.test_required(project=self.project['p5'], parent=self.element['e5202'], status='5_STATUS', forced_status=True,  name='e5423')
        TestElement.element['e5533'] = h.test_required(project=self.project['p5'], parent=self.element['e5322'], status='5_STATUS', forced_status=True,  name='e5533')
        
        TestElement.element['e1104'].tag={'t1':'e1104t1', 't1':'e1104t1', 't0':'e1104t0', 't4':None}
        TestElement.element['e1202'].tag={'t1':'e1202t1', 't2':'e1202t2', 't0':'e1202t0', 't2':None}
        TestElement.element['e1322'].tag={'t1':'e1322t1', 't3':'e1322t3', 't2':'e1322t2', 't2':None}
        TestElement.element['e1423'].tag={'t1':'e1423t1', 't4':'e1423t4', 't2':'e1423t2', 't3':None}
        TestElement.element['e1533'].tag={'t1':'e1533t1', 't5':'e1533t5', 't3':'e1533t3', 't3':None}
        TestElement.element['e1632'].tag={'t1':'e1632t1', 't6':'e1632t6', 't3':'e1632t3', 't2':None}
        TestElement.element['e1745'].tag={'t1':'e1745t1', 't7':'e1745t7', 't4':'e1745t4', 't5':None}
        TestElement.element['e1843'].tag={'t1':'e1843t1', 't8':'e1843t8', 't4':'e1843t4', 't3':None}
        TestElement.element['e1953'].tag={'t1':'e1953t1', 't9':'e1953t9', 't5':'e1953t5', 't3':None}
        TestElement.element['e2104'].tag={'t2':'e2104t2', 't1':'e2104t1', 't0':'e2104t0', 't4':None}
        TestElement.element['e2202'].tag={'t2':'e2202t2', 't2':'e2202t2', 't0':'e2202t0', 't2':None}
        TestElement.element['e2322'].tag={'t2':'e2322t2', 't3':'e2322t3', 't2':'e2322t2', 't2':None}
        TestElement.element['e2423'].tag={'t2':'e2423t2', 't4':'e2423t4', 't2':'e2423t2', 't3':None}
        TestElement.element['e2533'].tag={'t2':'e2533t2', 't5':'e2533t5', 't3':'e2533t3', 't3':None}
        TestElement.element['e2632'].tag={'t2':'e2632t2', 't6':'e2632t6', 't3':'e2632t3', 't2':None}
        TestElement.element['e2745'].tag={'t2':'e2745t2', 't7':'e2745t7', 't4':'e2745t4', 't5':None}
        TestElement.element['e2843'].tag={'t2':'e2843t2', 't8':'e2843t8', 't4':'e2843t4', 't3':None}
        TestElement.element['e3104'].tag={'t3':'e3104t3', 't1':'e3104t1', 't0':'e3104t0', 't4':None}
        TestElement.element['e3202'].tag={'t3':'e3202t3', 't2':'e3202t2', 't0':'e3202t0', 't2':None}
        TestElement.element['e3322'].tag={'t3':'e3322t3', 't3':'e3322t3', 't2':'e3322t2', 't2':None}
        TestElement.element['e3423'].tag={'t3':'e3423t3', 't4':'e3423t4', 't2':'e3423t2', 't3':None}
        TestElement.element['e3533'].tag={'t3':'e3533t3', 't5':'e3533t5', 't3':'e3533t3', 't3':None}
        TestElement.element['e3632'].tag={'t3':'e3632t3', 't6':'e3632t6', 't3':'e3632t3', 't2':None}
        TestElement.element['e3745'].tag={'t3':'e3745t3', 't7':'e3745t7', 't4':'e3745t4', 't5':None}
        TestElement.element['e4104'].tag={'t4':'e4104t4', 't1':'e4104t1', 't0':'e4104t0', 't4':None}
        TestElement.element['e4202'].tag={'t4':'e4202t4', 't2':'e4202t2', 't0':'e4202t0', 't2':None}
        TestElement.element['e4322'].tag={'t4':'e4322t4', 't3':'e4322t3', 't2':'e4322t2', 't2':None}
        TestElement.element['e4423'].tag={'t4':'e4423t4', 't4':'e4423t4', 't2':'e4423t2', 't3':None}
        TestElement.element['e4533'].tag={'t4':'e4533t4', 't5':'e4533t5', 't3':'e4533t3', 't3':None}
        TestElement.element['e4632'].tag={'t4':'e4632t4', 't6':'e4632t6', 't3':'e4632t3', 't2':None}
        TestElement.element['e5104'].tag={'t5':'e5104t5', 't1':'e5104t1', 't0':'e5104t0', 't4':None}
        TestElement.element['e5202'].tag={'t5':'e5202t5', 't2':'e5202t2', 't0':'e5202t0', 't2':None}
        TestElement.element['e5322'].tag={'t5':'e5322t5', 't3':'e5322t3', 't2':'e5322t2', 't2':None}
        TestElement.element['e5423'].tag={'t5':'e5423t5', 't4':'e5423t4', 't2':'e5423t2', 't3':None}
        TestElement.element['e5533'].tag={'t5':'e5533t5', 't5':'e5533t5', 't3':'e5533t3', 't3':None}
        
        self.session.add_all(TestElement.element.itervalues())
        
        return TestElement.element

class TestQuery(TestElement):
    def test_forced_status(self):
        r = self.session.query(Element).filter_by(forced_status=True).all()
        assert len(r) == 10
        assert self.element['e1423'] in r
        assert self.element['e1533'] in r
        assert self.element['e2423'] in r
        assert self.element['e2533'] in r
        assert self.element['e3423'] in r
        assert self.element['e3533'] in r
        assert self.element['e4423'] in r
        assert self.element['e4533'] in r
        assert self.element['e5423'] in r
        assert self.element['e5533'] in r
    
    def test_name(self):
        r = self.session.query(Element).filter_by(name='e2104').one()
        assert self.element['e2104'] is r
    
    def test_parent(self):
        r = self.session.query(Element).filter_by(parent=self.element['e2202']).all()
        assert len(r) == 2
        assert self.element['e2322'] in r
        assert self.element['e2423'] in r
        
    def test_project(self):
        r = self.session.query(Element).filter_by(project=self.project['p2']).all()
        assert len(r) == 8
        assert self.element['e2104'] in r
        assert self.element['e2202'] in r
        assert self.element['e2322'] in r
        assert self.element['e2423'] in r
        assert self.element['e2533'] in r
        assert self.element['e2632'] in r
        assert self.element['e2745'] in r
        assert self.element['e2843'] in r
    
    def test_status(self):
        r = self.session.query(Element).filter_by(status='2_STATUS').all()
        assert len(r) == 6
        assert self.element['e1202'] in r
        assert self.element['e1322'] in r
        assert self.element['e1632'] in r
        assert self.element['e2202'] in r
        assert self.element['e2322'] in r
        assert self.element['e2632'] in r
    
    def test_tag_true(self):
        r = Element.query_tags(self.session, tags={'t5': True}).all()
        assert len(r) == 13
        assert self.element['e1533'] in r
        assert self.element['e1745'] in r
        assert self.element['e1953'] in r
        assert self.element['e2533'] in r
        assert self.element['e2745'] in r
        assert self.element['e3533'] in r
        assert self.element['e3745'] in r
        assert self.element['e4533'] in r
        assert self.element['e5104'] in r
        assert self.element['e5202'] in r
        assert self.element['e5322'] in r
        assert self.element['e5423'] in r
        assert self.element['e5533'] in r
    
    def test_tag_none(self):
        r = Element.query_tags(self.session, tags={'t5': None}).all()
        assert len(r) == 3
        assert self.element['e1745'] in r
        assert self.element['e2745'] in r
        assert self.element['e3745'] in r
        
    def test_tag_value(self):
        r = Element.query_tags(self.session, tags={'t5': 'e3533t5'}).filter_by(name='e3533').all()
        assert len(r) == 1
        assert self.element['e3533'] in r

class TestStatusCascade(TestElement):
    def test_down(self):
        # Precondition:
        #     e1202 (2) -> e1322 (2) -> e1632 (2)
        # Action:
        #     e1632.status = 1
        # Postcondition:
        #     e1202 (1) -> e1322 (1) -> e1632 (1)
        assert self.element['e1202'].status == '2_STATUS'
        assert self.element['e1322'].status == '2_STATUS'
        assert self.element['e1632'].status == '2_STATUS'
        assert self.element['e1202'].forced_status == False
        assert self.element['e1322'].forced_status == False
        self.element['e1632'].status = '1_STATUS'
        assert self.element['e1202'].status == '1_STATUS'
        assert self.element['e1322'].status == '1_STATUS'
        assert self.element['e1632'].status == '1_STATUS'
        assert self.element['e1202'].forced_status == False
        assert self.element['e1322'].forced_status == False
    
    def test_up(self):
        # Precondition:
        #     e1202 (2) -> e1322 (2) -> { e1632 (2), e1533 (3F) }
        # Action:
        #     e1632.status = 3
        # Postcondition:
        #     e1202 (3) -> e1322 (3) -> { e1632 (3), e1533 (3F) }
        assert self.element['e1202'].status == '2_STATUS'
        assert self.element['e1322'].status == '2_STATUS'
        assert self.element['e1533'].status == '3_STATUS'
        assert self.element['e1632'].status == '2_STATUS'
        assert self.element['e1202'].forced_status == False
        assert self.element['e1322'].forced_status == False
        self.element['e1632'].status = '3_STATUS'
        assert self.element['e1202'].status == '3_STATUS'
        assert self.element['e1322'].status == '3_STATUS'
        assert self.element['e1533'].status == '3_STATUS'
        assert self.element['e1632'].status == '3_STATUS'
        assert self.element['e1202'].forced_status == False
        assert self.element['e1322'].forced_status == False
    
    def test_unchanged(self):
        # Precondition:
        #     e1202 (2) -> e1322 (2) -> { e1632 (2), e1533 (3F) }
        # Action:
        #     e1533.status = 2
        #     e1632.status = 3
        # Postcondition:
        #     e1202 (2) -> e1322 (2) -> { e1632 (3), e1533 (2F) }
        assert self.element['e1202'].status == '2_STATUS'
        assert self.element['e1322'].status == '2_STATUS'
        assert self.element['e1533'].status == '3_STATUS'
        assert self.element['e1632'].status == '2_STATUS'
        assert self.element['e1202'].forced_status == False
        assert self.element['e1322'].forced_status == False
        self.element['e1533'].status = '2_STATUS'
        self.element['e1632'].status = '3_STATUS'
        assert self.element['e1202'].status == '2_STATUS'
        assert self.element['e1322'].status == '2_STATUS'
        assert self.element['e1533'].status == '2_STATUS'
        assert self.element['e1632'].status == '3_STATUS'
        assert self.element['e1202'].forced_status == False
        assert self.element['e1322'].forced_status == False
    
    def test_down_forced(self):
        # Precondition:
        #     e1533 (3F) -> e1953 (3)
        # Action:
        #     e1953.status = 2
        # Postcondition:
        #     e1533 (3F) -> e1953 (2)
        assert self.element['e1533'].status == '3_STATUS'
        assert self.element['e1953'].status == '3_STATUS'
        assert self.element['e1533'].forced_status == True
        self.element['e1953'].status = '2_STATUS'
        assert self.element['e1533'].status == '3_STATUS'
        assert self.element['e1953'].status == '2_STATUS'
        assert self.element['e1533'].forced_status == True
    
    def test_up_forced(self):
        # Precondition:
        #     e1533 (3F) -> e1953 (3)
        # Action:
        #     e1953.status = 4
        # Postcondition:
        #     e1533 (3F) -> e1953 (4)
        assert self.element['e1533'].status == '3_STATUS'
        assert self.element['e1953'].status == '3_STATUS'
        assert self.element['e1533'].forced_status == True
        self.element['e1953'].status = '4_STATUS'
        assert self.element['e1533'].status == '3_STATUS'
        assert self.element['e1953'].status == '4_STATUS'
        assert self.element['e1533'].forced_status == True
    
    def test_children_add(self):
        # Precondition:
        #     e1104 (4), ...e1632 (2)
        # Action:
        #     e1104.parent = e1632
        # Postcondition:
        #     e1632 (4) -> e1104 (4)
        assert self.element['e1104'].status == '4_STATUS'
        assert self.element['e1632'].status == '2_STATUS'
        assert self.element['e1632'].forced_status == False
        self.element['e1104'].parent = self.element['e1632']
        assert self.element['e1104'].status == '4_STATUS'
        assert self.element['e1632'].status == '4_STATUS'
        assert self.element['e1632'].forced_status == False
    
    def test_children_remove(self):
        # Precondition:
        #     e1322 (2) -> { e1632 (2), e1533 (3F) }
        # Action:
        #     e1632.parent = None
        # Postcondition:
        #     e1322 (3) -> e1533 (3F)
        assert self.element['e1322'].status == '2_STATUS'
        assert self.element['e1533'].status == '3_STATUS'
        assert self.element['e1632'].status == '2_STATUS'
        assert self.element['e1322'].forced_status == False
        self.element['e1632'].parent = None
        assert self.element['e1322'].status == '3_STATUS'
        assert self.element['e1533'].status == '3_STATUS'
        assert self.element['e1322'].forced_status == False
    
    def test_children_add_forced(self):
        # Precondition:
        #     e1533 (3F) -> e1953 (3), ...e1632 (2)
        # Action:
        #     e1632.parent = e1533
        # Postcondition:
        #     e1533 (3F) -> { e1953 (3), e1632 (2) }
        assert self.element['e1533'].status == '3_STATUS'
        assert self.element['e1632'].status == '2_STATUS'
        assert self.element['e1953'].status == '3_STATUS'
        assert self.element['e1533'].forced_status == True
        self.element['e1632'].parent = self.element['e1533']
        assert self.element['e1533'].status == '3_STATUS'
        assert self.element['e1632'].status == '2_STATUS'
        assert self.element['e1953'].status == '3_STATUS'
        assert self.element['e1533'].forced_status == True
    
    def test_children_remove_forced(self):
        # Precondition:
        #     e1423 (3F) -> { e1745 (5), e1843 (3) }
        # Action:
        #     e1843.parent = None
        # Postcondition:
        #     e1423 (3F) -> e1745 (5)
        assert self.element['e1423'].status == '3_STATUS'
        assert self.element['e1745'].status == '5_STATUS'
        assert self.element['e1843'].status == '3_STATUS'
        assert self.element['e1423'].forced_status == True
        self.element['e1843'].parent = None
        assert self.element['e1423'].status == '3_STATUS'
        assert self.element['e1745'].status == '5_STATUS'
        assert self.element['e1423'].forced_status == True
    
    def test_children_add_unchanged(self):
        # Precondition:
        #     e1104 (4), e1322 (2) -> { e1632 (2), e1533 (3F) }
        # Action:
        #     e1104.parent = e1322
        # Postcondition:
        #     e1322 (2) -> { e1632 (2), e1533 (3F), e1104 (4) }
        assert self.element['e1104'].status == '4_STATUS'
        assert self.element['e1322'].status == '2_STATUS'
        assert self.element['e1533'].status == '3_STATUS'
        assert self.element['e1632'].status == '2_STATUS'
        assert self.element['e1322'].forced_status == False
        self.element['e1104'].parent = self.element['e1322']
        assert self.element['e1104'].status == '4_STATUS'
        assert self.element['e1322'].status == '2_STATUS'
        assert self.element['e1533'].status == '3_STATUS'
        assert self.element['e1632'].status == '2_STATUS'
        assert self.element['e1322'].forced_status == False
    
    def test_children_remove_unchanged(self):
        # Precondition:
        #     e1202 (2) -> { e1322 (2), e1423 (3F) }
        # Action:
        #     e1423.parent = None
        # Postcondition:
        #     e1423 (3F), e1202 (2) -> e1322 (2)
        assert self.element['e1202'].status == '2_STATUS'
        assert self.element['e1322'].status == '2_STATUS'
        assert self.element['e1423'].status == '3_STATUS'
        assert self.element['e1202'].forced_status == False
        self.element['e1423'].parent = None
        assert self.element['e1202'].status == '2_STATUS'
        assert self.element['e1322'].status == '2_STATUS'
        assert self.element['e1423'].status == '3_STATUS'
        assert self.element['e1202'].forced_status == False

class TestCTE(TestElement):
    def test_ancestor_no_parent(self):
        assert self.element['e2202'].ancestors == []
    
    @raises(UnboundExecutionError)
    def test_disable_bind(self):
        self.session.flush()
        bind = self.session.bind
        try:
            # Disable statement execution
            self.session.bind = None
            multivac.metadata.bind = None
            # Raise an error
            self.session.query(Element).first()
        finally:
            # Reenable statement execution
            self.session.bind = bind
            multivac.metadata.bind = bind
    
    def test_ancestor_in_session(self):
        # Force flush before its disallowed.
        self.session.flush()
        # Save engine
        bind = self.session.bind
        try:
            # Disable statement execution
            self.session.bind = None
            multivac.metadata.bind = None
            # Retrieve and verify the ancestors
            a = self.element['e2533'].ancestors        
            assert a[0] == self.element['e2322']
            assert a[1] == self.element['e2202']
        finally:
            # Reenable statement execution
            self.session.bind = bind
            multivac.metadata.bind = bind
    
    def test_ancestor_without_cte(self):
        if self.session.bind.name == 'postgresql':
            raise SkipTest('This database uses CTEs.')
        
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=multivac.CTENotSupported)
            self.session.flush()
            self.session.expunge_all()
            # After expunging all objects from the session, we can no longer use them
            e = self.session.query(Element).filter_by(name='e2533').one()
            a = list(e.ancestors)
            assert a[0].name == 'e2322'
            assert a[1].name == 'e2202'
    
    def test_ancestor_with_cte(self):
        if self.session.bind.name != 'postgresql':
            raise SkipTest('CTEs are only supported on PostgreSQL.')  
        
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=multivac.CTENotSupported)
            self.session.flush()
            self.session.expunge_all()
            # After expunging all objects from the session, we can no longer use them
            e = self.session.query(Element).filter_by(name='e2533').one()
            a = list(e.ancestors)
            assert a[0].name == 'e2322'
            assert a[1].name == 'e2202'
