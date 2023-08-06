from django.views.generic.base import View
from django.http import HttpResponse
from django.core.context_processors import csrf

from lxml import etree

class SmoffView(View):
    page_class = None
    def get(self, *args, **kwargs):
        context = csrf(self.request)
        self.page_class.request = self.request
        ret = HttpResponse(etree.tostring(self.page_class().render(context)))
        #fixme: handle multiple tabs etc.
        if 'post_handler' in context:
            self.request.session['post_handler'] = context['post_handler']
        return ret
    def post(self, *args, **kwargs):
        return self.request.session.pop('post_handler').handlePost(self.request)
