from lxml import etree
from StringIO import StringIO
import pkgutil

def basicMarkupFromClass(cls):
    """
    Load the file associated with the specific class, and return the raw element tree without processing any tags
    """
    markup = pkgutil.get_data(cls.__module__, "%s.html" % cls.__name__)
    parser = etree.HTMLParser()
    return etree.parse(StringIO(markup), parser)

def markupFromClass(cls):
    tree = basicMarkupFromClass(cls)
    #If a component's markup has a <smoff:extend> tag that means it extends its parent's markup rather than replacing it
    #TODO: Proper use of namespaces
    extendElements = tree.findall('//extend', namespaces={'smoff': "http://optim.al/smoff"})
    if(len(extendElements) > 1):
        raise Exception("Found multiple <smoff:extend> tags in the same file")
    elif(len(extendElements) == 1):
        extendElement = extendElements[0]
        parentMarkup = markupFromClass(cls.__bases__[0]) #TODO: Allow multiple inheritance
        #Extend markup is inserted into the parent markup at the <smoff:child> tag
        childElement = parentMarkup.find('//child')
        childElement.getparent().replace(childElement, extendElement)
        return parentMarkup
    else:
        return tree

class MarkupFromFile(object):
    """
    Mixin for classes that expect to have an html file with them
    (principally Page and Panel)
    """
    def markupFromFile(self):
        return markupFromClass(self.__class__)
