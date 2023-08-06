#!/usr/bin/env python2
from component import Component

class Label(Component):
    """
    A plain text value. Suitable for use with <span>, <h[1-6]> etc.
    """
    def __init__(self, value):
        if not isinstance(value, basestring): raise Exception("Label value must be a string")
        self.value = value
    def renderInto(self, tag, context):
        tag.text = self.value
