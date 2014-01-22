import re

try:
    from lxml.etree import parse as parse_xml
except ImportError:
    from xml.etree.cElementTree import parse as parse_xml


__all__ = ["parse_xml", "inner_text", "XmlNode"]


def path(*parts):
    return list(parts)


def qualified_name(element_type):
    return "{%s}%s" % element_type


class XmlNode(object):
    def __init__(self, node):
        if node is None:
            raise ValueError("node is None")
        self._node = node
        
    def map_nodes(self, path, func):
        return map(func, self.findall(path))
    
    def find(self, path):
        child = self._node.find(_path_to_xpath(path))
        if child is None:
            return None
        else:
            return XmlNode(child)
    
    def findall(self, path):
        return map(XmlNode, self._node.findall(_path_to_xpath(path)))
    
    def get(self, name):
        return self._node.get(name)
    
    def inner_text(self):
        return inner_text(self._node)
        
    def children(self):
        for child in self._node:
            yield XmlNode(child)
            
    def local_name(self):
        return re.sub(r"\{[^}]*\}", "", self._node.tag)
    
    def qualified_name(self):
        return self._node.tag
    
    def attributes(self):
        return self._node.items()
    

def _path_to_xpath(path):
    return "/".join(
        qualified_name(part)
        for part in path
    )


def inner_text(element):
    return (element.text or "") + "".join(map(_inner_text_and_tail, element))


def _inner_text_and_tail(element):
    return inner_text(element) + (element.tail or "")
