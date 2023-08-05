#!/usr/bin/env python
#-*- coding:utf-8 -*-


from pynlpl.formats.folia import *
import lxml.etree
d = Document(file='/tmp/D3.xml',debug=2)

d.save('/tmp/tst2.xml')
