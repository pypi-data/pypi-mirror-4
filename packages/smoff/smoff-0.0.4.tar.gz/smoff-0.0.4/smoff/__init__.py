#!/usr/bin/env python2
SMOFF_NAMESPACE = "http://optim.al/smoff"

from component import Component
from label import Label
from page import Page
from smoffview import SmoffView

def smoffView(pagecls):
    return SmoffView.as_view(page_class=pagecls)
