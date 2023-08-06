#!/usr/bin/env python2

from webmarkupcontainer import WebMarkupContainer
from markupfromfile import MarkupFromFile

class Page(WebMarkupContainer, MarkupFromFile):
    """
    A top-level page. Knows how to render() its component hierarchy into an lxml.etree.Element tree
    """
    def render(self, context):
        tree = self.markupFromFile()
        head = tree.find('//head')
        self.renderHead(head)
        self.renderInto(tree, context)
        return tree
