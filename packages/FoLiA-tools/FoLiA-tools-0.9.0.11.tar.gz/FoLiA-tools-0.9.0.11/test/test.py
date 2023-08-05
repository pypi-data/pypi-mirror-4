#!/usr/bin/env python
#-*- coding:utf-8 -*-


from pynlpl.formats.folia import *
import lxml.etree
d = Document(file='example.xml',debug=2)

relaxng('test.rng')
validate('example.xml')
