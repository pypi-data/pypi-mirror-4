from lxml import html
from smoff import Component

class DjangoForm(Component):
    def __init__(self, dform):
        super(DjangoForm, self).__init__()
        self.dform = dform
    def renderInto(self, tag, context):
        super(DjangoForm, self).renderInto(tag, context)
        tag.append(html.fragment_fromstring(self.dform.as_p()))
