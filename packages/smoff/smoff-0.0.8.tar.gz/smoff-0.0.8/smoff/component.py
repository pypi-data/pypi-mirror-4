#!/usr/bin/env python2
from smoff import SMOFF_NAMESPACE
from lxml import etree
from StringIO import StringIO
import pkgutil

class Component(object):
    """
    Base of the smoff class hierarchy
    The key concept is the hierarchy; components are arranged in a tree, corresponding to the tree in markup
    Visibility could plausibly be separated into a separate class if we wanted to keep everything ultra-decoupled
    """
    def __init__(self):
        #_children is private, intended to be accessed only via add(...)
        self._children = {}
        self._attributeModifiers = set()
        #visible is a public property
        self.visible = True
        
    def add(self, markupid, child):
        """
        Add child (a Component) with the given markupId (string).
        Implies that this component's markup contains a child node with smoff:id= this markupid
        into which that component should be rendered
        """
        if(markupid in self._children):
            raise Exception("Already have a child with markup id %s" % markupid)
        self._children[markupid] = child
        child.parent = self

    def addModifier(self, modifier):
        """Add a "modifier" that changes this tag, as opposed to a "child" that appears below it."""
        self._attributeModifiers.add(modifier)
    
    def renderHead(self, tag):
        """Add anything necessary (e.g. CSS) to the head tag of a page this component is found on"""
        for child in self._children.values():
            child.renderHead(tag)
        
    def renderInto(self, tag, context):
        """
        Render this component into the given tag (an lxml.etree.Element or compatible).
        context is a bit of a hack but I can't see a better way to do it
        TODO: replace visibility with attribute modifier
        """
        if not self.visible:
            #Currently we don't check anything or render subelements in the case of an invisible Component.
            #This may be worth reconsidering
            tag.attrib['style'] = 'display:none'
        else:
            #Keep track of how deep into the tree we are
            #We are only responsible for rendering our immediate children
            #We could theoretically achieve better performance by pulling the iteration up so that we only
            #traverse the tree once for a page (rather than each Component traversing its own tree during rendering)
            #but performance has not yet become a concern
            path = []
            for event, element in etree.iterwalk(tag, ('start', 'end')):
                if 'smoff:id' in element.attrib and not tag == element:
                    if 'start' == event:
                        path.append(element)
                    elif 'end' == event:
                        if(path.pop() != element):
                            #I believe this error is impossible, so throwing a non-catchable exception
                            raise Exception("Expect same element on ascent as on descent")
                        if(not path):
                            childid = element.attrib['smoff:id']
                            #Raise an exception if a component was added in markup but not in code
                            #This indicates programming error rather than runtime failure, so should
                            #not be catchable
                            self._children.pop(childid).renderInto(element, context)
            #Raise an exception if a component was added in code but not in markup
            #This indicates programming error rather than runtime failure, so should
            #not be catchable
            if(self._children):
                raise Exception("""Unable to find markup ids for %s. Did you forget to set smoff:id in your markup?
                    Markup was: %s""" % (self._children, etree.tostring(tag)))
        for modifier in self._attributeModifiers:
            modifier(tag)

