from lxml import etree
from StringIO import StringIO
import pkgutil

def basicMarkupFromClass(cls):
    markup = pkgutil.get_data(cls.__module__, "%s.html" % cls.__name__)
    parser = etree.HTMLParser()
    return etree.parse(StringIO(markup), parser)

def markupFromClass(cls):
    tree = basicMarkupFromClass(cls)
    extendElements = tree.findall('//extend', namespaces={'smoff': "http://optim.al/smoff"})
    if(len(extendElements) > 1):
        raise Exception("Found multiple <smoff:extend> tags in the same file")
    elif(len(extendElements) == 1):
        extendElement = extendElements[0]
        parentMarkup = markupFromClass(cls.__bases__[0]) #TODO: Allow multiple inheritance
        childElement = parentMarkup.find('//child')
        childElement.getparent().replace(childElement, extendElement)
        return parentMarkup
    else:
        return tree


class MarkupFromFile(object):
    def markupFromFile(self):
        return markupFromClass(self.__class__)
