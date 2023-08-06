from django.views.generic.base import View
from django.http import HttpResponse
from django.core.context_processors import csrf

from lxml import etree

def renderSmoff(request, page_class, *args, **kwargs):
    context = csrf(request)
    page_class.request = request
    ret = HttpResponse(etree.tostring(page_class(*args, **kwargs).render(context), method='html'))
    #FIXME: handle multiple tabs etc.
    if 'post_handler' in context:
        request.session['post_handler'] = context['post_handler']
    return ret

   

class SmoffView(View):
    """
    Adapts a Page as a django class-based view.
    """
    page_class = None
    def get(self, *args, **kwargs):
        #FIXME: we sort-of want to pass *args through to the page as well, but there's some other crap in there
        return renderSmoff(self.request, self.page_class, **kwargs)
    def post(self, *args, **kwargs):
        return self.request.session.pop('post_handler').handlePost(self.request, **kwargs)
