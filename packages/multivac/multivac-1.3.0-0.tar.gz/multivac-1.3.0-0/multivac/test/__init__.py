#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import json
import common

import model

def setup():
    model.init(common.session_maker, extra_mapping = {
        'element'     : common.CustomElement,
        'project'     : common.CustomProject,
        'tag_element' : common.CustomTagElement,
        'tag_project' : common.CustomTagProject,
    })
    
    model.metadata.drop_all()
    model.metadata.create_all()

def teardown():
    #model.metadata.drop_all()
    pass
