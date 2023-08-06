#!/usr/bin/env python2
from smoff import SMOFF_NAMESPACE
from lxml import etree
from StringIO import StringIO
import pkgutil

class Component(object):
    def __init__(self):
        self._children = {}
        self.visible = True
    def add(self, markupid, child):
        if(markupid in self._children):
            raise Exception("Already have a child with markup id %s" % markupid)
        self._children[markupid] = child
        child.parent = self
    def renderInto(self, tag, context):
        if not self.visible:
            tag.attrib['style'] = 'display:none'
        else:
            path = []
            for event, element in etree.iterwalk(tag, ('start', 'end')):
                if 'smoff:id' in element.attrib and not tag == element:
                    if 'start' == event:
                        path.append(element)
                    elif 'end' == event:
                        if(path.pop() != element):
                            raise Exception("Expect same element on ascent as on descent")
                        if(not path):
                            childid = element.attrib['smoff:id']
                            self._children.pop(childid).renderInto(element, context)
            if(self._children):
                raise Exception("""Unable to find markup ids for %s. Did you forget to set smoff:id in your markup?
                    Markup was: %s""" % (self._children, etree.tostring(tag)))
