#!/usr/bin/env python2

from webmarkupcontainer import WebMarkupContainer
from markupfromfile import MarkupFromFile

class Page(WebMarkupContainer, MarkupFromFile):
    def get(self, request, *args, **kwargs):
        pass
    
    def render(self):
        tree = self.markupFromFile()
        self.renderInto(tree)
        return tree
