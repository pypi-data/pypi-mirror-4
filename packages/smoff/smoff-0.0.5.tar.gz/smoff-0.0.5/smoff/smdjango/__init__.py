
from smoffview import SmoffView
from djangoform import DjangoForm

def smoffView(pagecls):
    return SmoffView.as_view(page_class=pagecls)
