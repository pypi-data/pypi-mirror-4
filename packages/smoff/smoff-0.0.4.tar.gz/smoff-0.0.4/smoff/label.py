#!/usr/bin/env python2
from component import Component

class Label(Component):
    def __init__(self, value):
        self.value = value
    #TODO: proper API around this
    def renderInto(self, parenttag):
        parenttag.text = self.value
