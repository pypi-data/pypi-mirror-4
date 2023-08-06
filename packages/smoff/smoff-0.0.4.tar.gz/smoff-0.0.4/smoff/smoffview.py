from django.views.generic.base import View
from django.http import HttpResponse
from lxml import etree

class SmoffView(View):
    page_class = None
    def get(self, *args, **kwargs):
        return HttpResponse(etree.tostring(self.page_class().render()))
    def post(self, *args, **kwargs):
        #TODO
        pass 
