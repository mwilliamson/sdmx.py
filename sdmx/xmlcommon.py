import re
from xml.dom import pulldom

try:
    from lxml.etree import parse as parse_xml
except ImportError:
    from xml.etree.cElementTree import parse as parse_xml


__all__ = ["parse_xml", "inner_text", "XmlNode"]


def parse_xml_lazy(fileobj):
    stream = DomStream(pulldom.parse(fileobj))
    event = None
    while event != pulldom.START_ELEMENT:
        event, node = next(stream)
    return StreamingXmlNode(stream, node)


class DomStream(object):
    def __init__(self, stream):
        self._stream = stream
        self.depth = 0
    
    def __iter__(self):
        return self
    
    def next(self):
        event, node = next(self._stream)
        if event == pulldom.START_ELEMENT:
            self.depth += 1
        elif event == pulldom.END_ELEMENT:
            self.depth -= 1
        return event, node


class StreamingXmlNode(object):
    def __init__(self, stream, node):
        self._stream = stream
        self._node = node
    
    def find(self, path):
        return next(self.findall(path))
    
    def findall(self, path):
        part, = path
        # TODO: what if we skipped elements that we actually care about e.g. observations before a key?
        original_depth = self._stream.depth
        while self._stream.depth >= original_depth:
            event, node = next(self._stream)
            if self._stream.depth == original_depth + 1 and event == pulldom.START_ELEMENT and (node.namespaceURI, node.localName) == part:
                yield StreamingXmlNode(self._stream, node)
    
    def get(self, name):
        return self._node.getAttribute(name)
    
    def inner_text(self):
        text = []
        original_depth = self._stream.depth
        while self._stream.depth >= original_depth:
            event, node = next(self._stream)
            if event == pulldom.CHARACTERS:
                text.append(node.nodeValue)
        return "".join(text)
    
    def qualified_name(self):
        return qualified_name((self._node.namespaceURI, self._node.localName))


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
