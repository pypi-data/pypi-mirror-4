#!/usr/bin/env python2
from component import Component

class Label(Component):
    def __init__(self, value):
        if not isinstance(value, basestring): raise Exception("Label value must be a string")
        self.value = value
    #TODO: proper API around this
    def renderInto(self, parenttag, context):
        parenttag.text = self.value
