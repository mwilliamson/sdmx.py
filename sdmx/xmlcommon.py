try:
    from lxml.etree import parse as parse_xml
except ImportError:
    from xml.etree.cElementTree import parse as parse_xml


__all__ = ["parse_xml", "inner_text"]

    
def inner_text(element):
    return (element.text or "") + "".join(map(inner_text, element)) + (element.tail or "")
