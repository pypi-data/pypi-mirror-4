#!/usr/bin/env python2
from smoff import SMOFF_NAMESPACE
from lxml import etree
from StringIO import StringIO
import pkgutil

class SmoffBuilder(etree.TreeBuilder):
    def __init__(self, children):
        self.children = children

    def start(self, tag, attrib):
        super(SmoffBuilder, self).start(self, tag, attrib)
	print attrib

class Component(object):
    def __init__(self):
        self._children = {}
    def add(self, markupid, child):
        self._children[markupid] = child
    def render(self):
    	markup = pkgutil.get_data(self.__class__.__module__, "%s.html" % self.__class__.__name__)
	parser = etree.HTMLParser()
	tree = etree.parse(StringIO(markup), parser)
	for event, element in etree.iterwalk(tree):
	    if 'smoff:id' in element.attrib:
	        childid = element.attrib['smoff:id']
		self._children.pop(childid).renderInto(element)
	if(self._children):
	    raise Exception()
	return tree
