from lxml import etree
from StringIO import StringIO
import pkgutil

class MarkupFromFile(object):
    def markupFromFile(self):
        markup = pkgutil.get_data(self.__class__.__module__, "%s.html" % self.__class__.__name__)
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(markup), parser)
        return tree