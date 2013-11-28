import re

try:
    from lxml.etree import parse as parse_xml
except ImportError:
    from xml.etree.cElementTree import parse as parse_xml


__all__ = ["parse_xml", "inner_text", "XmlNode"]



class XmlNode(object):
    def __init__(self, node):
        self._node = node
        
    def map_nodes(self, path, func):
        return map(func, self.findall(path))
    
    def find(self, path):
        return XmlNode(self._node.find(path))
    
    def findall(self, path):
        return map(XmlNode, self._node.findall(path))
    
    def get(self, name):
        return self._node.get(name)
    
    def inner_text(self):
        return inner_text(self._node)
        
    def children(self):
        for child in self._node:
            yield XmlNode(child)
            
    def local_name(self):
        return re.sub(r"\{[^}]*\}", "", self._node.tag)
        
    def attributes(self):
        return self._node.items()


def inner_text(element):
    return (element.text or "") + "".join(map(inner_text, element)) + (element.tail or "")
