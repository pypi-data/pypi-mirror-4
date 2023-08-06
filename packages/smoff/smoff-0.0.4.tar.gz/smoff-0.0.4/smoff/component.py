#!/usr/bin/env python2
from smoff import SMOFF_NAMESPACE
from lxml import etree
from StringIO import StringIO
import pkgutil

class Component(object):
    def __init__(self):
        self._children = {}
    def add(self, markupid, child):
        self._children[markupid] = child
    def renderInto(self, parenttag):
        path = []
        for event, element in etree.iterwalk(parenttag, ('start', 'end')):
            if 'smoff:id' in element.attrib and not parenttag == element:
	        if 'start' == event:
		    path.append(element)
		elif 'end' == event:
		    if(path.pop() != element):
		        raise Exception("Expect same element on ascent as on descent")
		    if(not path):
		        childid = element.attrib['smoff:id']
                        self._children.pop(childid).renderInto(element)
	if(self._children):
            raise Exception()
