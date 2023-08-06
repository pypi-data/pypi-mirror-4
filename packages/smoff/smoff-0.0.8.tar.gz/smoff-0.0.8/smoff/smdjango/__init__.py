from smoffview import SmoffView

def smoffView(pagecls):
    return SmoffView.as_view(page_class=pagecls)
